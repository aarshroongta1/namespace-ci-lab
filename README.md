# pandas CI on Namespace: diagnosed and fixed

**[Open the interactive demo](https://www.aarshroongta.com/demo/namespace)**

A pandas runner migration initially restored its cache but missed most compiler entries. I traced the mismatch to `LC_ALL`, verified a one-line fix, and reran the same source build and 4,045 groupby tests.

| Configuration | Dispatch to passing checks | Source build | Compiler-cache hits |
|---|---:|---:|---:|
| GitHub | 126s | 34.81s | 59/59 |
| Namespace unchanged | 225s | 157.18s | 3/59 |
| Namespace with LC_ALL unset | 80s | 24.38s | 59/59 |

All three passed 4,045 tests, with 2 skipped. These are three jobs from one shared dispatch, using the same original archive, source edit, compiler, dependency lockfile, build/test commands, and 4-vCPU/16-GB Linux shape.

## What was wrong

GitHub had `LANG=C.UTF-8` with `LC_ALL` unset. The Namespace runner used here also had `LC_ALL=C.UTF-8`. Ccache hashes locale variables, so the extra field changed the key despite the same effective locale.

Compiler/header manifests checked matched. The representative ccache COMMON and DIRECT input text becomes identical after removing the extra `LC_ALL` field. Unsetting it then restored all 59 cacheable calls from the same immutable GitHub archive.

```sh
env -u LC_ALL python3 scripts/measure_pandas.py
```

The slow result was a migration environment mismatch, not evidence of slow Namespace compute. A cache archive restoring successfully did not establish effective compiler-cache reuse.

## Evidence and verification

- [Diagnosis and suggestion for Namespace](INVESTIGATION.md)
- [Controlled timing results and CI job links](LOCALE_RESULTS.md)
- [Ccache input comparison](results/cache-diagnosis/comparison.txt)
- [Diagnostic workflow](.github/workflows/cache-diagnosis.yml)
- [Fix-verification workflow](.github/workflows/pandas-locale.yml)
- [Compiler-cache regression check](scripts/assert_compiler_reuse.py), which rejects the unchanged 3/59 result and accepts the fixed 59/59 result

## Product feedback

Document this ccache migration case, including `LANG` and `LC_ALL`. For the Ubuntu runner used here, check whether the default locale environment can match GitHub's. Otherwise include the normalization step when bringing an existing compiler cache. The fix retains ccache validation; it does not ignore cache inputs.

This targets the customer outcome emphasized in [Framer's CI story](https://namespace.so/customers/framer) and [DuckDB's PR-validation story](https://namespace.so/customers/duckdb): shorter developer feedback loops while retaining GitHub Actions.

## Scope

One bounded pandas contributor job, not its full upstream CI matrix. The same small Python helper rename was applied to each checkout. Two compiler processes and two pytest workers were used. Every runner, checkout, environment prefix, and build directory was fresh; only cached data persisted.

One timing trial per configuration on different underlying hardware. Compiler-input evidence, a reproduced negative control, and full hit restoration verify the cause. Timing differences also include startup, checkout, installation, and post-job work. Diagnostic logging was disabled in the verification timing run.

Earlier migration and Cache Volume trials remain in [MIGRATION_RESULTS.md](MIGRATION_RESULTS.md), [PANDAS_RESULTS.md](PANDAS_RESULTS.md), and the results directory. The locale investigation resolves the previously unexplained runner-only compiler misses. No upstream PR, issue, or external message was sent.

## Demo

The buildless UI is in `demo/`, copied to the portfolio's `public/namespace-ci/` directory. `scripts/collect_locale_verification.py RUN_ID` collects evidence and exports `demo/verification.json`. The page replays recorded results and makes no live CI requests.
