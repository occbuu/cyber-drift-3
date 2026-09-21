from __future__ import annotations
import math
import geoopt
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from .features import FeaturePipeline

# Backbone profiles.  Flow features are skewed enough that the input encoder,
# not the network width, is what decides whether a small MLP can match a tree
# ensemble on closed-set accuracy -- and per Vaze et al. (ICLR 2022) closed-set
# accuracy is in turn the strongest predictor of open-set performance.
PROFILES: dict[str, dict] = {
    # rank-gauss only; keeps the original ~6k-parameter budget
    "lite": {"quantile": True, "piecewise_bins": 0, "hidden_dims": (64,), "latent_dim": 16},
    # rank-gauss plus an 8-bin piecewise-linear expansion
    "balanced": {"quantile": True, "piecewise_bins": 8, "hidden_dims": (64,), "latent_dim": 16},
    # widest profile, strongest low-false-alarm behaviour
    "max": {"quantile": True, "piecewise_bins": 16, "hidden_dims": (128,), "latent_dim": 32},
}
DEFAULT_PROFILE = "balanced"

class TabularBackbone(nn.Module):
    def __init__(self, input_dim: int, num_classes: int, hidden_dim: int = 64, feature_dim: int = 32):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, feature_dim)
        )
        self.classifier = nn.Linear(feature_dim, num_classes)
    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        features = self.encoder(x)
        return self.classifier(features), features

