# pandas: measured CI results

| Runner | Phase | Environment (s) | Build (s) | Tests (s) | Cache attach/restore (s) | Whole job (s) | Test result | Evidence |
|---|---|---:|---:|---:|---:|---:|---|---|
| github | cold | 15.87 | 202.28 | 9.72 | 0 | 299 | 4045 passed / 2 skipped | [run](https://github.com/aarshroongta1/namespace-ci-lab/actions/runs/45055495476) |
| github | warm | 1.99 | 32.97 | 9.46 | 23 | 131 | 4045 passed / 2 skipped | [run](https://github.com/aarshroongta1/namespace-ci-lab/actions/runs/45056009608) |
| github | edited | 5.56 | 36.07 | 10.02 | 26 | 143 | 4045 passed / 2 skipped | [run](https://github.com/aarshroongta1/namespace-ci-lab/actions/runs/45056240043) |
| namespace | cold | 13.94 | 169.90 | 6.81 | 0 | 217 | 4045 passed / 2 skipped | [run](https://github.com/aarshroongta1/namespace-ci-lab/actions/runs/45055498946) |
| namespace | warm requested; cache MISS | 12.50 | 166.45 | 6.66 | 0 | 208 | 4045 passed / 2 skipped | [run](https://github.com/aarshroongta1/namespace-ci-lab/actions/runs/45055882874) |
| namespace | warm | 8.92 | 32.09 | 8.23 | 0 | 76 | 4045 passed / 2 skipped | [run](https://github.com/aarshroongta1/namespace-ci-lab/actions/runs/45056383722) |
| namespace | edited | 7.77 | 24.22 | 6.71 | 0 | 62 | 4045 passed / 2 skipped | [run](https://github.com/aarshroongta1/namespace-ci-lab/actions/runs/45056617810) |

Only successful trials appear in this table. Raw evidence is in [results/pandas](results/pandas/). Failed setup attempts, if downloaded, are preserved separately.

Whole-job time includes setup, package installation, evidence upload and post-job cache handling; it is not just build time. Cache times come from GitHub step timestamps at one-second resolution. These are individual trials, not a statistical benchmark. The edited phase is a behavior-preserving Python helper rename, not a Cython or C++ change.
