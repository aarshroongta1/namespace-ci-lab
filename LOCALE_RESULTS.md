# pandas CI: GitHub vs Namespace

Same source, dependencies, build, tests, and cache archive. Both runners used 4 vCPUs and 16 GB RAM.

| Configuration | Wait to start | Job runtime | Dispatch to passing result | Build | Cache restore/attach | Compiler hits | Tests |
|---|---:|---:|---:|---:|---:|---:|---|
| [GitHub](https://github.com/aarshroongta1/namespace-ci-lab/actions/runs/45065516592/job/137340663437) | 4s | 122s | 126s | 34.81s | 17s | 59/59 | 4,045 passed |
| [Namespace](https://github.com/aarshroongta1/namespace-ci-lab/actions/runs/45065516592/job/137340663130) | 3s | 77s | 80s | 24.38s | 20s | 59/59 | 4,045 passed |

Both jobs passed 4,045 tests, with 2 skipped. Namespace used `env -u LC_ALL` to match GitHub’s locale environment and reuse the compiler cache. Debug logging was off. One timing trial per configuration; times include startup and cleanup.

The original dispatch also included a cache-mismatch diagnostic control. Its results remain in [the investigation](INVESTIGATION.md) and raw evidence. Historical GitHub Actions job names cannot be renamed.
