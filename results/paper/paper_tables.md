# PACT — paper tables (generated; do not edit by hand)

Regenerate with `python -m experiments.open_set.paper_tables`.

## RQ1 / RQ2 — alert quality per calibration draw (n = 12,000, window 2,000)

Each seed is an independent calibration split with its own trained model; within a seed, five subsamples of 12,000 are drawn from it. `draws>q` counts (seed, subsample) pairs whose stream FDR exceeded q, `seeds>q` counts seeds whose own mean did. FDR and power are mean ± 95% CI over the five seeds. The certificate column applies PACT's exchangeability audit: a refused dataset supports no FDR claim from any procedure.

| dataset | q | π | procedure | FDR | draws>q | seeds>q | power | certificate |
|---|---|---|---|---|---|---|---|---|
| cse2018 | 0.1 | 0.01 | marginal BH | 0.096 ± 0.030 | 36% | 40% | 0.970 ± 0.040 | certified |
| cse2018 | 0.1 | 0.01 | PACT conditional L=1 | 0.067 ± 0.023 | 8% | 0% | 0.898 ± 0.167 | certified |
| cse2018 | 0.1 | 0.01 | PACT conditional L=5 | 0.051 ± 0.015 | 0% | 0% | 0.774 ± 0.307 | certified |
| cse2018 | 0.1 | 0.01 | PACT conditional L=100 (shipped) | 0.036 ± 0.015 | 0% | 0% | 0.430 ± 0.288 | certified |
| cse2018 | 0.1 | 0.01 | Storey-BH | 0.097 ± 0.030 | 36% | 40% | 0.971 ± 0.038 | certified |
| cse2018 | 0.1 | 0.01 | BY | 0.008 ± 0.010 | 0% | 0% | 0.109 ± 0.137 | certified |
| cse2018 | 0.1 | 0.01 | e-BH | 0.027 ± 0.043 | 8% | 0% | 0.287 ± 0.303 | certified |
| cse2018 | 0.1 | 0.001 | marginal BH | 0.198 ± 0.053 | 96% | 100% | 0.286 ± 0.225 | certified |
| cse2018 | 0.1 | 0.001 | PACT conditional L=1 | 0.056 ± 0.066 | 20% | 20% | 0.046 ± 0.059 | certified |
| cse2018 | 0.1 | 0.001 | PACT conditional L=5 | 0.001 ± 0.003 | 0% | 0% | 0.001 ± 0.002 | certified |
| cse2018 | 0.1 | 0.001 | PACT conditional L=100 (shipped) | 0.000 ± 0.000 | 0% | 0% | 0.000 ± 0.000 | certified |
| cse2018 | 0.1 | 0.001 | Storey-BH | 0.198 ± 0.053 | 96% | 100% | 0.286 ± 0.225 | certified |
| cse2018 | 0.1 | 0.001 | BY | 0.000 ± 0.000 | 0% | 0% | 0.000 ± 0.000 | certified |
| cse2018 | 0.1 | 0.001 | e-BH | 0.120 ± 0.099 | 56% | 60% | 0.193 ± 0.215 | certified |
| cse2018 | 0.2 | 0.01 | marginal BH | 0.187 ± 0.021 | 20% | 40% | 0.996 ± 0.011 | certified |
| cse2018 | 0.2 | 0.01 | PACT conditional L=1 | 0.148 ± 0.022 | 4% | 0% | 0.992 ± 0.014 | certified |
| cse2018 | 0.2 | 0.01 | PACT conditional L=5 | 0.123 ± 0.026 | 0% | 0% | 0.981 ± 0.025 | certified |
| cse2018 | 0.2 | 0.01 | PACT conditional L=100 (shipped) | 0.094 ± 0.028 | 0% | 0% | 0.934 ± 0.107 | certified |
| cse2018 | 0.2 | 0.01 | Storey-BH | 0.189 ± 0.022 | 32% | 40% | 0.996 ± 0.011 | certified |
| cse2018 | 0.2 | 0.01 | BY | 0.025 ± 0.013 | 0% | 0% | 0.437 ± 0.338 | certified |
| cse2018 | 0.2 | 0.01 | e-BH | 0.123 ± 0.308 | 12% | 20% | 0.288 ± 0.303 | certified |
| cse2018 | 0.2 | 0.001 | marginal BH | 0.331 ± 0.069 | 100% | 100% | 0.654 ± 0.255 | certified |
| cse2018 | 0.2 | 0.001 | PACT conditional L=1 | 0.224 ± 0.061 | 56% | 80% | 0.298 ± 0.225 | certified |
| cse2018 | 0.2 | 0.001 | PACT conditional L=5 | 0.097 ± 0.094 | 16% | 20% | 0.073 ± 0.074 | certified |
| cse2018 | 0.2 | 0.001 | PACT conditional L=100 (shipped) | 0.008 ± 0.010 | 0% | 0% | 0.005 ± 0.007 | certified |
| cse2018 | 0.2 | 0.001 | Storey-BH | 0.332 ± 0.069 | 100% | 100% | 0.655 ± 0.255 | certified |
| cse2018 | 0.2 | 0.001 | BY | 0.001 ± 0.003 | 0% | 0% | 0.001 ± 0.002 | certified |
| cse2018 | 0.2 | 0.001 | e-BH | 0.228 ± 0.357 | 44% | 20% | 0.287 ± 0.298 | certified |
| cicids2017 | 0.1 | 0.01 | marginal BH | 0.100 ± 0.047 | 60% | 60% | 0.377 ± 0.420 | certified |
| cicids2017 | 0.1 | 0.01 | PACT conditional L=1 | 0.072 ± 0.060 | 36% | 40% | 0.176 ± 0.288 | certified |
| cicids2017 | 0.1 | 0.01 | PACT conditional L=5 | 0.037 ± 0.060 | 12% | 0% | 0.054 ± 0.111 | certified |
| cicids2017 | 0.1 | 0.01 | PACT conditional L=100 (shipped) | 0.004 ± 0.010 | 0% | 0% | 0.003 ± 0.008 | certified |
| cicids2017 | 0.1 | 0.01 | Storey-BH | 0.100 ± 0.047 | 60% | 60% | 0.378 ± 0.420 | certified |
| cicids2017 | 0.1 | 0.01 | BY | 0.000 ± 0.000 | 0% | 0% | 0.000 ± 0.000 | certified |
| cicids2017 | 0.1 | 0.01 | e-BH | 0.054 ± 0.093 | 40% | 40% | 0.011 ± 0.018 | certified |
| cicids2017 | 0.1 | 0.001 | marginal BH | 0.189 ± 0.183 | 72% | 80% | 0.019 ± 0.024 | certified |
| cicids2017 | 0.1 | 0.001 | PACT conditional L=1 | 0.000 ± 0.000 | 0% | 0% | 0.000 ± 0.000 | certified |
| cicids2017 | 0.1 | 0.001 | PACT conditional L=5 | 0.000 ± 0.000 | 0% | 0% | 0.000 ± 0.000 | certified |
| cicids2017 | 0.1 | 0.001 | PACT conditional L=100 (shipped) | 0.000 ± 0.000 | 0% | 0% | 0.000 ± 0.000 | certified |
| cicids2017 | 0.1 | 0.001 | Storey-BH | 0.189 ± 0.183 | 72% | 80% | 0.019 ± 0.024 | certified |
| cicids2017 | 0.1 | 0.001 | BY | 0.000 ± 0.000 | 0% | 0% | 0.000 ± 0.000 | certified |
| cicids2017 | 0.1 | 0.001 | e-BH | 0.087 ± 0.148 | 40% | 40% | 0.004 ± 0.007 | certified |
| cicids2017 | 0.2 | 0.01 | marginal BH | 0.165 ± 0.030 | 4% | 0% | 0.724 ± 0.264 | certified |
| cicids2017 | 0.2 | 0.01 | PACT conditional L=1 | 0.134 ± 0.027 | 0% | 0% | 0.558 ± 0.380 | certified |
| cicids2017 | 0.2 | 0.01 | PACT conditional L=5 | 0.116 ± 0.036 | 0% | 0% | 0.413 ± 0.429 | certified |
| cicids2017 | 0.2 | 0.01 | PACT conditional L=100 (shipped) | 0.072 ± 0.052 | 0% | 0% | 0.228 ± 0.350 | certified |
| cicids2017 | 0.2 | 0.01 | Storey-BH | 0.166 ± 0.030 | 4% | 0% | 0.726 ± 0.261 | certified |
| cicids2017 | 0.2 | 0.01 | BY | 0.003 ± 0.004 | 0% | 0% | 0.001 ± 0.002 | certified |
| cicids2017 | 0.2 | 0.01 | e-BH | 0.053 ± 0.093 | 0% | 0% | 0.020 ± 0.027 | certified |
| cicids2017 | 0.2 | 0.001 | marginal BH | 0.462 ± 0.284 | 84% | 80% | 0.163 ± 0.174 | certified |
| cicids2017 | 0.2 | 0.001 | PACT conditional L=1 | 0.200 ± 0.183 | 44% | 60% | 0.023 ± 0.029 | certified |
| cicids2017 | 0.2 | 0.001 | PACT conditional L=5 | 0.030 ± 0.058 | 0% | 0% | 0.003 ± 0.005 | certified |
| cicids2017 | 0.2 | 0.001 | PACT conditional L=100 (shipped) | 0.000 ± 0.000 | 0% | 0% | 0.000 ± 0.000 | certified |
| cicids2017 | 0.2 | 0.001 | Storey-BH | 0.464 ± 0.279 | 84% | 80% | 0.163 ± 0.174 | certified |
| cicids2017 | 0.2 | 0.001 | BY | 0.000 ± 0.000 | 0% | 0% | 0.000 ± 0.000 | certified |
| cicids2017 | 0.2 | 0.001 | e-BH | 0.236 ± 0.403 | 40% | 40% | 0.022 ± 0.028 | certified |
| toniot | 0.1 | 0.01 | marginal BH | 0.099 ± 0.066 | 24% | 40% | 0.000 ± 0.000 | certified |
| toniot | 0.1 | 0.01 | PACT conditional L=1 | 0.000 ± 0.000 | 0% | 0% | 0.000 ± 0.000 | certified |
| toniot | 0.1 | 0.01 | PACT conditional L=5 | 0.000 ± 0.000 | 0% | 0% | 0.000 ± 0.000 | certified |
| toniot | 0.1 | 0.01 | PACT conditional L=100 (shipped) | 0.000 ± 0.000 | 0% | 0% | 0.000 ± 0.000 | certified |
| toniot | 0.1 | 0.01 | Storey-BH | 0.099 ± 0.066 | 24% | 40% | 0.000 ± 0.000 | certified |
| toniot | 0.1 | 0.01 | BY | 0.000 ± 0.000 | 0% | 0% | 0.000 ± 0.000 | certified |
| toniot | 0.1 | 0.01 | e-BH | 0.099 ± 0.066 | 24% | 40% | 0.000 ± 0.000 | certified |
| toniot | 0.1 | 0.001 | marginal BH | 0.066 ± 0.061 | 16% | 20% | 0.000 ± 0.000 | certified |
| toniot | 0.1 | 0.001 | PACT conditional L=1 | 0.000 ± 0.000 | 0% | 0% | 0.000 ± 0.000 | certified |
| toniot | 0.1 | 0.001 | PACT conditional L=5 | 0.000 ± 0.000 | 0% | 0% | 0.000 ± 0.000 | certified |
| toniot | 0.1 | 0.001 | PACT conditional L=100 (shipped) | 0.000 ± 0.000 | 0% | 0% | 0.000 ± 0.000 | certified |
| toniot | 0.1 | 0.001 | Storey-BH | 0.066 ± 0.061 | 16% | 20% | 0.000 ± 0.000 | certified |
| toniot | 0.1 | 0.001 | BY | 0.000 ± 0.000 | 0% | 0% | 0.000 ± 0.000 | certified |
| toniot | 0.1 | 0.001 | e-BH | 0.066 ± 0.061 | 16% | 20% | 0.000 ± 0.000 | certified |
| toniot | 0.2 | 0.01 | marginal BH | 0.498 ± 0.226 | 84% | 100% | 0.003 ± 0.002 | certified |
| toniot | 0.2 | 0.01 | PACT conditional L=1 | 0.100 ± 0.063 | 20% | 0% | 0.000 ± 0.000 | certified |
| toniot | 0.2 | 0.01 | PACT conditional L=5 | 0.000 ± 0.000 | 0% | 0% | 0.000 ± 0.000 | certified |
| toniot | 0.2 | 0.01 | PACT conditional L=100 (shipped) | 0.000 ± 0.000 | 0% | 0% | 0.000 ± 0.000 | certified |
| toniot | 0.2 | 0.01 | Storey-BH | 0.500 ± 0.229 | 84% | 100% | 0.003 ± 0.002 | certified |
| toniot | 0.2 | 0.01 | BY | 0.000 ± 0.000 | 0% | 0% | 0.000 ± 0.000 | certified |
| toniot | 0.2 | 0.01 | e-BH | 0.443 ± 0.261 | 68% | 80% | 0.002 ± 0.003 | certified |
| toniot | 0.2 | 0.001 | marginal BH | 0.604 ± 0.295 | 80% | 100% | 0.003 ± 0.003 | certified |
| toniot | 0.2 | 0.001 | PACT conditional L=1 | 0.068 ± 0.059 | 12% | 0% | 0.000 ± 0.000 | certified |
| toniot | 0.2 | 0.001 | PACT conditional L=5 | 0.000 ± 0.000 | 0% | 0% | 0.000 ± 0.000 | certified |
| toniot | 0.2 | 0.001 | PACT conditional L=100 (shipped) | 0.000 ± 0.000 | 0% | 0% | 0.000 ± 0.000 | certified |
| toniot | 0.2 | 0.001 | Storey-BH | 0.604 ± 0.295 | 80% | 100% | 0.003 ± 0.003 | certified |
| toniot | 0.2 | 0.001 | BY | 0.000 ± 0.000 | 0% | 0% | 0.000 ± 0.000 | certified |
| toniot | 0.2 | 0.001 | e-BH | 0.545 ± 0.316 | 68% | 80% | 0.003 ± 0.003 | certified |
| ciciomt2024 | 0.1 | 0.01 | marginal BH | 0.965 ± 0.044 | 100% | 100% | 0.212 ± 0.546 | refuse |
| ciciomt2024 | 0.1 | 0.01 | PACT conditional L=1 | 0.709 ± 0.350 | 88% | 100% | 0.203 ± 0.551 | refuse |
| ciciomt2024 | 0.1 | 0.01 | PACT conditional L=5 | 0.428 ± 0.481 | 56% | 80% | 0.199 ± 0.549 | refuse |
| ciciomt2024 | 0.1 | 0.01 | PACT conditional L=100 (shipped) | 0.207 ± 0.488 | 28% | 20% | 0.179 ± 0.497 | refuse |
| ciciomt2024 | 0.1 | 0.01 | Storey-BH | 0.976 ± 0.041 | 100% | 100% | 0.234 ± 0.532 | refuse |
| ciciomt2024 | 0.1 | 0.01 | BY | 0.000 ± 0.000 | 0% | 0% | 0.000 ± 0.000 | refuse |
| ciciomt2024 | 0.1 | 0.01 | e-BH | 0.628 ± 0.365 | 84% | 100% | 0.001 ± 0.001 | refuse |
| ciciomt2024 | 0.1 | 0.001 | marginal BH | 0.981 ± 0.043 | 100% | 100% | 0.213 ± 0.545 | refuse |
| ciciomt2024 | 0.1 | 0.001 | PACT conditional L=1 | 0.715 ± 0.373 | 88% | 100% | 0.202 ± 0.547 | refuse |
| ciciomt2024 | 0.1 | 0.001 | PACT conditional L=5 | 0.450 ± 0.507 | 56% | 60% | 0.189 ± 0.523 | refuse |
| ciciomt2024 | 0.1 | 0.001 | PACT conditional L=100 (shipped) | 0.232 ± 0.528 | 28% | 20% | 0.127 ± 0.353 | refuse |
| ciciomt2024 | 0.1 | 0.001 | Storey-BH | 0.998 ± 0.005 | 100% | 100% | 0.231 ± 0.534 | refuse |
| ciciomt2024 | 0.1 | 0.001 | BY | 0.000 ± 0.000 | 0% | 0% | 0.000 ± 0.000 | refuse |
| ciciomt2024 | 0.1 | 0.001 | e-BH | 0.637 ± 0.387 | 76% | 100% | 0.000 ± 0.001 | refuse |
| ciciomt2024 | 0.2 | 0.01 | marginal BH | 0.936 ± 0.060 | 100% | 100% | 0.695 ± 0.529 | refuse |
| ciciomt2024 | 0.2 | 0.01 | PACT conditional L=1 | 0.939 ± 0.065 | 100% | 100% | 0.611 ± 0.521 | refuse |
| ciciomt2024 | 0.2 | 0.01 | PACT conditional L=5 | 0.944 ± 0.062 | 100% | 100% | 0.526 ± 0.493 | refuse |
| ciciomt2024 | 0.2 | 0.01 | PACT conditional L=100 (shipped) | 0.955 ± 0.050 | 100% | 100% | 0.385 ± 0.471 | refuse |
| ciciomt2024 | 0.2 | 0.01 | Storey-BH | 0.942 ± 0.043 | 100% | 100% | 0.793 ± 0.531 | refuse |
| ciciomt2024 | 0.2 | 0.01 | BY | 0.006 ± 0.011 | 0% | 0% | 0.000 ± 0.000 | refuse |
| ciciomt2024 | 0.2 | 0.01 | e-BH | 0.939 ± 0.115 | 100% | 100% | 0.001 ± 0.002 | refuse |
| ciciomt2024 | 0.2 | 0.001 | marginal BH | 0.993 ± 0.007 | 100% | 100% | 0.652 ± 0.507 | refuse |
| ciciomt2024 | 0.2 | 0.001 | PACT conditional L=1 | 0.994 ± 0.006 | 100% | 100% | 0.518 ± 0.463 | refuse |
| ciciomt2024 | 0.2 | 0.001 | PACT conditional L=5 | 0.996 ± 0.004 | 100% | 100% | 0.416 ± 0.460 | refuse |
| ciciomt2024 | 0.2 | 0.001 | PACT conditional L=100 (shipped) | 0.997 ± 0.004 | 100% | 100% | 0.305 ± 0.494 | refuse |
| ciciomt2024 | 0.2 | 0.001 | Storey-BH | 0.993 ± 0.006 | 100% | 100% | 0.783 ± 0.524 | refuse |
| ciciomt2024 | 0.2 | 0.001 | BY | 0.000 ± 0.000 | 0% | 0% | 0.000 ± 0.000 | refuse |
| ciciomt2024 | 0.2 | 0.001 | e-BH | 0.962 ± 0.099 | 100% | 100% | 0.001 ± 0.002 | refuse |



