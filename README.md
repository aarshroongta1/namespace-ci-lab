# pandas CI migration to Namespace

**[Open the interactive demo](https://www.aarshroongta.com/demo/namespace)**

This experiment asks how quickly a contributor gets passing checks after a small pandas source edit, and separates changing the runner from adopting Namespace Cache Volumes.

The motivation comes from Namespace's [GitHub Actions product](https://namespace.so/github-actions) and its customer stories: [Framer](https://namespace.so/customers/framer) focuses on keeping CI short enough to preserve developer focus, while [DuckDB](https://namespace.so/customers/duckdb) measures pull-request validation time and values visibility into bottlenecks.

## One workflow, three configurations

Each configuration built the same pinned pandas source and ran the same 4,045 groupby tests. All passed, with 2 skipped. The build/test commands, dependency lockfile, two compiler workers, two pytest workers, and 4-vCPU/16-GB Linux shape stayed the same.

| Configuration | Dispatch to successful completion | Compiler-cache hits |
|---|---:|---:|
| GitHub with its existing archive | 142s | 59/59 |
| Namespace runner with the same archive | 248s | 3/59 |
| Namespace with a populated Cache Volume | 98s | 59/59 |

[Results and job links](MIGRATION_RESULTS.md) · [Workflow](.github/workflows/pandas-migration.yml) · [Raw evidence](results/pandas-migration/)

## Findings

The runner-only migration passed without changing the build or tests. Its restored archive, however, mostly failed to produce compiler-cache hits and the job recompiled native code. I did not isolate why those entries did not match.

With a Cache Volume already populated by previous Namespace builds, the checks completed 44 seconds sooner than the GitHub baseline. Both cases hit all 59 cacheable compiler calls. The difference includes cache handling, runner startup, checkout, and tool installation.

A restored cache and an effective compiler cache are different things. The demo exposes compiler hit counts alongside the time to passing checks and shows the runner and cache workflow changes separately.

## Scope

One trial per configuration, launched from one workflow dispatch, on different underlying hardware. This is one bounded contributor job, not pandas' complete CI matrix. The volume was warmed on Namespace; the archive was warmed on GitHub. The 248s-to-98s comparison is therefore not a pure storage-speed comparison. No cost, concurrency, or reliability conclusions are drawn.

Each runner, environment prefix and build directory was fresh. Only cached packages and compiler outputs persisted. Timelines combine measured command durations with GitHub timestamps, including dispatch/scheduling and post-job work.

The source edit is a behavior-preserving helper rename in `GroupBy.prod`; it does not change native code. No upstream PR was opened. Earlier cold/warm trials are retained in [PANDAS_RESULTS.md](PANDAS_RESULTS.md) and `results/pandas/` as preliminary evidence.

## Demo source

The buildless UI is in [demo/](demo/). `scripts/collect_migration.py RUN_ID` collects the job evidence and exports `demo/migration.json`. Portfolio deployment copies the files to `public/namespace-ci/` and serves `/demo/namespace`.