class HyperbolicEvidentialModel(nn.Module):
    def __init__(
        self,
        input_dim: int,
        num_classes: int,
        hidden_dim: int = 64,
        latent_dim: int = 16,
        curvature: float = 0.5,
        features: FeaturePipeline | None = None,
        hidden_dims: tuple[int, ...] | None = None,
    ):
        super().__init__()
        self.num_classes = num_classes
        # curvature = 0 is the flat limit of the Poincare ball, and selects a plain
        # Euclidean prototype head.  It exists so the manifold can be ablated while
        # every other part of the model -- encoder, loss, evidential head, scorer --
        # stays bit-for-bit identical, which is the only way to attribute a result
        # to the geometry rather than to some incidental difference.
        self.euclidean = curvature <= 0.0
        self.manifold = geoopt.PoincareBall(c=max(curvature, 1e-6))
        self.features = features
        widths = tuple(hidden_dims) if hidden_dims else (hidden_dim,)
        encoded_dim = features.output_dim(input_dim) if features is not None else input_dim

        # Micro-MLP: the parameter budget stays small; the input encoder does the
        # heavy lifting of making skewed flow features tractable.
        layers: list[nn.Module] = []
        previous = encoded_dim
        for width in widths:
            layers += [nn.Linear(previous, width), nn.BatchNorm1d(width), nn.ReLU()]
            previous = width
        layers += [nn.Linear(previous, latent_dim)]
        self.encoder = nn.Sequential(*layers)
        if self.euclidean:
            self.prototypes = nn.Parameter(torch.randn(num_classes, latent_dim) * 0.01)
        else:
            self.prototypes = geoopt.ManifoldParameter(
                self.manifold.random_normal((num_classes, latent_dim), std=0.01)
            )
        self.log_evidence_scale = nn.Parameter(torch.tensor(5.0))
        self.raw_gamma = nn.Parameter(torch.tensor(0.0))
        self.raw_temperature = nn.Parameter(torch.tensor(-1.0))

    @classmethod
    def build(
        cls,
        train_x: np.ndarray,
        num_classes: int,
        profile: str = DEFAULT_PROFILE,
        curvature: float = 0.5,
    ) -> "HyperbolicEvidentialModel":
        """Fit the input encoders on the training split and size the backbone.

        ``curvature=0`` builds the Euclidean ablation of the same architecture."""
        if profile not in PROFILES:
            raise ValueError(f"Unknown backbone profile {profile!r}; choose from {sorted(PROFILES)}")
        config = PROFILES[profile]
        features = FeaturePipeline.fit(
            train_x, quantile=config["quantile"], piecewise_bins=config["piecewise_bins"]
        )
        return cls(
            input_dim=train_x.shape[1],
            num_classes=num_classes,
            latent_dim=config["latent_dim"],
            curvature=curvature,
            features=features,
            hidden_dims=config["hidden_dims"],
        )

    def state_floats(self) -> int:
        """Non-trainable fitted state that ships with the model."""
        return self.features.state_floats() if self.features is not None else 0

    def forward(self, x: torch.Tensor) -> dict[str, torch.Tensor]:
        if self.features is not None:
            x = self.features(x)
        tangent = torch.clamp(self.encoder(x), -5.0, 5.0)
        if self.euclidean:
            embedding = tangent
            distances = torch.cdist(tangent, self.prototypes)
        else:
            embedding = self.manifold.expmap0(tangent)
            distances = self.manifold.dist(embedding[:, None, :], self.prototypes[None, :, :])
        gamma = F.softplus(self.raw_gamma) + 1e-4
        log_evidence = torch.clamp(self.log_evidence_scale - gamma * distances, -10.0, 10.0)
        evidence = torch.exp(log_evidence)
        alpha = evidence + 1.0
        strength = alpha.sum(dim=1, keepdim=True)
        probabilities = alpha / strength
        vacuity = self.num_classes / strength
        temperature = F.softplus(self.raw_temperature) + 0.05
        prototype_logits = -distances / temperature
        return {
            "alpha": alpha, "logits": prototype_logits, "probabilities": probabilities,
            "vacuity": vacuity.squeeze(1), "prototype_logits": prototype_logits,
            "distances": distances, "embedding": embedding, "tangent": tangent,
        }

    @torch.no_grad()
    def predict_fast(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """Deployment path: the tangent features the scorer needs, and the predicted class.

        ``forward`` goes through geoopt's generic manifold ops, which build a
        [batch, classes, dim] tensor and launch dozens of small kernels -- at the
        pipeline's batch size that launch overhead, not arithmetic, is what
        dominated inference time.  Here the expmap0 and the Mobius addition inside
        the Poincare distance are written in closed form from one [batch, classes]
        inner-product matrix.  The predicted class is the prototype with the
        smallest ||(-x) (+) p||, which is monotone in the Poincare distance, so the
        arg-min agrees with ``forward`` without evaluating artanh or the
        evidential head.
        """
        if self.features is not None:
            x = self.features(x)
        tangent = torch.clamp(self.encoder(x), -5.0, 5.0)
        if self.euclidean:
            return tangent, torch.cdist(tangent, self.prototypes).argmin(dim=1)
        c = self.manifold.c.to(tangent.dtype)
        sqrt_c = c.sqrt()
        norm = tangent.norm(dim=1, keepdim=True).clamp_min(1e-15)
        embedding = torch.tanh(sqrt_c * norm) * tangent / (sqrt_c * norm)
        # keep points strictly inside the ball, as geoopt's projection does
        max_norm = (1.0 - 4e-3) / sqrt_c
        embedding_norm = embedding.norm(dim=1, keepdim=True).clamp_min(1e-15)
        embedding = torch.where(embedding_norm > max_norm, embedding / embedding_norm * max_norm, embedding)

        prototypes = self.prototypes
        inner = -(embedding @ prototypes.T)                     # <-x, p>
        x2 = embedding.pow(2).sum(dim=1, keepdim=True)          # ||x||^2
        y2 = prototypes.pow(2).sum(dim=1)[None, :]              # ||p||^2
        left = 1.0 + 2.0 * c * inner + c * y2                   # coefficient of -x
        right = 1.0 - c * x2                                    # coefficient of p
        numerator = left.pow(2) * x2 + 2.0 * left * right * inner + right.pow(2) * y2
        denominator = (1.0 + 2.0 * c * inner + c.pow(2) * x2 * y2).pow(2).clamp_min(1e-15)
        predictions = (numerator / denominator).argmin(dim=1)
        return tangent, predictions

def dirichlet_kl(alpha: torch.Tensor, labels: torch.Tensor | None = None) -> torch.Tensor:
    if labels is not None:
        one_hot = F.one_hot(labels, num_classes=alpha.shape[1]).float()
        alpha_tilde = one_hot + (1.0 - one_hot) * alpha
        alpha = alpha_tilde
    beta = torch.ones_like(alpha)
    sum_alpha = alpha.sum(dim=1, keepdim=True)
    sum_beta = beta.sum(dim=1, keepdim=True)
    log_normalizer = torch.lgamma(sum_alpha) - torch.lgamma(alpha).sum(dim=1, keepdim=True)
    log_uniform = torch.lgamma(beta).sum(dim=1, keepdim=True) - torch.lgamma(sum_beta)
    return (((alpha - beta) * (torch.digamma(alpha) - torch.digamma(sum_alpha))).sum(dim=1, keepdim=True) + log_normalizer + log_uniform).mean()

def hedl_loss(outputs: dict[str, torch.Tensor], labels: torch.Tensor, epoch: int, annealing_epochs: int = 10, evidential_weight: float = 1.0, prototype_weight: float = 1.0, kl_weight: float = 0.01, class_weights: torch.Tensor | None = None, margin_weight: float = 1.0) -> torch.Tensor:
    alpha = outputs["alpha"]
    one_hot = F.one_hot(labels, num_classes=alpha.shape[1]).float()
    strength = alpha.sum(dim=1, keepdim=True)
    mean = alpha / strength
    error = (one_hot - mean).pow(2)
    variance = alpha * (strength - alpha) / (strength.pow(2) * (strength + 1.0))
    evidential_per_sample = (error + variance).sum(dim=1)
    if class_weights is None:
        evidential = evidential_per_sample.mean()
    else:
        sample_weights = class_weights[labels]
        evidential = (evidential_per_sample * sample_weights).sum() / sample_weights.sum()
    
    annealing = min(1.0, epoch / max(1, annealing_epochs))
    prototype = F.cross_entropy(outputs["prototype_logits"], labels, weight=class_weights)
    distances = outputs["distances"]
    target_distances = distances[torch.arange(len(labels)), labels]
    non_target_mask = torch.ones_like(distances, dtype=torch.bool)
    non_target_mask[torch.arange(len(labels)), labels] = False
    nearest_non_target = distances.masked_fill(~non_target_mask, float("inf")).min(dim=1).values
    margin_loss = F.relu(target_distances - nearest_non_target + 1.0).mean()
    return evidential_weight * evidential + prototype_weight * prototype + annealing * kl_weight * dirichlet_kl(alpha, labels) + margin_weight * margin_loss