### RQ1 gate (b): PACT conditional at the shipped level budget (L = 100), π = 0.01

| dataset | q | FDR | draws>q | power | refused seeds | pass |
|---|---|---|---|---|---|---|
| cse2018 | 0.1 | 0.036 | 0% | 0.430 | 0 | PASS |
| cse2018 | 0.2 | 0.094 | 0% | 0.934 | 0 | PASS |
| cicids2017 | 0.1 | 0.004 | 0% | 0.003 | 0 | fail |
| cicids2017 | 0.2 | 0.072 | 0% | 0.228 | 0 | PASS |
| toniot | 0.1 | 0.000 | 0% | 0.000 | 0 | fail |
| toniot | 0.2 | 0.000 | 0% | 0.000 | 0 | fail |
| ciciomt2024 | 0.1 | 0.207 | 28% | 0.179 | 5 | fail |
| ciciomt2024 | 0.2 | 0.955 | 100% | 0.385 | 5 | fail |



### RQ2: marginal vs training-conditional, and what the level correction costs

| dataset | q | π | marginal draws>q | conditional L=1 | conditional L=100 | marginal power | shipped power | power price | refused | gate |
|---|---|---|---|---|---|---|---|---|---|---|
| cse2018 | 0.1 | 0.01 | 36% | 8% | 0% | 0.970 | 0.430 | 55.6% | 0 | MET |
| cse2018 | 0.1 | 0.001 | 96% | 20% | 0% | 0.286 | 0.000 | 100.0% | 0 |  |
| cse2018 | 0.2 | 0.01 | 20% | 4% | 0% | 0.996 | 0.934 | 6.2% | 0 | MET |
| cse2018 | 0.2 | 0.001 | 100% | 56% | 0% | 0.654 | 0.005 | 99.2% | 0 |  |
| cicids2017 | 0.1 | 0.01 | 60% | 36% | 0% | 0.377 | 0.003 | 99.2% | 0 |  |
| cicids2017 | 0.1 | 0.001 | 72% | 0% | 0% | 0.019 | 0.000 | 100.0% | 0 |  |
| cicids2017 | 0.2 | 0.01 | 4% | 0% | 0% | 0.724 | 0.228 | 68.5% | 0 |  |
| cicids2017 | 0.2 | 0.001 | 84% | 44% | 0% | 0.163 | 0.000 | 100.0% | 0 |  |
| toniot | 0.1 | 0.01 | 24% | 0% | 0% | 0.000 | 0.000 | 100.0% | 0 |  |
| toniot | 0.1 | 0.001 | 16% | 0% | 0% | 0.000 | 0.000 | 100.0% | 0 |  |
| toniot | 0.2 | 0.01 | 84% | 20% | 0% | 0.003 | 0.000 | 100.0% | 0 |  |
| toniot | 0.2 | 0.001 | 80% | 12% | 0% | 0.003 | 0.000 | 100.0% | 0 |  |
| ciciomt2024 | 0.1 | 0.01 | 100% | 88% | 28% | 0.212 | 0.179 | 15.3% | 5 |  |
| ciciomt2024 | 0.1 | 0.001 | 100% | 88% | 28% | 0.213 | 0.127 | 40.2% | 5 |  |
| ciciomt2024 | 0.2 | 0.01 | 100% | 100% | 100% | 0.695 | 0.385 | 44.5% | 5 |  |
| ciciomt2024 | 0.2 | 0.001 | 100% | 100% | 100% | 0.652 | 0.305 | 53.2% | 5 |  |

## RQ1 — stream-level alert quality at the full calibration set (window 2,000)

**Secondary.** At its largest size this sweep reads the whole calibration sample, so its five draws share one calibration set and differ only in the stream: `draws>q` here is stream-to-stream variation, not calibration variation. The per-draw claim is the n = 12,000 table above. Mean ± 95% CI over seeds.

