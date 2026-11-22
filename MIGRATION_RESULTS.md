# pandas: controlled runner migration comparison

All three configurations ran in one workflow dispatch, with the same source edit, build, tests, and dependency lockfile.

| Configuration | Wait to start | Job runtime | Dispatch to passing result | Build | Cache restore/attach | Compiler hits | Tests |
|---|---:|---:|---:|---:|---:|---:|---|
| [GitHub](https://github.com/aarshroongta1/namespace-ci-lab/actions/runs/45062565507/job/137331519171) | 5s | 137s | 142s | 43.56s | 23s | 59/59 | 4,045 passed |
| [Namespace runner](https://github.com/aarshroongta1/namespace-ci-lab/actions/runs/45062565507/job/137331518970) | 13s | 235s | 248s | 175.39s | 22s | 3/59 | 4,045 passed |
| [Namespace with Cache Volume](https://github.com/aarshroongta1/namespace-ci-lab/actions/runs/45062565507/job/137331519246) | 13s | 85s | 98s | 35.71s | 0s | 59/59 | 4,045 passed |

The first comparison changes the runner while retaining actions/cache. The second changes to Namespace Cache Volumes on the same Namespace runner profile. The existing archive was populated on GitHub; the Cache Volume was populated by earlier Namespace builds. Restored data does not imply reusable compiler outputs: the runner-only migration hit just 3/59 calls. The reason for those mismatches was not isolated. Do not attribute the runner-only/volume gap solely to storage speed. One run per configuration, not a broad benchmark. No upstream PR was opened.
