# pandas CI on Namespace

[Demo](https://www.aarshroongta.com/demo/namespace)

Build pandas from source and run 4,045 groupby tests.

| Runner | Time to passing CI | Build | Compiler-cache hits |
|---|---:|---:|---:|
| GitHub | 126s | 34.81s | 59/59 |
| Namespace | 80s | 24.38s | 59/59 |

Both passed 4,045 tests, with 2 skipped. Same source, dependencies, commands, cache archive, and 4-vCPU/16-GB runner size. Times include startup and cleanup.

## Method

pandas `717bcd3`, Python 3.12, locked Pixi environment, editable Meson build. Two compiler processes and two test workers. Each job used a fresh runner. The same small Python helper rename was applied to both checkouts.

Namespace used `env -u LC_ALL` to match GitHub’s locale environment and reuse the compiler cache. [Cache diagnosis](INVESTIGATION.md).

One trial per configuration on different underlying hardware. This compares runners using an archive cache; it does not measure Namespace Cache Volumes or isolate hardware performance.

## Evidence

- [Results and CI jobs](LOCALE_RESULTS.md)
- [Workflow](.github/workflows/pandas-locale.yml)
- [Raw results](results/locale-verification)

Earlier diagnostic controls and Cache Volume trials remain in the results directory, [INVESTIGATION.md](INVESTIGATION.md), [MIGRATION_RESULTS.md](MIGRATION_RESULTS.md), and [PANDAS_RESULTS.md](PANDAS_RESULTS.md).

## Demo source

`demo/` contains the page and recorded timings. `scripts/collect_locale_verification.py RUN_ID` collects the comparison. The page makes no live CI requests.