| dataset | q | π | procedure | FDR | draws>q | power | certificate |
|---|---|---|---|---|---|---|---|
| cse2018 | 0.1 | 0.01 | Bates BH | 0.094 ± 0.018 | 36% | 0.977 ± 0.031 | certified |
| cse2018 | 0.1 | 0.01 | PACT conditional | 0.069 ± 0.014 | 0% | 0.947 ± 0.065 | certified |
| cse2018 | 0.1 | 0.01 | Storey-BH | 0.096 ± 0.018 | 40% | 0.978 ± 0.031 | certified |
| cse2018 | 0.1 | 0.01 | BY | 0.005 ± 0.006 | 0% | 0.050 ± 0.063 | certified |
| cse2018 | 0.1 | 0.01 | e-BH | 0.189 ± 0.507 | 20% | 0.072 ± 0.131 | certified |
| cse2018 | 0.1 | 0.001 | Bates BH | 0.265 ± 0.251 | 96% | 0.295 ± 0.173 | certified |
| cse2018 | 0.1 | 0.001 | PACT conditional | 0.078 ± 0.076 | 36% | 0.048 ± 0.044 | certified |
| cse2018 | 0.1 | 0.001 | Storey-BH | 0.266 ± 0.237 | 100% | 0.301 ± 0.171 | certified |
| cse2018 | 0.1 | 0.001 | BY | 0.000 ± 0.000 | 0% | 0.000 ± 0.000 | certified |
| cse2018 | 0.1 | 0.001 | e-BH | 0.233 ± 0.505 | 40% | 0.073 ± 0.132 | certified |
| cse2018 | 0.2 | 0.01 | Bates BH | 0.185 ± 0.017 | 8% | 0.996 ± 0.011 | certified |
| cse2018 | 0.2 | 0.01 | PACT conditional | 0.157 ± 0.017 | 0% | 0.994 ± 0.015 | certified |
| cse2018 | 0.2 | 0.01 | Storey-BH | 0.188 ± 0.017 | 28% | 0.996 ± 0.011 | certified |
| cse2018 | 0.2 | 0.01 | BY | 0.024 ± 0.006 | 0% | 0.505 ± 0.386 | certified |
| cse2018 | 0.2 | 0.01 | e-BH | 0.189 ± 0.507 | 20% | 0.072 ± 0.131 | certified |
| cse2018 | 0.2 | 0.001 | Bates BH | 0.301 ± 0.035 | 100% | 0.694 ± 0.229 | certified |
| cse2018 | 0.2 | 0.001 | PACT conditional | 0.292 ± 0.137 | 88% | 0.441 ± 0.212 | certified |
| cse2018 | 0.2 | 0.001 | Storey-BH | 0.304 ± 0.036 | 100% | 0.698 ± 0.227 | certified |
| cse2018 | 0.2 | 0.001 | BY | 0.001 ± 0.003 | 0% | 0.000 ± 0.001 | certified |
| cse2018 | 0.2 | 0.001 | e-BH | 0.233 ± 0.505 | 36% | 0.073 ± 0.132 | certified |
| cicids2017 | 0.1 | 0.01 | Bates BH | 0.100 ± 0.049 | 60% | 0.376 ± 0.420 | certified |
| cicids2017 | 0.1 | 0.01 | PACT conditional | 0.073 ± 0.059 | 36% | 0.186 ± 0.304 | certified |
| cicids2017 | 0.1 | 0.01 | Storey-BH | 0.100 ± 0.049 | 60% | 0.377 ± 0.421 | certified |
| cicids2017 | 0.1 | 0.01 | BY | 0.000 ± 0.000 | 0% | 0.000 ± 0.000 | certified |
| cicids2017 | 0.1 | 0.01 | e-BH | 0.054 ± 0.093 | 40% | 0.011 ± 0.018 | certified |
| cicids2017 | 0.1 | 0.001 | Bates BH | 0.181 ± 0.186 | 72% | 0.018 ± 0.023 | certified |
| cicids2017 | 0.1 | 0.001 | PACT conditional | 0.000 ± 0.000 | 0% | 0.000 ± 0.000 | certified |
| cicids2017 | 0.1 | 0.001 | Storey-BH | 0.181 ± 0.186 | 72% | 0.018 ± 0.023 | certified |
| cicids2017 | 0.1 | 0.001 | BY | 0.000 ± 0.000 | 0% | 0.000 ± 0.000 | certified |
| cicids2017 | 0.1 | 0.001 | e-BH | 0.087 ± 0.148 | 40% | 0.004 ± 0.007 | certified |
| cicids2017 | 0.2 | 0.01 | Bates BH | 0.163 ± 0.032 | 0% | 0.727 ± 0.253 | certified |
| cicids2017 | 0.2 | 0.01 | PACT conditional | 0.135 ± 0.028 | 0% | 0.551 ± 0.388 | certified |
| cicids2017 | 0.2 | 0.01 | Storey-BH | 0.164 ± 0.032 | 0% | 0.730 ± 0.252 | certified |
| cicids2017 | 0.2 | 0.01 | BY | 0.004 ± 0.009 | 0% | 0.001 ± 0.002 | certified |
| cicids2017 | 0.2 | 0.01 | e-BH | 0.053 ± 0.093 | 0% | 0.020 ± 0.027 | certified |
| cicids2017 | 0.2 | 0.001 | Bates BH | 0.459 ± 0.288 | 80% | 0.164 ± 0.177 | certified |
| cicids2017 | 0.2 | 0.001 | PACT conditional | 0.193 ± 0.182 | 44% | 0.022 ± 0.027 | certified |
| cicids2017 | 0.2 | 0.001 | Storey-BH | 0.459 ± 0.288 | 80% | 0.164 ± 0.177 | certified |
| cicids2017 | 0.2 | 0.001 | BY | 0.000 ± 0.000 | 0% | 0.000 ± 0.000 | certified |
| cicids2017 | 0.2 | 0.001 | e-BH | 0.236 ± 0.403 | 40% | 0.022 ± 0.028 | certified |
| toniot | 0.1 | 0.01 | Bates BH | 0.298 ± 0.397 | 60% | 0.001 ± 0.002 | certified |
| toniot | 0.1 | 0.01 | PACT conditional | 0.000 ± 0.000 | 0% | 0.000 ± 0.000 | certified |
| toniot | 0.1 | 0.01 | Storey-BH | 0.298 ± 0.397 | 60% | 0.001 ± 0.002 | certified |
| toniot | 0.1 | 0.01 | BY | 0.000 ± 0.000 | 0% | 0.000 ± 0.000 | certified |
| toniot | 0.1 | 0.01 | e-BH | 0.254 ± 0.445 | 40% | 0.001 ± 0.002 | certified |
| toniot | 0.1 | 0.001 | Bates BH | 0.361 ± 0.482 | 60% | 0.002 ± 0.003 | certified |
| toniot | 0.1 | 0.001 | PACT conditional | 0.000 ± 0.000 | 0% | 0.000 ± 0.000 | certified |
| toniot | 0.1 | 0.001 | Storey-BH | 0.361 ± 0.482 | 60% | 0.002 ± 0.003 | certified |
| toniot | 0.1 | 0.001 | BY | 0.000 ± 0.000 | 0% | 0.000 ± 0.000 | certified |
| toniot | 0.1 | 0.001 | e-BH | 0.312 ± 0.531 | 40% | 0.002 ± 0.003 | certified |
| toniot | 0.2 | 0.01 | Bates BH | 0.545 ± 0.289 | 92% | 0.003 ± 0.003 | certified |
| toniot | 0.2 | 0.01 | PACT conditional | 0.090 ± 0.121 | 20% | 0.000 ± 0.001 | certified |
| toniot | 0.2 | 0.01 | Storey-BH | 0.550 ± 0.287 | 92% | 0.003 ± 0.003 | certified |
| toniot | 0.2 | 0.01 | BY | 0.000 ± 0.000 | 0% | 0.000 ± 0.000 | certified |
| toniot | 0.2 | 0.01 | e-BH | 0.254 ± 0.445 | 40% | 0.001 ± 0.002 | certified |
| toniot | 0.2 | 0.001 | Bates BH | 0.671 ± 0.415 | 80% | 0.003 ± 0.004 | certified |
| toniot | 0.2 | 0.001 | PACT conditional | 0.062 ± 0.087 | 8% | 0.000 ± 0.001 | certified |
| toniot | 0.2 | 0.001 | Storey-BH | 0.671 ± 0.415 | 80% | 0.003 ± 0.004 | certified |
| toniot | 0.2 | 0.001 | BY | 0.000 ± 0.000 | 0% | 0.000 ± 0.000 | certified |
| toniot | 0.2 | 0.001 | e-BH | 0.312 ± 0.531 | 40% | 0.002 ± 0.003 | certified |
| ciciomt2024 | 0.1 | 0.01 | Bates BH | 0.976 ± 0.044 | 100% | 0.214 ± 0.544 | refuse |
| ciciomt2024 | 0.1 | 0.01 | PACT conditional | 0.904 ± 0.170 | 100% | 0.207 ± 0.549 | refuse |
| ciciomt2024 | 0.1 | 0.01 | Storey-BH | 0.975 ± 0.041 | 100% | 0.239 ± 0.529 | refuse |
| ciciomt2024 | 0.1 | 0.01 | BY | 0.000 ± 0.000 | 0% | 0.000 ± 0.000 | refuse |
| ciciomt2024 | 0.1 | 0.01 | e-BH | 0.936 ± 0.164 | 100% | 0.000 ± 0.000 | refuse |
| ciciomt2024 | 0.1 | 0.001 | Bates BH | 0.995 ± 0.006 | 100% | 0.214 ± 0.544 | refuse |
| ciciomt2024 | 0.1 | 0.001 | PACT conditional | 0.915 ± 0.167 | 100% | 0.207 ± 0.548 | refuse |
| ciciomt2024 | 0.1 | 0.001 | Storey-BH | 0.998 ± 0.004 | 100% | 0.232 ± 0.533 | refuse |
| ciciomt2024 | 0.1 | 0.001 | BY | 0.000 ± 0.000 | 0% | 0.000 ± 0.000 | refuse |
| ciciomt2024 | 0.1 | 0.001 | e-BH | 0.951 ± 0.126 | 100% | 0.000 ± 0.000 | refuse |
| ciciomt2024 | 0.2 | 0.01 | Bates BH | 0.936 ± 0.057 | 100% | 0.718 ± 0.522 | refuse |
| ciciomt2024 | 0.2 | 0.01 | PACT conditional | 0.937 ± 0.061 | 100% | 0.669 ± 0.521 | refuse |
| ciciomt2024 | 0.2 | 0.01 | Storey-BH | 0.944 ± 0.041 | 100% | 0.797 ± 0.533 | refuse |
| ciciomt2024 | 0.2 | 0.01 | BY | 0.020 ± 0.038 | 0% | 0.000 ± 0.000 | refuse |
| ciciomt2024 | 0.2 | 0.01 | e-BH | 0.936 ± 0.164 | 100% | 0.000 ± 0.000 | refuse |
| ciciomt2024 | 0.2 | 0.001 | Bates BH | 0.993 ± 0.007 | 100% | 0.679 ± 0.504 | refuse |
| ciciomt2024 | 0.2 | 0.001 | PACT conditional | 0.994 ± 0.006 | 100% | 0.597 ± 0.476 | refuse |
| ciciomt2024 | 0.2 | 0.001 | Storey-BH | 0.994 ± 0.005 | 100% | 0.791 ± 0.528 | refuse |
| ciciomt2024 | 0.2 | 0.001 | BY | 0.036 ± 0.080 | 4% | 0.000 ± 0.000 | refuse |
| ciciomt2024 | 0.2 | 0.001 | e-BH | 0.951 ± 0.126 | 100% | 0.000 ± 0.000 | refuse |



### RQ1 gate (b): conditional procedure at π = 0.01

| dataset | q | FDR | draws>q | power | refused seeds | pass |
|---|---|---|---|---|---|---|
| cse2018 | 0.1 | 0.069 | 0% | 0.947 | 0 | PASS |
| cse2018 | 0.2 | 0.157 | 0% | 0.994 | 0 | PASS |
| cicids2017 | 0.1 | 0.073 | 36% | 0.186 | 0 | fail |
| cicids2017 | 0.2 | 0.135 | 0% | 0.551 | 0 | PASS |
| toniot | 0.1 | 0.000 | 0% | 0.000 | 0 | fail |
| toniot | 0.2 | 0.090 | 20% | 0.000 | 0 | fail |
| ciciomt2024 | 0.1 | 0.904 | 100% | 0.207 | 5 | fail |
| ciciomt2024 | 0.2 | 0.937 | 100% | 0.669 | 5 | fail |



## RQ2 — marginal vs training-conditional per calibration draw

| dataset | q | π | marginal draws>q | conditional draws>q | marginal power | conditional power | power price | refused | gate |
|---|---|---|---|---|---|---|---|---|---|
| cse2018 | 0.1 | 0.01 | 36% | 0% | 0.977 | 0.947 | 3.0% | 0 | MET |
| cse2018 | 0.1 | 0.001 | 96% | 36% | 0.295 | 0.048 | 83.6% | 0 |  |
| cse2018 | 0.2 | 0.01 | 8% | 0% | 0.996 | 0.994 | 0.2% | 0 |  |
| cse2018 | 0.2 | 0.001 | 100% | 88% | 0.694 | 0.441 | 36.4% | 0 |  |
| cicids2017 | 0.1 | 0.01 | 60% | 36% | 0.376 | 0.186 | 50.5% | 0 |  |
| cicids2017 | 0.1 | 0.001 | 72% | 0% | 0.018 | 0.000 | 100.0% | 0 |  |
| cicids2017 | 0.2 | 0.01 | 0% | 0% | 0.727 | 0.551 | 24.2% | 0 |  |
| cicids2017 | 0.2 | 0.001 | 80% | 44% | 0.164 | 0.022 | 86.9% | 0 |  |
| toniot | 0.1 | 0.01 | 60% | 0% | 0.001 | 0.000 | 100.0% | 0 |  |
| toniot | 0.1 | 0.001 | 60% | 0% | 0.002 | 0.000 | 100.0% | 0 |  |
| toniot | 0.2 | 0.01 | 92% | 20% | 0.003 | 0.000 | 88.8% | 0 |  |
| toniot | 0.2 | 0.001 | 80% | 8% | 0.003 | 0.000 | 83.6% | 0 |  |
| ciciomt2024 | 0.1 | 0.01 | 100% | 100% | 0.214 | 0.207 | 3.4% | 5 |  |
| ciciomt2024 | 0.1 | 0.001 | 100% | 100% | 0.214 | 0.207 | 3.2% | 5 |  |
| ciciomt2024 | 0.2 | 0.01 | 100% | 100% | 0.718 | 0.669 | 6.8% | 5 |  |
| ciciomt2024 | 0.2 | 0.001 | 100% | 100% | 0.679 | 0.597 | 12.0% | 5 |  |

## Does the framework predict its own failures? (pre-stream classification)

Each row is classified from three quantities available before any alert is raised: the exchangeability audit, the conditional barrier at L = 100, and the clairvoyant ceiling. The measured column is the same cell of the window_draws stage. **Agreement: 15/16.** Dropping the clairvoyant ceiling, which a deployment cannot compute, leaves **13/16**.

| dataset | q | π | calibration needed | budget ok | ceiling | exchangeable | predicted | measured |  |
|---|---|---|---|---|---|---|---|---|---|
| cse2018 | 0.1 | 0.01 | 6,904 | yes | 0.970 | yes | usable | usable | ✓ |
| cse2018 | 0.1 | 0.001 | 69,074 | no | 0.729 | yes | budget-limited | no power | ✓ |
| cse2018 | 0.2 | 0.01 | 3,450 | yes | 0.970 | yes | usable | usable | ✓ |
| cse2018 | 0.2 | 0.001 | 34,535 | no | 0.729 | yes | budget-limited | no power | ✓ |
| cicids2017 | 0.1 | 0.01 | 6,904 | yes | 0.586 | yes | usable | no power | ✗ |
| cicids2017 | 0.1 | 0.001 | 69,074 | no | 0.293 | yes | budget-limited | no power | ✓ |
| cicids2017 | 0.2 | 0.01 | 3,450 | yes | 0.586 | yes | usable | usable | ✓ |
| cicids2017 | 0.2 | 0.001 | 34,535 | no | 0.293 | yes | budget-limited | no power | ✓ |
| toniot | 0.1 | 0.01 | 6,904 | yes | 0.020 | yes | detector-limited | no power | ✓ |
| toniot | 0.1 | 0.001 | 69,074 | no | 0.027 | yes | budget-limited | no power | ✓ |
| toniot | 0.2 | 0.01 | 3,450 | yes | 0.020 | yes | detector-limited | no power | ✓ |
| toniot | 0.2 | 0.001 | 34,535 | no | 0.027 | yes | budget-limited | no power | ✓ |
| ciciomt2024 | 0.1 | 0.01 | 6,904 | yes | 0.001 | no | refuse | guarantee broken | ✓ |
| ciciomt2024 | 0.1 | 0.001 | 69,074 | no | 0.001 | no | refuse | guarantee broken | ✓ |
| ciciomt2024 | 0.2 | 0.01 | 3,450 | yes | 0.001 | no | refuse | guarantee broken | ✓ |
| ciciomt2024 | 0.2 | 0.001 | 34,535 | no | 0.001 | no | refuse | guarantee broken | ✓ |

