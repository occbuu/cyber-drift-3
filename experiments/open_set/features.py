"""Input feature encoders for the H-EDL backbone.

Network-flow features are extremely skewed and heavy-tailed: packet counts,
byte counts and durations span several orders of magnitude and carry large point
masses at zero.  A plain affine rescaling leaves an MLP fighting that geometry,
which is the usual reason tree ensembles beat neural networks on tabular
intrusion data.

Two encoders address it, both fitted on the training split only and stored as
buffers so that their cost is counted in measured inference latency:

``QuantileNormalizer``      rank-gauss transform -- map each feature through its
                            own empirical CDF and then through the inverse normal
                            CDF, so every feature arrives at the encoder roughly
                            standard normal and outliers stop dominating.
``PiecewiseLinearEncoding`` Gorishniy, Rubachev and Babenko, "On embeddings for
                            numerical features in tabular deep learning",
                            NeurIPS 2022: replace each scalar by the vector of
                            its positions inside quantile bins, which lets a
                            small MLP express bin-local decision boundaries the
                            way a tree does.

Neither encoder has trainable parameters.
"""

from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn


class QuantileNormalizer(nn.Module):
    """Rank-gauss transform with a fitted per-feature quantile grid."""

    def __init__(self, knots: np.ndarray, epsilon: float = 1e-7):
        super().__init__()
        self.epsilon = epsilon
        self.register_buffer("knots", torch.from_numpy(np.ascontiguousarray(knots)).float())
        self.register_buffer("references", torch.linspace(0.0, 1.0, knots.shape[1]))

    @classmethod
    def fit(cls, x: np.ndarray, quantiles: int = 512) -> "QuantileNormalizer":
        levels = np.linspace(0.0, 1.0, quantiles)
        knots = np.quantile(x.astype(np.float64), levels, axis=0).T
        knots = np.maximum.accumulate(knots, axis=1)
        return cls(knots)

    @property
    def output_dim_factor(self) -> int:
        return 1

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        values = x.transpose(0, 1).contiguous()
        last = self.knots.shape[1] - 1
        # First knot at or above the value, and last knot at or below it.  A run
        # of equal knots is routine here because flow features carry large point
        # masses at zero; the two indices bracket that run and its midpoint rank
        # is used, which reproduces scikit-learn's symmetric interpolation rather
        # than collapsing the whole tie onto its lower edge.
        above = torch.searchsorted(self.knots, values, right=False).clamp(0, last)
        below = (torch.searchsorted(self.knots, values, right=True) - 1).clamp(0, last)
        reference_above = self.references[above]
        reference_below = self.references[below]
        knot_above = torch.gather(self.knots, 1, above)
        knot_below = torch.gather(self.knots, 1, below)
        weight = ((values - knot_below) / torch.clamp(knot_above - knot_below, min=1e-12)).clamp(0.0, 1.0)
        interpolated = reference_below + weight * (reference_above - reference_below)
        tied = 0.5 * (reference_above + reference_below)
        rank = torch.where(below >= above, tied, interpolated)
        # scikit-learn pins a value sitting exactly on the fitted minimum to rank 0
        # and one on the maximum to rank 1, rather than to the midpoint of the tie
        # run.  For flow features that is the difference between "zero is the most
        # extreme value this feature takes" and "zero is unremarkable", so the
        # behaviour is reproduced rather than approximated.
        rank = torch.where(values <= self.knots[:, :1], torch.zeros_like(rank), rank)
        rank = torch.where(values >= self.knots[:, last:], torch.ones_like(rank), rank)
        rank = rank.clamp(self.epsilon, 1.0 - self.epsilon)
        return torch.special.ndtri(rank).transpose(0, 1)


class PiecewiseLinearEncoding(nn.Module):
    """Expand every scalar into its piecewise-linear position across quantile bins."""

    def __init__(self, edges: np.ndarray):
        super().__init__()
        self.bins = edges.shape[1] - 1
        self.register_buffer("edges", torch.from_numpy(np.ascontiguousarray(edges)).float())

    @classmethod
    def fit(cls, x: np.ndarray, bins: int = 8) -> "PiecewiseLinearEncoding":
        levels = np.linspace(0.0, 1.0, bins + 1)
        rows = []
        for column in range(x.shape[1]):
            edge = np.unique(np.quantile(x[:, column].astype(np.float64), levels))
            if len(edge) < bins + 1:
                edge = np.linspace(float(edge[0]), float(edge[-1]) + 1e-6, bins + 1)
            rows.append(edge)
        return cls(np.stack(rows))

    @property
    def output_dim_factor(self) -> int:
        return self.bins

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        left = self.edges[None, :, :-1]
        right = self.edges[None, :, 1:]
        ratio = (x[:, :, None] - left) / torch.clamp(right - left, min=1e-6)
        return ratio.clamp(0.0, 1.0).flatten(1)


class FeaturePipeline(nn.Module):
    """Optional rank-gauss step followed by an optional piecewise-linear expansion."""

    def __init__(self, normalizer: QuantileNormalizer | None, encoding: PiecewiseLinearEncoding | None):
        super().__init__()
        self.normalizer = normalizer
        self.encoding = encoding

    @classmethod
    def fit(
        cls,
        x: np.ndarray,
        quantile: bool = True,
        piecewise_bins: int = 0,
        quantiles: int = 512,
    ) -> "FeaturePipeline":
        normalizer = QuantileNormalizer.fit(x, quantiles) if quantile else None
        if piecewise_bins:
            basis = x
            if normalizer is not None:
                with torch.no_grad():
                    basis = normalizer(torch.from_numpy(x).float()).numpy()
            encoding = PiecewiseLinearEncoding.fit(basis, piecewise_bins)
        else:
            encoding = None
        return cls(normalizer, encoding)

    def output_dim(self, input_dim: int) -> int:
        return input_dim * (self.encoding.output_dim_factor if self.encoding is not None else 1)

    def state_floats(self) -> int:
        """Fitted state that is not trainable but still has to ship with the model."""
        total = 0
        if self.normalizer is not None:
            total += int(self.normalizer.knots.numel())
        if self.encoding is not None:
            total += int(self.encoding.edges.numel())
        return total

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if self.normalizer is not None:
            x = self.normalizer(x)
        if self.encoding is not None:
            x = self.encoding(x)
        return x
