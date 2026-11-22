# pandas: measured CI results

| Runner | Phase | Environment (s) | Build (s) | Tests (s) | Cache attach/restore (s) | Whole job (s) | Test result | Evidence |
|---|---|---:|---:|---:|---:|---:|---|---|
| namespace | cold | 13.94 | 169.90 | 6.81 | 0 | 217 | 4045 passed / 2 skipped | [run](https://github.com/aarshroongta1/namespace-ci-lab/actions/runs/45055498946) |

Only successful trials appear in this table. Raw evidence is in [results/pandas](results/pandas/). Failed setup attempts, if downloaded, are preserved separately.

Whole-job time includes setup, package installation, evidence upload and post-job cache handling; it is not just build time. Cache times come from GitHub step timestamps at one-second resolution. These are individual trials, not a statistical benchmark. The edited phase is a behavior-preserving Python helper rename, not a Cython or C++ change.