A row marked ✗ is a cell the framework did not call in advance and is discussed as such.

## Sensitivity to the prevalence estimate the gate is given

The gate certifies at n = 12,000 whenever the estimate reaches the threshold in the third column, which does not depend on the true prevalence. The last three columns give the state when the operator supplies half, exactly, and twice the true value.

| dataset | q | true π | audit refuses | π̂ needed to certify | as a factor of π | π̂ = ½π | π̂ = π | π̂ = 2π |
|---|---|---|---|---|---|---|---|---|
| cse2018 | 0.1 | 0.01 | no | 5.75e-03 | 0.58x | degraded | certified | certified |
| cse2018 | 0.1 | 0.001 | no | 5.75e-03 | 5.75x | refuse | degraded | degraded |
| cse2018 | 0.2 | 0.01 | no | 2.88e-03 | 0.29x | certified | certified | certified |
| cse2018 | 0.2 | 0.001 | no | 2.88e-03 | 2.88x | degraded | degraded | degraded |
| cicids2017 | 0.1 | 0.01 | no | 5.75e-03 | 0.58x | degraded | certified | certified |
| cicids2017 | 0.1 | 0.001 | no | 5.75e-03 | 5.75x | refuse | degraded | degraded |
| cicids2017 | 0.2 | 0.01 | no | 2.88e-03 | 0.29x | certified | certified | certified |
| cicids2017 | 0.2 | 0.001 | no | 2.88e-03 | 2.88x | degraded | degraded | degraded |
| toniot | 0.1 | 0.01 | no | 5.75e-03 | 0.58x | degraded | certified | certified |
| toniot | 0.1 | 0.001 | no | 5.75e-03 | 5.75x | refuse | degraded | degraded |
| toniot | 0.2 | 0.01 | no | 2.88e-03 | 0.29x | certified | certified | certified |
| toniot | 0.2 | 0.001 | no | 2.88e-03 | 2.88x | degraded | degraded | degraded |
| ciciomt2024 | 0.1 | 0.01 | yes | 5.75e-03 | 0.58x | refuse | refuse | refuse |
| ciciomt2024 | 0.1 | 0.001 | yes | 5.75e-03 | 5.75x | refuse | refuse | refuse |
| ciciomt2024 | 0.2 | 0.01 | yes | 2.88e-03 | 0.29x | refuse | refuse | refuse |
| ciciomt2024 | 0.2 | 0.001 | yes | 2.88e-03 | 2.88x | refuse | refuse | refuse |

Cells wrongly certified by a two-fold over-estimate: **0/16**. Certified cells downgraded by a two-fold under-estimate: **3/16**.

## What the operator already does — percentile threshold versus PACT

A percentile threshold is what a SOC runs today: alert on the top x% of traffic by score, with the threshold read off the same calibration sample. It is compared here at the same alert volume per 1,000 flows. The last column is the difference that matters: whether the false-alert share carries a promise that holds for this calibration sample, or is only observed after the fact.

| dataset | q | π | policy | alerts/1000 | FDP | power | streams over q | makes an FDR claim |
|---|---|---|---|---|---|---|---|---|
| cse2018 | 0.1 | 0.01 | top 5% | 60.09 ± 1.23 | 0.835 ± 0.003 | 1.000 ± 0.000 | 100% | no |
| cse2018 | 0.1 | 0.01 | top 1% | 19.49 ± 0.70 | 0.491 ± 0.019 | 1.000 ± 0.001 | 100% | no |
| cse2018 | 0.1 | 0.01 | top 0.1% | 10.74 ± 0.30 | 0.092 ± 0.030 | 0.983 ± 0.022 | 40% | no |
| cse2018 | 0.1 | 0.01 | marginal BH | 10.67 ± 0.47 | 0.095 ± 0.029 | 0.973 ± 0.038 | 44% | yes |
| cse2018 | 0.1 | 0.01 | PACT conditional L=5 | 8.17 ± 3.11 | 0.053 ± 0.016 | 0.780 ± 0.300 | 0% | yes |
| cse2018 | 0.1 | 0.001 | top 5% | 51.61 ± 1.23 | 0.980 ± 0.000 | 1.000 ± 0.000 | 100% | no |
| cse2018 | 0.1 | 0.001 | top 1% | 10.66 ± 0.71 | 0.904 ± 0.007 | 0.999 ± 0.003 | 100% | no |
| cse2018 | 0.1 | 0.001 | top 0.1% | 2.01 ± 0.33 | 0.497 ± 0.088 | 0.974 ± 0.039 | 100% | no |
| cse2018 | 0.1 | 0.001 | marginal BH | 0.37 ± 0.30 | 0.209 ± 0.086 | 0.261 ± 0.210 | 64% | yes |
| cse2018 | 0.1 | 0.001 | PACT conditional L=5 | 0.00 ± 0.00 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0% | yes |
| cse2018 | 0.2 | 0.01 | top 5% | 60.09 ± 1.23 | 0.835 ± 0.003 | 1.000 ± 0.000 | 100% | no |
| cse2018 | 0.2 | 0.01 | top 1% | 19.49 ± 0.70 | 0.491 ± 0.019 | 1.000 ± 0.001 | 100% | no |
| cse2018 | 0.2 | 0.01 | top 0.1% | 10.74 ± 0.30 | 0.092 ± 0.030 | 0.983 ± 0.022 | 0% | no |
| cse2018 | 0.2 | 0.01 | marginal BH | 12.21 ± 0.33 | 0.191 ± 0.023 | 0.996 ± 0.010 | 40% | yes |
| cse2018 | 0.2 | 0.01 | PACT conditional L=5 | 11.12 ± 0.41 | 0.124 ± 0.026 | 0.981 ± 0.029 | 0% | yes |
| cse2018 | 0.2 | 0.001 | top 5% | 51.61 ± 1.23 | 0.980 ± 0.000 | 1.000 ± 0.000 | 100% | no |
| cse2018 | 0.2 | 0.001 | top 1% | 10.66 ± 0.71 | 0.904 ± 0.007 | 0.999 ± 0.003 | 100% | no |
| cse2018 | 0.2 | 0.001 | top 0.1% | 2.01 ± 0.33 | 0.497 ± 0.088 | 0.974 ± 0.039 | 100% | no |
| cse2018 | 0.2 | 0.001 | marginal BH | 0.99 ± 0.43 | 0.353 ± 0.093 | 0.624 ± 0.266 | 96% | yes |
| cse2018 | 0.2 | 0.001 | PACT conditional L=5 | 0.08 ± 0.08 | 0.124 ± 0.143 | 0.051 ± 0.043 | 28% | yes |
| cicids2017 | 0.1 | 0.01 | top 5% | 59.07 ± 3.30 | 0.834 ± 0.009 | 0.990 ± 0.002 | 100% | no |
| cicids2017 | 0.1 | 0.01 | top 1% | 18.71 ± 1.79 | 0.489 ± 0.035 | 0.962 ± 0.037 | 100% | no |
| cicids2017 | 0.1 | 0.01 | top 0.1% | 6.93 ± 2.25 | 0.105 ± 0.020 | 0.627 ± 0.213 | 60% | no |
| cicids2017 | 0.1 | 0.01 | marginal BH | 4.14 ± 4.57 | 0.110 ± 0.045 | 0.372 ± 0.420 | 60% | yes |
| cicids2017 | 0.1 | 0.01 | PACT conditional L=5 | 0.56 ± 1.33 | 0.053 ± 0.101 | 0.049 ± 0.119 | 28% | yes |
| cicids2017 | 0.1 | 0.001 | top 5% | 50.75 ± 3.33 | 0.980 ± 0.001 | 0.996 ± 0.004 | 100% | no |
| cicids2017 | 0.1 | 0.001 | top 1% | 10.24 ± 1.56 | 0.902 ± 0.013 | 0.972 ± 0.033 | 100% | no |
| cicids2017 | 0.1 | 0.001 | top 0.1% | 1.37 ± 0.36 | 0.531 ± 0.049 | 0.635 ± 0.198 | 100% | no |
| cicids2017 | 0.1 | 0.001 | marginal BH | 0.06 ± 0.09 | 0.260 ± 0.220 | 0.020 ± 0.036 | 32% | yes |
| cicids2017 | 0.1 | 0.001 | PACT conditional L=5 | 0.00 ± 0.00 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0% | yes |
| cicids2017 | 0.2 | 0.01 | top 5% | 59.07 ± 3.30 | 0.834 ± 0.009 | 0.990 ± 0.002 | 100% | no |
| cicids2017 | 0.2 | 0.01 | top 1% | 18.71 ± 1.79 | 0.489 ± 0.035 | 0.962 ± 0.037 | 100% | no |
| cicids2017 | 0.2 | 0.01 | top 0.1% | 6.93 ± 2.25 | 0.105 ± 0.020 | 0.627 ± 0.213 | 0% | no |
| cicids2017 | 0.2 | 0.01 | marginal BH | 8.26 ± 3.53 | 0.151 ± 0.030 | 0.703 ± 0.295 | 4% | yes |
| cicids2017 | 0.2 | 0.01 | PACT conditional L=5 | 4.46 ± 4.82 | 0.119 ± 0.046 | 0.396 ± 0.439 | 8% | yes |
| cicids2017 | 0.2 | 0.001 | top 5% | 50.75 ± 3.33 | 0.980 ± 0.001 | 0.996 ± 0.004 | 100% | no |
| cicids2017 | 0.2 | 0.001 | top 1% | 10.24 ± 1.56 | 0.902 ± 0.013 | 0.972 ± 0.033 | 100% | no |
| cicids2017 | 0.2 | 0.001 | top 0.1% | 1.37 ± 0.36 | 0.531 ± 0.049 | 0.635 ± 0.198 | 100% | no |
| cicids2017 | 0.2 | 0.001 | marginal BH | 0.40 ± 0.40 | 0.468 ± 0.206 | 0.179 ± 0.197 | 80% | yes |
| cicids2017 | 0.2 | 0.001 | PACT conditional L=5 | 0.01 ± 0.03 | 0.062 ± 0.113 | 0.003 ± 0.007 | 8% | yes |
| toniot | 0.1 | 0.01 | top 5% | 57.71 ± 3.15 | 0.893 ± 0.023 | 0.626 ± 0.155 | 100% | no |
| toniot | 0.1 | 0.01 | top 1% | 13.35 ± 1.46 | 0.812 ± 0.083 | 0.258 ± 0.135 | 100% | no |
| toniot | 0.1 | 0.01 | top 0.1% | 1.21 ± 0.63 | 0.726 ± 0.170 | 0.033 ± 0.021 | 100% | no |
| toniot | 0.1 | 0.01 | marginal BH | 0.01 ± 0.01 | 0.090 ± 0.111 | 0.000 ± 0.000 | 12% | yes |
| toniot | 0.1 | 0.01 | PACT conditional L=5 | 0.00 ± 0.00 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0% | yes |
| toniot | 0.1 | 0.001 | top 5% | 52.66 ± 2.09 | 0.988 ± 0.002 | 0.637 ± 0.128 | 100% | no |
| toniot | 0.1 | 0.001 | top 1% | 11.19 ± 0.97 | 0.975 ± 0.012 | 0.266 ± 0.129 | 100% | no |
| toniot | 0.1 | 0.001 | top 0.1% | 0.91 ± 0.58 | 0.974 ± 0.022 | 0.020 ± 0.015 | 100% | no |
| toniot | 0.1 | 0.001 | marginal BH | 0.01 ± 0.02 | 0.080 ± 0.136 | 0.000 ± 0.000 | 8% | yes |
| toniot | 0.1 | 0.001 | PACT conditional L=5 | 0.00 ± 0.00 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0% | yes |
| toniot | 0.2 | 0.01 | top 5% | 57.71 ± 3.15 | 0.893 ± 0.023 | 0.626 ± 0.155 | 100% | no |
| toniot | 0.2 | 0.01 | top 1% | 13.35 ± 1.46 | 0.812 ± 0.083 | 0.258 ± 0.135 | 100% | no |
| toniot | 0.2 | 0.01 | top 0.1% | 1.21 ± 0.63 | 0.726 ± 0.170 | 0.033 ± 0.021 | 100% | no |
| toniot | 0.2 | 0.01 | marginal BH | 0.12 ± 0.11 | 0.549 ± 0.286 | 0.003 ± 0.003 | 72% | yes |
| toniot | 0.2 | 0.01 | PACT conditional L=5 | 0.00 ± 0.00 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0% | yes |
| toniot | 0.2 | 0.001 | top 5% | 52.66 ± 2.09 | 0.988 ± 0.002 | 0.637 ± 0.128 | 100% | no |
| toniot | 0.2 | 0.001 | top 1% | 11.19 ± 0.97 | 0.975 ± 0.012 | 0.266 ± 0.129 | 100% | no |
| toniot | 0.2 | 0.001 | top 0.1% | 0.91 ± 0.58 | 0.974 ± 0.022 | 0.020 ± 0.015 | 100% | no |
| toniot | 0.2 | 0.001 | marginal BH | 0.08 ± 0.03 | 0.617 ± 0.310 | 0.002 ± 0.003 | 64% | yes |
| toniot | 0.2 | 0.001 | PACT conditional L=5 | 0.00 ± 0.00 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0% | yes |
| ciciomt2024 | 0.1 | 0.01 | top 5% | 163.49 ± 7.52 | 0.950 ± 0.029 | 0.823 ± 0.490 | 100% | no |
| ciciomt2024 | 0.1 | 0.01 | top 1% | 77.31 ± 25.26 | 0.949 ± 0.085 | 0.410 ± 0.644 | 100% | no |
| ciciomt2024 | 0.1 | 0.01 | top 0.1% | 8.22 ± 7.73 | 0.982 ± 0.020 | 0.013 ± 0.011 | 100% | no |
| ciciomt2024 | 0.1 | 0.01 | marginal BH | 39.18 ± 53.15 | 0.937 ± 0.106 | 0.211 ± 0.547 | 96% | yes |
| ciciomt2024 | 0.1 | 0.01 | PACT conditional L=5 | 23.51 ± 59.21 | 0.461 ± 0.595 | 0.199 ± 0.550 | 48% | yes |
| ciciomt2024 | 0.1 | 0.001 | top 5% | 157.61 ± 6.32 | 0.995 ± 0.003 | 0.821 ± 0.495 | 100% | no |
| ciciomt2024 | 0.1 | 0.001 | top 1% | 74.41 ± 23.52 | 0.994 ± 0.010 | 0.400 ± 0.653 | 100% | no |
| ciciomt2024 | 0.1 | 0.001 | top 0.1% | 8.19 ± 7.79 | 0.999 ± 0.002 | 0.007 ± 0.008 | 100% | no |
| ciciomt2024 | 0.1 | 0.001 | marginal BH | 37.14 ± 47.94 | 0.997 ± 0.005 | 0.204 ± 0.552 | 100% | yes |
| ciciomt2024 | 0.1 | 0.001 | PACT conditional L=5 | 20.23 ± 51.18 | 0.517 ± 0.567 | 0.192 ± 0.530 | 52% | yes |
| ciciomt2024 | 0.2 | 0.01 | top 5% | 163.49 ± 7.52 | 0.950 ± 0.029 | 0.823 ± 0.490 | 100% | no |
| ciciomt2024 | 0.2 | 0.01 | top 1% | 77.31 ± 25.26 | 0.949 ± 0.085 | 0.410 ± 0.644 | 100% | no |
| ciciomt2024 | 0.2 | 0.01 | top 0.1% | 8.22 ± 7.73 | 0.982 ± 0.020 | 0.013 ± 0.011 | 100% | no |
| ciciomt2024 | 0.2 | 0.01 | marginal BH | 118.83 ± 33.49 | 0.937 ± 0.060 | 0.695 ± 0.528 | 100% | yes |
| ciciomt2024 | 0.2 | 0.01 | PACT conditional L=5 | 105.89 ± 35.58 | 0.943 ± 0.063 | 0.537 ± 0.493 | 100% | yes |
| ciciomt2024 | 0.2 | 0.001 | top 5% | 157.61 ± 6.32 | 0.995 ± 0.003 | 0.821 ± 0.495 | 100% | no |
| ciciomt2024 | 0.2 | 0.001 | top 1% | 74.41 ± 23.52 | 0.994 ± 0.010 | 0.400 ± 0.653 | 100% | no |
| ciciomt2024 | 0.2 | 0.001 | top 0.1% | 8.19 ± 7.79 | 0.999 ± 0.002 | 0.007 ± 0.008 | 100% | no |
| ciciomt2024 | 0.2 | 0.001 | marginal BH | 110.75 ± 37.71 | 0.993 ± 0.007 | 0.621 ± 0.510 | 100% | yes |
| ciciomt2024 | 0.2 | 0.001 | PACT conditional L=5 | 98.90 ± 39.43 | 0.996 ± 0.004 | 0.402 ± 0.468 | 100% | yes |

