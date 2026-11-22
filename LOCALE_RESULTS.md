# pandas: verifying the compiler-cache locale fix

All three configurations ran in one dispatch with the same original GitHub archive, source edit, build, tests, and dependency lockfile. Namespace fixed differs from Namespace default only by running the measurement script with LC_ALL removed from its environment.

| Configuration | Wait to start | Job runtime | Dispatch to passing result | Build | Cache restore/attach | Compiler hits | Tests |
|---|---:|---:|---:|---:|---:|---:|---|
| [GitHub](https://github.com/aarshroongta1/namespace-ci-lab/actions/runs/45065516592/job/137340663437) | 4s | 122s | 126s | 34.81s | 17s | 59/59 | 4,045 passed |
| [Namespace default](https://github.com/aarshroongta1/namespace-ci-lab/actions/runs/45065516592/job/137340663345) | 12s | 213s | 225s | 157.18s | 21s | 3/59 | 4,045 passed |
| [Namespace fixed](https://github.com/aarshroongta1/namespace-ci-lab/actions/runs/45065516592/job/137340663130) | 3s | 77s | 80s | 24.38s | 20s | 59/59 | 4,045 passed |

All three jobs restore the same immutable archive. The only treatment between the two Namespace jobs is env -u LC_ALL. Both retain LANG=C.UTF-8. Compiler/input tracing found the extra LC_ALL field in Namespace cache keys; the headers and compiler files checked matched. Debug instrumentation was disabled for this timing run. One timing trial per configuration; ccache-input evidence and the negative-control regression check provide the causal verification.