### RQ1 gate (a): contamination floor T4 on below-barrier firing cells

Bound holds on **340/340** cells.

| dataset | holds |
|---|---|
| cicids2017 | 54/54 |
| ciciomt2024 | 215/215 |
| cse2018 | 46/46 |
| toniot | 25/25 |

### RQ1 gate (c): the barrier binds the whole panel (largest calibration, window 2,000, q = 0.1)

T7 (e-BH never beats Bates BH) holds on every cell: **True**.

| dataset | method | π | AUROC | clairvoyant ceiling | Bates BH | PACT conditional | e-BH | diagnosis |
|---|---|---|---|---|---|---|---|---|
| cicids2017 | AIS-NIDS | 0.001 | 0.925 ± 0.016 | 0.053 ± 0.046 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | feasible |
| cicids2017 | AIS-NIDS | 0.01 | 0.925 ± 0.016 | 0.059 ± 0.053 | 0.018 ± 0.050 | 0.001 ± 0.002 | 0.000 ± 0.000 | feasible |
| cicids2017 | CLOSR | 0.001 | 0.701 ± 0.073 | 0.002 ± 0.002 | 0.001 ± 0.001 | 0.000 ± 0.000 | 0.001 ± 0.001 | detector-limited |
| cicids2017 | CLOSR | 0.01 | 0.701 ± 0.073 | 0.002 ± 0.001 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | detector-limited |
| cicids2017 | DOC++ | 0.001 | 0.929 ± 0.053 | 0.426 ± 0.172 | 0.168 ± 0.168 | 0.000 ± 0.000 | 0.168 ± 0.168 | feasible |
| cicids2017 | DOC++ | 0.01 | 0.929 ± 0.053 | 0.459 ± 0.181 | 0.418 ± 0.187 | 0.346 ± 0.234 | 0.335 ± 0.211 | feasible |
| cicids2017 | EFC | 0.001 | 0.798 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | detector-limited |
| cicids2017 | EFC | 0.01 | 0.798 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | detector-limited |
| cicids2017 | H-EDL | 0.001 | 0.998 ± 0.001 | 0.257 ± 0.068 | 0.013 ± 0.018 | 0.000 ± 0.000 | 0.005 ± 0.008 | feasible |
| cicids2017 | H-EDL | 0.01 | 0.998 ± 0.001 | 0.564 ± 0.147 | 0.373 ± 0.438 | 0.193 ± 0.320 | 0.012 ± 0.019 | feasible |
| cicids2017 | ORI | 0.001 | 0.983 ± 0.001 | 0.159 ± 0.029 | 0.007 ± 0.016 | 0.000 ± 0.000 | 0.005 ± 0.012 | feasible |
| cicids2017 | ORI | 0.01 | 0.983 ± 0.001 | 0.227 ± 0.031 | 0.094 ± 0.138 | 0.023 ± 0.064 | 0.014 ± 0.029 | feasible |
| cicids2017 | RENOIR-DML | 0.001 | 0.984 ± 0.007 | 0.150 ± 0.155 | 0.018 ± 0.042 | 0.000 ± 0.000 | 0.018 ± 0.040 | feasible |
| cicids2017 | RENOIR-DML | 0.01 | 0.984 ± 0.007 | 0.166 ± 0.187 | 0.149 ± 0.248 | 0.090 ± 0.162 | 0.041 ± 0.106 | feasible |
| cicids2017 | usfAD | 0.001 | 0.916 ± 0.004 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | detector-limited |
| cicids2017 | usfAD | 0.01 | 0.916 ± 0.004 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | detector-limited |
| ciciomt2024 | AIS-NIDS | 0.001 | 0.324 ± 0.092 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | detector-limited |
| ciciomt2024 | AIS-NIDS | 0.01 | 0.324 ± 0.092 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | detector-limited |
| ciciomt2024 | CLOSR | 0.001 | 0.228 ± 0.061 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | detector-limited |
| ciciomt2024 | CLOSR | 0.01 | 0.228 ± 0.061 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | detector-limited |
| ciciomt2024 | DOC++ | 0.001 | 0.125 ± 0.075 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | detector-limited |
| ciciomt2024 | DOC++ | 0.01 | 0.125 ± 0.075 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | detector-limited |
| ciciomt2024 | EFC | 0.001 | 0.681 ± 0.003 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | detector-limited |
| ciciomt2024 | EFC | 0.01 | 0.681 ± 0.003 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | detector-limited |
| ciciomt2024 | H-EDL | 0.001 | 0.898 ± 0.057 | 0.001 ± 0.003 | 0.215 ± 0.543 | 0.207 ± 0.545 | 0.000 ± 0.000 | detector-limited |
| ciciomt2024 | H-EDL | 0.01 | 0.898 ± 0.057 | 0.002 ± 0.003 | 0.213 ± 0.546 | 0.206 ± 0.550 | 0.000 ± 0.000 | detector-limited |
| ciciomt2024 | ORI | 0.001 | 0.067 ± 0.001 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | detector-limited |
| ciciomt2024 | ORI | 0.01 | 0.067 ± 0.001 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | detector-limited |
| ciciomt2024 | RENOIR-DML | 0.001 | 0.273 ± 0.027 | 0.000 ± 0.001 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | detector-limited |
| ciciomt2024 | RENOIR-DML | 0.01 | 0.273 ± 0.027 | 0.000 ± 0.001 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | detector-limited |
| ciciomt2024 | usfAD | 0.001 | 0.639 ± 0.033 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | detector-limited |
| ciciomt2024 | usfAD | 0.01 | 0.639 ± 0.033 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | detector-limited |
| cse2018 | AIS-NIDS | 0.001 | 0.947 ± 0.028 | 0.000 ± 0.001 | 0.000 ± 0.001 | 0.000 ± 0.001 | 0.000 ± 0.001 | detector-limited |
| cse2018 | AIS-NIDS | 0.01 | 0.947 ± 0.028 | 0.001 ± 0.001 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | detector-limited |
| cse2018 | CLOSR | 0.001 | 0.954 ± 0.032 | 0.122 ± 0.111 | 0.007 ± 0.013 | 0.000 ± 0.000 | 0.000 ± 0.001 | feasible |
| cse2018 | CLOSR | 0.01 | 0.954 ± 0.032 | 0.149 ± 0.136 | 0.044 ± 0.065 | 0.006 ± 0.010 | 0.000 ± 0.000 | feasible |
| cse2018 | DOC++ | 0.001 | 0.759 ± 0.052 | 0.001 ± 0.003 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | detector-limited |
| cse2018 | DOC++ | 0.01 | 0.759 ± 0.052 | 0.001 ± 0.004 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | detector-limited |
| cse2018 | EFC | 0.001 | 0.984 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | detector-limited |
| cse2018 | EFC | 0.01 | 0.984 ± 0.000 | 0.001 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | detector-limited |
| cse2018 | H-EDL | 0.001 | 1.000 ± 0.000 | 0.893 ± 0.065 | 0.148 ± 0.174 | 0.016 ± 0.033 | 0.073 ± 0.134 | feasible |
| cse2018 | H-EDL | 0.01 | 1.000 ± 0.000 | 0.984 ± 0.029 | 0.981 ± 0.035 | 0.953 ± 0.063 | 0.068 ± 0.123 | feasible |
| cse2018 | ORI | 0.001 | 0.991 ± 0.007 | 0.233 ± 0.126 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | feasible |
| cse2018 | ORI | 0.01 | 0.991 ± 0.007 | 0.225 ± 0.124 | 0.102 ± 0.107 | 0.029 ± 0.045 | 0.000 ± 0.000 | feasible |
| cse2018 | RENOIR-DML | 0.001 | 0.955 ± 0.030 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | detector-limited |
| cse2018 | RENOIR-DML | 0.01 | 0.955 ± 0.030 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | detector-limited |
| cse2018 | usfAD | 0.001 | 0.938 ± 0.009 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | detector-limited |
| cse2018 | usfAD | 0.01 | 0.938 ± 0.009 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | detector-limited |
| toniot | AIS-NIDS | 0.001 | 0.808 ± 0.055 | 0.007 ± 0.002 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | detector-limited |
| toniot | AIS-NIDS | 0.01 | 0.808 ± 0.055 | 0.009 ± 0.004 | 0.000 ± 0.001 | 0.000 ± 0.000 | 0.000 ± 0.000 | detector-limited |
| toniot | CLOSR | 0.001 | 0.829 ± 0.091 | 0.009 ± 0.009 | 0.001 ± 0.001 | 0.000 ± 0.000 | 0.001 ± 0.001 | detector-limited |
| toniot | CLOSR | 0.01 | 0.829 ± 0.091 | 0.008 ± 0.007 | 0.001 ± 0.001 | 0.000 ± 0.000 | 0.000 ± 0.000 | detector-limited |
| toniot | DOC++ | 0.001 | 0.746 ± 0.031 | 0.004 ± 0.007 | 0.000 ± 0.001 | 0.000 ± 0.000 | 0.000 ± 0.001 | detector-limited |
| toniot | DOC++ | 0.01 | 0.746 ± 0.031 | 0.005 ± 0.005 | 0.001 ± 0.002 | 0.000 ± 0.000 | 0.001 ± 0.002 | detector-limited |
| toniot | EFC | 0.001 | 0.588 ± 0.000 | 0.169 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | feasible |
| toniot | EFC | 0.01 | 0.588 ± 0.000 | 0.163 ± 0.000 | 0.003 ± 0.002 | 0.000 ± 0.001 | 0.000 ± 0.000 | feasible |
| toniot | H-EDL | 0.001 | 0.947 ± 0.017 | 0.024 ± 0.017 | 0.001 ± 0.001 | 0.000 ± 0.000 | 0.001 ± 0.001 | detector-limited |
| toniot | H-EDL | 0.01 | 0.947 ± 0.017 | 0.022 ± 0.014 | 0.001 ± 0.002 | 0.000 ± 0.000 | 0.001 ± 0.002 | detector-limited |
| toniot | ORI | 0.001 | 0.796 ± 0.010 | 0.032 ± 0.021 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | detector-limited |
| toniot | ORI | 0.01 | 0.796 ± 0.010 | 0.031 ± 0.021 | 0.000 ± 0.001 | 0.000 ± 0.000 | 0.000 ± 0.001 | detector-limited |
| toniot | RENOIR-DML | 0.001 | 0.837 ± 0.050 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | detector-limited |
| toniot | RENOIR-DML | 0.01 | 0.837 ± 0.050 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | detector-limited |
| toniot | usfAD | 0.001 | 0.883 ± 0.009 | 0.001 ± 0.002 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | detector-limited |
| toniot | usfAD | 0.01 | 0.883 ± 0.009 | 0.001 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | detector-limited |

AUROC against certified power at π = 0.01: all — 32 pairs, Spearman ρ = 0.48 (p = 0.006), 27 below 0.05; auroc_at_least_0.90 — 14 pairs, Spearman ρ = 0.52 (p = 0.055), 10 below 0.05

## RQ3 — eight-method panel, unknown AUROC (mean ± 95% CI over seeds)

Rotations use the registered hold-out groups (twins held out together).

| dataset | rotation | held out | seeds | H-EDL | CLOSR | EFC | RENOIR-DML | ORI | DOC++ | AIS-NIDS | usfAD |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cse2018 | Z1 | ddos_attack_hoic | 5 | **1.000 ± 0.000** | 0.954 ± 0.032 | 0.984 ± 0.000 | 0.955 ± 0.030 | 0.991 ± 0.007 | 0.759 ± 0.052 | 0.947 ± 0.028 | 0.938 ± 0.009 |
| cse2018 | Z2 | dos_attacks_hulk | 5 | **0.994 ± 0.007** | 0.928 ± 0.033 | 0.981 ± 0.000 | 0.979 ± 0.008 | 0.979 ± 0.005 | 0.869 ± 0.056 | 0.950 ± 0.004 | 0.978 ± 0.002 |
| cse2018 | Z3 | sql_injection+brute_force_web | 5 | **0.965 ± 0.013** | 0.892 ± 0.016 | 0.883 ± 0.000 | 0.931 ± 0.020 | 0.931 ± 0.006 | 0.756 ± 0.099 | 0.920 ± 0.005 | 0.934 ± 0.001 |
| cicids2017 | Z1 | dos_hulk | 5 | **0.998 ± 0.001** | 0.701 ± 0.073 | 0.798 ± 0.000 | 0.984 ± 0.007 | 0.983 ± 0.001 | 0.929 ± 0.053 | 0.925 ± 0.016 | 0.916 ± 0.004 |
| cicids2017 | Z2 | ssh_patator | 5 | **0.999 ± 0.000** | 0.823 ± 0.114 | 0.922 ± 0.000 | 0.862 ± 0.021 | 0.984 ± 0.001 | 0.996 ± 0.001 | 0.836 ± 0.031 | 0.865 ± 0.009 |
| cicids2017 | Z3 | web_attack_xss+web_attack_brute_force | 5 | **0.994 ± 0.002** | 0.976 ± 0.019 | 0.206 ± 0.000 | 0.910 ± 0.027 | 0.797 ± 0.035 | 0.878 ± 0.168 | 0.842 ± 0.041 | 0.896 ± 0.011 |
| toniot | Z1 | ddos | 5 | **0.947 ± 0.017** | 0.829 ± 0.091 | 0.588 ± 0.000 | 0.837 ± 0.050 | 0.796 ± 0.010 | 0.746 ± 0.031 | 0.808 ± 0.055 | 0.883 ± 0.009 |
| toniot | Z2 | injection | 5 | **0.952 ± 0.003** | 0.828 ± 0.035 | 0.678 ± 0.000 | 0.698 ± 0.017 | 0.945 ± 0.001 | 0.809 ± 0.045 | 0.793 ± 0.021 | 0.792 ± 0.004 |
| toniot | Z3 | ransomware | 5 | **0.992 ± 0.003** | 0.868 ± 0.031 | 0.941 ± 0.000 | 0.909 ± 0.033 | 0.983 ± 0.003 | 0.784 ± 0.097 | 0.947 ± 0.011 | 0.949 ± 0.005 |
| ciciomt2024 | Z1 | tcp_ip_ddos_udp | 5 | **0.898 ± 0.057** | 0.228 ± 0.061 | 0.681 ± 0.003 | 0.273 ± 0.027 | 0.067 ± 0.001 | 0.125 ± 0.075 | 0.324 ± 0.092 | 0.639 ± 0.033 |
| ciciomt2024 | Z2 | recon_port_scan | 5 | 0.448 ± 0.070 | 0.698 ± 0.051 | 0.314 ± 0.002 | 0.622 ± 0.025 | 0.280 ± 0.004 | 0.456 ± 0.022 | 0.812 ± 0.007 | **0.848 ± 0.005** |



### Primary test — the rotation is the unit of replication

Averaging the seeds inside each rotation leaves **11** independent rotations. Friedman p = 6.07e-04; H-EDL ranks first in 10 of them.

| method | mean AUROC | mean rank | H-EDL wins | Wilcoxon p | Holm p |
|---|---|---|---|---|---|
| H-EDL | 0.926 | 1.45 | – | – | – |
| usfAD | 0.876 | 4.00 | 10/11 | 0.0537 | 0.1289 |
| RENOIR-DML | 0.814 | 4.27 | 10/11 | 0.0322 | 0.1289 |
| ORI | 0.794 | 4.36 | 11/11 | 0.0010 | 0.0068 |
| AIS-NIDS | 0.828 | 5.00 | 10/11 | 0.0420 | 0.1289 |
| CLOSR | 0.793 | 5.36 | 10/11 | 0.0322 | 0.1289 |
| EFC | 0.725 | 5.55 | 11/11 | 0.0010 | 0.0068 |
| DOC++ | 0.737 | 6.00 | 10/11 | 0.0029 | 0.0146 |

With eleven rotations the smallest p a signed-rank test can return is about 0.001, so this test separates H-EDL from the weaker half of the panel and leaves the stronger half undecided. The seed-level numbers below are reported for completeness; their p-values must not be read as independent evidence.



Secondary, seed level (**55** non-independent blocks): Friedman p = 9.65e-25; H-EDL ranks first in 49 blocks.

| method | mean AUROC | mean rank | H-EDL − method | H-EDL wins | Wilcoxon p (Holm) |
|---|---|---|---|---|---|
| H-EDL | 0.926 ± 0.042 | 1.42 | – | – | – |
| usfAD | 0.876 ± 0.025 | 3.98 | +0.050 | 50/55 | 2.32e-05 |
| ORI | 0.794 ± 0.083 | 4.27 | +0.132 | 55/55 | 7.75e-10 |
| RENOIR-DML | 0.814 ± 0.056 | 4.55 | +0.112 | 49/55 | 1.04e-05 |
| AIS-NIDS | 0.828 ± 0.047 | 4.89 | +0.098 | 50/55 | 1.79e-05 |
| CLOSR | 0.793 ± 0.055 | 5.27 | +0.133 | 50/55 | 1.04e-05 |
| EFC | 0.725 ± 0.069 | 5.60 | +0.201 | 55/55 | 7.75e-10 |
| DOC++ | 0.737 ± 0.066 | 6.02 | +0.189 | 53/55 | 2.82e-09 |

## Label-separability audit and hold-out groups

| dataset | groups @0.80 | groups @0.70 | groups @0.90 | closest attack pairs |
|---|---|---|---|---|
| cse2018 | [['brute_force_web', 'sql_injection'], ['dos_attacks_slowhttptest', 'ftp_bruteforce']] | [['dos_attacks_slowhttptest', 'ftp_bruteforce']] | [['brute_force_web', 'brute_force_xss', 'sql_injection'], ['dos_attacks_slowhttptest', 'ftp_bruteforce']] | dos_attacks_slowhttptest/ftp_bruteforce 0.505; brute_force_web/sql_injection 0.724; brute_force_web/brute_force_xss 0.861 |
| toniot | [] | [] | [] | dos/xss 0.938; injection/xss 0.970; dos/injection 0.980 |
| cicids2017 | [['web_attack_brute_force', 'web_attack_xss']] | [['web_attack_brute_force', 'web_attack_xss']] | [['web_attack_brute_force', 'web_attack_xss']] | web_attack_brute_force/web_attack_xss 0.594; dos_slowhttptest/dos_slowloris 0.994; dos_slowhttptest/web_attack_xss 0.994 |
| ciciomt2024 | [] | [] | [] | recon_os_scan/recon_port_scan 0.918; arp_spoofing/recon_ping_sweep 0.948; arp_spoofing/mqtt_malformed_data 0.960 |



### Threshold sensitivity — cse2018 Z3

| method | t70 | t80 (registered) | t90 |
|---|---|---|---|
| H-EDL | 0.953 ± 0.028 | 0.965 ± 0.013 | 0.987 ± 0.002 |
| CLOSR | 0.872 ± 0.060 | 0.892 ± 0.016 | 0.866 ± 0.019 |
| EFC | 0.872 ± 0.000 | 0.883 ± 0.000 | 0.918 ± 0.000 |
| RENOIR-DML | 0.992 ± 0.002 | 0.931 ± 0.020 | 0.932 ± 0.015 |
| ORI | 0.761 ± 0.011 | 0.931 ± 0.006 | 0.947 ± 0.002 |
| DOC++ | 0.803 ± 0.107 | 0.756 ± 0.099 | 0.853 ± 0.027 |
| AIS-NIDS | 0.946 ± 0.007 | 0.920 ± 0.005 | 0.911 ± 0.015 |
| usfAD | 0.948 ± 0.005 | 0.934 ± 0.001 | 0.933 ± 0.007 |

### RQ3 — tail-lifted scorer (H-EDL, Z1)

A false-alarm rate is only resolvable if enough known test flows sit above it: at 1e-4 the threshold rests on two to six flows on these test splits, so that rate is not reported. TPR@1e-3 raised with AUROC unchanged (|Δ| < 5e-4) on **2** dataset(s); the tie at the score ceiling is what the lift removes.

| dataset | known test flows | flows above 1e-3 | AUROC floored | AUROC tail | TPR@1e-2 floored | TPR@1e-2 tail | TPR@1e-3 floored | TPR@1e-3 tail | ties at max floored | ties at max tail |
|---|---|---|---|---|---|---|---|---|---|---|
| cicids2017 | 15,965 | 16 | 0.9976 ± 0.0009 | 0.9976 ± 0.0010 | 0.962 ± 0.024 | 0.963 ± 0.022 | 0.719 ± 0.169 | 0.721 ± 0.185 | 886 ± 1208 | 1 ± 0 |
| ciciomt2024 | 55,472 | 55 | 0.8976 ± 0.0565 | 0.8972 ± 0.0562 | 0.015 ± 0.011 | 0.015 ± 0.010 | 0.003 ± 0.007 | 0.003 ± 0.006 | 3 ± 2 | 1 ± 0 |
| cse2018 | 29,460 | 29 | 0.9998 ± 0.0001 | 0.9998 ± 0.0001 | 1.000 ± 0.001 | 1.000 ± 0.001 | 0.981 ± 0.040 | 0.985 ± 0.033 | 4200 ± 7934 | 1 ± 0 |
| toniot | 26,202 | 26 | 0.9472 ± 0.0172 | 0.9474 ± 0.0168 | 0.243 ± 0.123 | 0.241 ± 0.107 | 0.041 ± 0.027 | 0.038 ± 0.028 | 12 ± 31 | 1 ± 0 |

### RQ3 — Mondrian calibration by three grouping variables (Prop. 11)

| dataset | grouping | π | pooled power | Mondrian power | pooled FDP | Mondrian FDP | groups lifted from 0 | Prop. 11 correct | audit refused seeds |
|---|---|---|---|---|---|---|---|---|---|
| cicids2017 | port class | 0.001 | 0.024 ± 0.031 | 0.003 ± 0.004 | 0.429 ± 0.314 | 0.403 ± 0.473 | 0 | 3/5 | 0/5 |
| cicids2017 | port class | 0.01 | 0.385 ± 0.423 | 0.297 ± 0.400 | 0.114 ± 0.022 | 0.107 ± 0.028 | 0 | 5/5 | 0/5 |
| cicids2017 | predicted class | 0.001 | 0.024 ± 0.031 | 0.000 ± 0.000 | 0.429 ± 0.314 | 0.000 ± 0.000 | 0 | 21/21 | 0/5 |
| cicids2017 | predicted class | 0.01 | 0.385 ± 0.423 | 0.109 ± 0.156 | 0.114 ± 0.022 | 0.093 ± 0.069 | 0 | 18/28 | 0/5 |
| ciciomt2024 | predicted class | 0.001 | 0.214 ± 0.544 | 0.236 ± 0.530 | 0.997 ± 0.005 | 0.997 ± 0.005 | 0 | 5/5 | 5/5 |
| ciciomt2024 | predicted class | 0.01 | 0.213 ± 0.545 | 0.237 ± 0.530 | 0.975 ± 0.044 | 0.974 ± 0.042 | 0 | 6/12 | 5/5 |
| ciciomt2024 | protocol | 0.001 | 0.214 ± 0.544 | 0.345 ± 0.545 | 0.997 ± 0.005 | 0.990 ± 0.016 | 0 | 5/5 | 5/5 |
| ciciomt2024 | protocol | 0.01 | 0.213 ± 0.545 | 0.442 ± 0.631 | 0.975 ± 0.044 | 0.922 ± 0.102 | 0 | 6/10 | 5/5 |
| cse2018 | port class | 0.001 | 0.320 ± 0.188 | 0.181 ± 0.132 | 0.259 ± 0.227 | 0.167 ± 0.089 | 0 | 5/5 | 0/5 |
| cse2018 | port class | 0.01 | 0.977 ± 0.032 | 0.970 ± 0.037 | 0.092 ± 0.018 | 0.091 ± 0.018 | 0 | 5/5 | 0/5 |
| cse2018 | predicted class | 0.001 | 0.320 ± 0.188 | 0.045 ± 0.109 | 0.259 ± 0.227 | 0.001 ± 0.003 | 0 | 11/15 | 0/5 |
| cse2018 | predicted class | 0.01 | 0.977 ± 0.032 | 0.560 ± 0.349 | 0.092 ± 0.018 | 0.064 ± 0.012 | 0 | 13/19 | 0/5 |
| cse2018 | protocol | 0.001 | 0.320 ± 0.188 | 0.310 ± 0.187 | 0.259 ± 0.227 | 0.246 ± 0.236 | 0 | 5/5 | 0/5 |
| cse2018 | protocol | 0.01 | 0.977 ± 0.032 | 0.972 ± 0.039 | 0.092 ± 0.018 | 0.091 ± 0.020 | 0 | 5/5 | 0/5 |
| toniot | port class | 0.001 | 0.001 ± 0.002 | 0.000 ± 0.001 | 0.761 ± 0.535 | 0.188 ± 0.521 | 0 | 1/5 | 0/5 |
| toniot | port class | 0.01 | 0.001 ± 0.002 | 0.000 ± 0.001 | 0.589 ± 0.504 | 0.200 ± 0.370 | 1 | 8/10 | 0/5 |
| toniot | predicted class | 0.001 | 0.001 ± 0.002 | 0.000 ± 0.000 | 0.761 ± 0.535 | 0.000 ± 0.000 | 0 | 21/26 | 0/5 |
| toniot | predicted class | 0.01 | 0.001 ± 0.002 | 0.000 ± 0.000 | 0.589 ± 0.504 | 0.000 ± 0.000 | 0 | 25/35 | 0/5 |
| toniot | protocol | 0.001 | 0.001 ± 0.002 | 0.000 ± 0.000 | 0.761 ± 0.535 | 0.400 ± 0.680 | 0 | 5/10 | 0/5 |
| toniot | protocol | 0.01 | 0.001 ± 0.002 | 0.000 ± 0.000 | 0.589 ± 0.504 | 0.300 ± 0.555 | 0 | 7/10 | 0/5 |

### RQ3 — clairvoyant ceiling at π = 0.01 (Z1, across seeds)

| dataset | method | ceiling | usable on all seeds | reverses across seeds |
|---|---|---|---|---|
| cicids2017 | AIS-NIDS | 0.062 | False | True |
| cicids2017 | CLOSR | 0.001 | False | False |
| cicids2017 | DOC++ | 0.428 | True | False |
| cicids2017 | EFC | 0.000 | False | False |
| cicids2017 | H-EDL | 0.586 | True | False |
| cicids2017 | ORI | 0.201 | True | False |
| cicids2017 | RENOIR-DML | 0.154 | False | True |
| cicids2017 | usfAD | 0.000 | False | False |
| ciciomt2024 | AIS-NIDS | 0.000 | False | False |
| ciciomt2024 | CLOSR | 0.000 | False | False |
| ciciomt2024 | DOC++ | 0.000 | False | False |
| ciciomt2024 | EFC | 0.000 | False | False |
| ciciomt2024 | H-EDL | 0.001 | False | False |
| ciciomt2024 | ORI | 0.000 | False | False |
| ciciomt2024 | RENOIR-DML | 0.000 | False | False |
| ciciomt2024 | usfAD | 0.000 | False | False |
| cse2018 | AIS-NIDS | 0.001 | False | False |
| cse2018 | CLOSR | 0.127 | False | True |
| cse2018 | DOC++ | 0.002 | False | False |
| cse2018 | EFC | 0.001 | False | False |
| cse2018 | H-EDL | 0.970 | True | False |
| cse2018 | ORI | 0.220 | False | True |
| cse2018 | RENOIR-DML | 0.000 | False | False |
| cse2018 | usfAD | 0.000 | False | False |
| toniot | AIS-NIDS | 0.007 | False | False |
| toniot | CLOSR | 0.007 | False | False |
| toniot | DOC++ | 0.006 | False | False |
| toniot | EFC | 0.088 | False | False |
| toniot | H-EDL | 0.020 | False | False |
| toniot | ORI | 0.026 | False | False |
| toniot | RENOIR-DML | 0.000 | False | False |
| toniot | usfAD | 0.000 | False | False |

## RQ4 — exchangeability gate under label-mix shift (two-sample DKW/Smirnov threshold)

Overall: detection where the guarantee broke **90.6%** (n = 2580), false refusal on exchangeable traffic **8.0%** (n = 900). Gate: detection ≥ 90% and false refusal ≤ 10% → **PASS**. Fires on 76.5% of shifted conditions where the guarantee still held (n = 3780): the price of a gate that tests the shift, not the FDR.

| dataset | broken conditions | detection | false refusal | false alarms/1000 ungated | gated |
|---|---|---|---|---|---|
| cicids2017 | 430 | 59.8% | 10.3% | 0.62 | 0.81 |
| ciciomt2024 | 1350 | 98.7% | – (refused at baseline) | 110.04 | 2.44 |
| cse2018 | 650 | 93.5% | 6.7% | 1.31 | 0.41 |
| toniot | 150 | 93.3% | 7.0% | 0.13 | 2.12 |



| shift magnitude | gate fires | guarantee broken | ungated FDP | false alarms/1000 ungated | gated |
|---|---|---|---|---|---|
| 0.0 | 29.5% | 30.0% | 0.176 | 1.54 | 0.71 |
| 0.1 | 64.8% | 32.5% | 0.187 | 4.91 | 1.11 |
| 0.25 | 79.5% | 35.0% | 0.193 | 11.70 | 1.35 |
| 0.5 | 86.7% | 36.7% | 0.212 | 21.21 | 1.47 |
| 0.75 | 91.2% | 37.5% | 0.229 | 30.34 | 1.56 |
| 1.0 | 93.7% | 43.3% | 0.260 | 55.39 | 1.59 |

## RQ4 — exchangeability gate under label-mix shift (permutation threshold)

Overall: detection where the guarantee broke **90.6%** (n = 2580), false refusal on exchangeable traffic **8.4%** (n = 900). Gate: detection ≥ 90% and false refusal ≤ 10% → **PASS**. Fires on 76.6% of shifted conditions where the guarantee still held (n = 3780): the price of a gate that tests the shift, not the FDR.

| dataset | broken conditions | detection | false refusal | false alarms/1000 ungated | gated |
|---|---|---|---|---|---|
| cicids2017 | 430 | 59.5% | 11.7% | 0.62 | 0.81 |
| ciciomt2024 | 1350 | 98.7% | – (refused at baseline) | 110.04 | 2.43 |
| cse2018 | 650 | 93.5% | 6.7% | 1.31 | 0.41 |
| toniot | 150 | 93.3% | 7.0% | 0.13 | 2.12 |



| shift magnitude | gate fires | guarantee broken | ungated FDP | false alarms/1000 ungated | gated |
|---|---|---|---|---|---|
| 0.0 | 29.8% | 30.0% | 0.176 | 1.54 | 0.71 |
| 0.1 | 65.0% | 32.5% | 0.187 | 4.91 | 1.12 |
| 0.25 | 79.7% | 35.0% | 0.193 | 11.70 | 1.35 |
| 0.5 | 86.5% | 36.7% | 0.212 | 21.21 | 1.47 |
| 0.75 | 91.2% | 37.5% | 0.229 | 30.34 | 1.56 |
| 1.0 | 93.7% | 43.3% | 0.260 | 55.39 | 1.59 |

## Is the audit miscalibrated, or is the traffic not exchangeable?

Sampling the audit window from the calibration pool is an exchangeable null by construction; sampling it from the capture's own held-out known traffic is the deployment setting. α = 0.05.

Exchangeable null: **4.5%** (DKW/Smirnov) and **5.2%** (permutation-calibrated) — both at the nominal level, so the test holds its size. Held-out known traffic: **28.1%** and **28.7%**.

| dataset | fires on the exchangeable null | fires on held-out known traffic |
|---|---|---|
| cicids2017 | 5.0% | 5.4% |
| ciciomt2024 | 3.6% | 94.1% |
| cse2018 | 4.9% | 4.4% |
| toniot | 4.5% | 8.5% |

## Extension: six datasets the method was never tuned on

Each dataset supplies its own calibration size, so the conditional requirement predicts a different state per dataset. PCF scores, five calibration draws, 20 streams of 40,000 flows, window 2,000, L = 100.

| dataset | n | q | π | state | marginal FDR | marginal draws > q | PACT FDR | PACT power | PACT draws > q |
|---|---|---|---|---|---|---|---|---|---|
| NF-BoT-IoT-v3 | 9,100 | 0.1 | 0.01 | certified | 0.339 | 60% | 0.000 | 0.000 | 0% |
| NF-BoT-IoT-v3 | 9,100 | 0.1 | 0.001 | refuse | 0.330 | 53% | 0.000 | 0.000 | 0% |
| NF-BoT-IoT-v3 | 9,100 | 0.2 | 0.01 | certified | 0.672 | 67% | 0.000 | 0.000 | 0% |
| NF-BoT-IoT-v3 | 9,100 | 0.2 | 0.001 | degraded | 0.670 | 67% | 0.000 | 0.000 | 0% |
| CIDDS-001 | 6,100 | 0.1 | 0.01 | degraded | 0.186 | 73% | 0.000 | 0.000 | 0% |
| CIDDS-001 | 6,100 | 0.1 | 0.001 | refuse | 0.232 | 33% | 0.000 | 0.000 | 0% |
| CIDDS-001 | 6,100 | 0.2 | 0.01 | certified | 0.252 | 67% | 0.047 | 0.086 | 0% |
| CIDDS-001 | 6,100 | 0.2 | 0.001 | degraded | 0.776 | 100% | 0.000 | 0.000 | 0% |
| HIKARI-2021 | 4,300 | 0.1 | 0.01 | degraded | 0.329 | 33% | 0.000 | 0.000 | 0% |
| HIKARI-2021 | 4,300 | 0.1 | 0.001 | refuse | 0.330 | 33% | 0.000 | 0.000 | 0% |
| HIKARI-2021 | 4,300 | 0.2 | 0.01 | certified | 0.437 | 60% | 0.000 | 0.000 | 0% |
| HIKARI-2021 | 4,300 | 0.2 | 0.001 | refuse | 0.430 | 67% | 0.000 | 0.000 | 0% |
| InSDN | 9,200 | 0.1 | 0.01 | certified | 0.083 | 33% | 0.003 | 0.232 | 0% |
| InSDN | 9,200 | 0.1 | 0.001 | refuse | 0.011 | 0% | 0.000 | 0.000 | 0% |
| InSDN | 9,200 | 0.2 | 0.01 | certified | 0.190 | 67% | 0.074 | 0.717 | 0% |
| InSDN | 9,200 | 0.2 | 0.001 | degraded | 0.115 | 7% | 0.000 | 0.000 | 0% |
| UNR-IDD | 3,300 | 0.1 | 0.01 | degraded | 0.094 | 33% | 0.000 | 0.000 | 0% |
| UNR-IDD | 3,300 | 0.1 | 0.001 | refuse | 0.204 | 33% | 0.000 | 0.000 | 0% |
| UNR-IDD | 3,300 | 0.2 | 0.01 | degraded | 0.143 | 33% | 0.018 | 0.004 | 0% |
| UNR-IDD | 3,300 | 0.2 | 0.001 | refuse | 0.324 | 60% | 0.000 | 0.000 | 0% |
| NF-UNSW-NB15-v3 | 10,400 | 0.1 | 0.01 | certified | 0.436 | 67% | 0.000 | 0.000 | 0% |
| NF-UNSW-NB15-v3 | 10,400 | 0.1 | 0.001 | degraded | 0.446 | 67% | 0.000 | 0.000 | 0% |
| NF-UNSW-NB15-v3 | 10,400 | 0.2 | 0.01 | certified | 0.840 | 100% | 0.000 | 0.000 | 0% |
| NF-UNSW-NB15-v3 | 10,400 | 0.2 | 0.001 | degraded | 0.834 | 100% | 0.000 | 0.000 | 0% |

Marginal BH exceeded its own target on at least one draw in **23/24** cells. PACT certified **8** cells, of which **2** reach power ≥ 0.1; **0** certified cells contain a draw above q. No cell outside the certified region reaches usable power (0).

## Temporal extension: does random-split optimism replicate?

Two further NetFlow datasets rebuilt along the time axis, same calibration size in both arms of a dataset, q = 0.1, π = 10⁻².

| dataset | procedure | FDR random | FDR temporal | power random | power temporal | draws > q random | draws > q temporal |
|---|---|---|---|---|---|---|---|
| NF-BoT-IoT-v3 | marginal BH | 0.343 | 0.947 | 0.000 | 0.083 | 60% | 100% |
| NF-BoT-IoT-v3 | PACT conditional L=100 | 0.000 | 0.291 | 0.000 | 0.005 | 0% | 40% |
| NF-UNSW-NB15-v3 | marginal BH | 0.449 | 0.224 | 0.000 | 0.000 | 73% | 33% |
| NF-UNSW-NB15-v3 | PACT conditional L=100 | 0.000 | 0.000 | 0.000 | 0.000 | 0% | 0% |

The audit refuses **6/6** time-ordered captures and **0/6** random ones.

## RQ4 — cross-domain gate and two-currency label budget

Gate on cross-domain transfer: detection 100.0% (n = 255), false refusal 4.3% (n = 1275).

### Family labels buy ranking (unknown AUROC, total budget 3,000)

| case | source only | k=2 | k=5 | k=10 | k=20 |
|---|---|---|---|---|---|
| loeo_unsw | 0.485 ± 0.024 | 0.534 ± 0.025 | 0.537 ± 0.030 | 0.559 ± 0.013 | 0.561 ± 0.015 |
| ton_to_unsw | 0.476 ± 0.034 | 0.481 ± 0.060 | 0.493 ± 0.037 | 0.503 ± 0.027 | 0.499 ± 0.030 |
| unsw_to_ton | 0.474 ± 0.063 | 0.811 ± 0.068 | 0.808 ± 0.022 | 0.853 ± 0.028 | 0.860 ± 0.032 |

### Verified-known flows buy the certificate (anchors only, modal state)

| case | B=120 | B=300 | B=1000 | B=3000 |
|---|---|---|---|---|
| loeo_unsw | refuse | refuse | refuse | degraded |
| ton_to_unsw | refuse | refuse | refuse | degraded |
| unsw_to_ton | refuse | refuse | refuse | degraded |

## Deployment latency (device path: encoder + class + zero-day score)

| dataset | scorer | batch | ms/flow | flows/s | Spearman vs NumPy |
|---|---|---|---|---|---|
| cicids2017 | floored | 256 | 0.0632 | 15,831 | 0.999992 |
| cicids2017 | floored | 1024 | 0.0381 | 26,263 | 0.999992 |
| cicids2017 | floored | 4096 | 0.0326 | 30,685 | 0.999992 |
| cicids2017 | tail_lifted | 256 | 0.0731 | 13,671 | 0.999992 |
| cicids2017 | tail_lifted | 1024 | 0.0417 | 24,004 | 0.999992 |
| cicids2017 | tail_lifted | 4096 | 0.0327 | 30,549 | 0.999992 |
| nf_cse_cic_ids2018_v3 | floored | 256 | 0.0515 | 19,413 | 0.999564 |
| nf_cse_cic_ids2018_v3 | floored | 1024 | 0.0358 | 27,961 | 0.999564 |
| nf_cse_cic_ids2018_v3 | floored | 4096 | 0.0332 | 30,152 | 0.999564 |
| nf_cse_cic_ids2018_v3 | tail_lifted | 256 | 0.0689 | 14,508 | 0.999564 |
| nf_cse_cic_ids2018_v3 | tail_lifted | 1024 | 0.0401 | 24,935 | 0.999564 |
| nf_cse_cic_ids2018_v3 | tail_lifted | 4096 | 0.0345 | 29,003 | 0.999564 |

## Random split versus time-ordered split

Two datasets carry flow timestamps. The rotation is rebuilt so that every calibration flow predates every test flow of its family; nothing else changes. Three seeds, q = 0.1, π = 10⁻², n = 12,000.

### The exchangeability audit

Across both datasets the audit refuses **6/6** time-ordered captures and none of the random-split ones.

| dataset | split | violation | DKW bound | captures refused |
|---|---|---|---|---|
| cse2018 | random (Z1) | 0.0049 ± 0.0017 | 0.0107 | 0/3 |
| cse2018 | temporal (T2) | 0.1418 ± 0.0293 | 0.0111 | **3/3** |
| toniot | random (Z1) | 0.0073 ± 0.0051 | 0.0113 | 0/3 |
| toniot | temporal (T2) | 0.1773 ± 0.0140 | 0.0104 | **3/3** |

### What the procedures actually deliver

| dataset | procedure | FDR (random) | over q | power | FDR (temporal) | over q | power |
|---|---|---|---|---|---|---|---|
| cse2018 | marginal BH | 0.095 | 40% | 0.957 | **0.684** | **100%** | 0.997 |
| cse2018 | PACT conditional L=5 | 0.050 | 0% | 0.685 | **0.629** | **100%** | 0.916 |
| cse2018 | PACT conditional L=100 (shipped) | 0.033 | 0% | 0.335 | **0.586** | **100%** | 0.737 |
| toniot | marginal BH | 0.087 | 27% | 0.000 | **0.891** | **100%** | 0.002 |
| toniot | PACT conditional L=5 | 0.000 | 0% | 0.000 | **0.000** | **0%** | 0.000 |
| toniot | PACT conditional L=100 (shipped) | 0.000 | 0% | 0.000 | **0.000** | **0%** | 0.000 |

Every procedure, including the shipped one, quotes q = 0.1 and delivers several times that once the calibration sample is older than the traffic. The audit refuses these captures before a single alert is raised, which is the behaviour the certificate exists for.

### The detector ranking is not stable across the two splits either

| dataset | method | AUROC (random) | AUROC (temporal) | change |
|---|---|---|---|---|
| cse2018 | H-EDL | 1.000 | 0.994 | -0.006 |
| cse2018 | CLOSR | 0.950 | 0.938 | -0.012 |
| cse2018 | EFC | 0.984 | 0.981 | -0.003 |
| cse2018 | RENOIR-DML | 0.953 | 0.971 | +0.018 |
| cse2018 | ORI | 0.990 | 0.985 | -0.006 |
| cse2018 | DOC++ | 0.736 | 0.797 | +0.061 |
| cse2018 | AIS-NIDS | 0.955 | 0.899 | -0.057 |
| cse2018 | usfAD | 0.941 | 0.941 | -0.000 |
| toniot | H-EDL | 0.940 | 0.774 | -0.166 |
| toniot | CLOSR | 0.830 | 0.777 | -0.054 |
| toniot | EFC | 0.588 | 0.925 | +0.337 |
| toniot | RENOIR-DML | 0.857 | 0.741 | -0.116 |
| toniot | ORI | 0.801 | 0.615 | -0.186 |
| toniot | DOC++ | 0.759 | 0.754 | -0.005 |
| toniot | AIS-NIDS | 0.818 | 0.697 | -0.121 |
| toniot | usfAD | 0.886 | 0.795 | -0.091 |

## Bootstrap intervals for the headline numbers

Seeds are resampled whole (cluster bootstrap, 4,000 draws, 95% percentile interval), so the intervals do not assume a normal mean of five points and apply to the share-of-draws statistics as well as to the averages.

| operating point | procedure | power [95% CI] | draws over q [95% CI] |
|---|---|---|---|
| cse2018 q=0.2 | marginal BH | 0.996 [0.988, 1.000] | 20% [4%, 36%] |
| cse2018 q=0.2 | PACT (shipped) | 0.934 [0.856, 0.986] | 0% [0%, 0%] |
| cse2018 q=0.1 | marginal BH | 0.970 [0.944, 0.994] | 36% [4%, 72%] |
| cse2018 q=0.1 | PACT (shipped) | 0.430 [0.228, 0.579] | 0% [0%, 0%] |
| cicids2017 q=0.2 | marginal BH | 0.724 [0.540, 0.887] | 4% [0%, 12%] |
| cicids2017 q=0.2 | PACT (shipped) | 0.228 [0.020, 0.460] | 0% [0%, 0%] |



### RQ3 — margin over the best competing method, per rotation

Averaged over the **11** rotations, PCF leads the strongest other method by **-0.001** AUROC [-0.097, +0.070], and leads in 91% of rotations [73%, 100%]. Resampling is over rotations, the unit the claim is made in.



### RQ4 — the gate, resampling datasets

Detection where the guarantee broke: **90.6%** [68.4%, 98.1%]. False refusal on exchangeable traffic: **8.1%** [6.7%, 10.9%]. With four datasets the interval is wide by construction, and it contains the gate's own threshold — which is the honest way to report a four-cluster result.

## What the method's name may claim

Each named component measured against its own removal, everything else fixed. The detector is called **Prototype Conformal Fusion (PCF)** because those are the parts that survive this table; the code and every result file keep the historical identifier `hedl`.

| component | dataset | with | without | difference | verdict |
|---|---|---|---|---|---|
| trained encoder | cicids2017 | 0.998 | 0.963 | +0.035 | kept |
| trained encoder | cse2018 | 1.000 | 0.997 | +0.003 | kept |
| trained encoder | toniot | 0.947 | 0.810 | +0.137 | kept |
| trained encoder | ciciomt2024 | 0.898 | 0.242 | +0.656 | kept |
| evidential term | ciciomt2024 | 0.898 | 0.911 | -0.013 | p = 0.41 |
| evidential term | toniot | 0.947 | 0.934 | +0.013 | p = 0.10 |
| hyperbolic geometry | cse2018 | 0.9951 | 0.9954 | -0.0003 | dropped |
| k-NN component | cse2018 | 0.9952 | 0.9930 | +0.0021 | kept |

The hyperbolic geometry and the Dirichlet evidential term cannot be told from their own absence (pooled difference +0.0000, p = 1.00 for the evidential term over ten paired runs), so neither is claimed. Every capture in this study was run at curvature 0, that is, in the flat limit.

## Data integrity and what it means for the tables

### Split leakage by source id

| dataset | train | calibration | test | train∩cal / train∩test / cal∩test |
|---|---|---|---|---|
| cse2018 | 139140 | 29913 | 54454 | 0 / 0 / 0 |
| toniot | 122595 | 26370 | 47489 | 0 / 0 / 0 |
| cicids2017 | 73835 | 15740 | 35121 | 0 / 0 / 0 |
| ciciomt2024 | 209459 | 52342 | 60002 | 0 / 0 / 0 |

No flow is shared between splits on any dataset, so the conformal p-values are computed against traffic the scorer never saw.



### Flows that carry more than one family label

| dataset | flows | share | most common conflicting pair |
|---|---|---|---|
| cse2018 | 10,505 | 4.7% | dos_attacks_slowhttptest + ftp_bruteforce (10,403); brute_force_xss + sql_injection (51) |
| toniot | 75 | 0.0% | benign + scanning (70); benign + password (4) |
| cicids2017 | 0 | 0.0% | – |
| ciciomt2024 | 0 | 0.0% | – |

These are identical feature rows labelled as two different families: dataset noise, not a modelling choice. The largest group is the pair the separability audit independently flags, which is why that rotation is scored as a group.



### Calibration and test known-traffic mix (seed 13)

| dataset | total variation distance | worst family |
|---|---|---|
| cse2018 | 6.1% | ftp_bruteforce ×7.21 |
| cicids2017 | 1.4% | bot ×0.86 |
| toniot | 0.6% | ransomware ×0.96 |
| ciciomt2024 | 11.4% | recon_vulscan ×2.36 |

The exchangeability audit refuses ciciomt2024 on every seed. This table says why: its calibration and test splits do not carry the same family mix. The refusal is a property of the partition, not of any detector.



### Detectors with no seed-to-seed variation

| dataset | method | AUROC | seeds |
|---|---|---|---|
| cse2018 | EFC | 0.9837 | 5 |
| cicids2017 | EFC | 0.7982 | 5 |
| toniot | EFC | 0.5878 | 5 |

A zero interval for these rows means the method ignores the seed, not that it is stable under retraining.



### Device scorer versus the NumPy reference

| dataset | scorer | Spearman | p99 relative error | max relative error |
|---|---|---|---|---|
| cicids2017 | floored | 0.999992 | 0.063 | 0.39 |
| cicids2017 | tail_lifted | 0.999992 | 0.063 | 0.39 |
| cse2018 | floored | 0.999564 | 0.462 | 3.78 |
| cse2018 | tail_lifted | 0.999564 | 0.462 | 3.78 |

The deployment path evaluates the same statistics in float32. Ranking is preserved to Spearman ≥ 0.9996 and calibration and test flows go through the same path, so p-values stay self-consistent; individual scores can still differ by the amounts shown.
