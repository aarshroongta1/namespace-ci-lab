# pandas CI on Namespace

A small, reproducible experiment: **how much of a pandas contributor's build-and-test loop can persistent caches remove?**

**Status:** Complete. See [the experiment note](README.md) and [measured results](PANDAS_RESULTS.md).

## Why pandas

pandas is a widely used Python library with Python, Cython, and C/C++ sources. Its CI builds pandas from source in a locked Pixi environment and runs pytest. This experiment follows that structure, narrowing the tests to groupby reductions and general groupby behavior so the work fits in one sitting.

## The experiment

Each phase starts on a fresh Linux x86_64 runner, with a fresh source checkout and environment prefix:

| Phase | Source | Reused data |
|---|---|---|
| Cold | Pinned upstream revision | Empty experiment cache |
| Warm | Identical revision | Downloaded Pixi packages and ccache compiler outputs |
| Edited | Rename a local helper in `GroupBy.prod` | Same caches; fresh build directory |

The edit renames `prod_compat` to `product_compat` without changing behavior. It is a small Python refactor, **not a native-source edit or a bug fix**. Its patch is preserved with the run evidence. Native build directories, installed environments, and test results are never cached.

Both providers run the same pinned pandas source and Pixi lockfile, the same Python 3.12 environment, two compiler processes, and two pytest workers. GitHub stores the experiment cache with `actions/cache`; Namespace attaches it with `nscloud-cache-action` to a cache-enabled profile. This compares realistic caching configurations, not hardware in isolation.

## Results and evidence

Pandas results are in [PANDAS_RESULTS.md](PANDAS_RESULTS.md). Raw logs, compiler-cache statistics, package versions, JUnit test results, patches, and JSON timings live in [`results/pandas/`](results/pandas/) and in each run's artifact.

- [Run the experiment / inspect Actions](https://github.com/aarshroongta1/namespace-ci-lab/actions/workflows/pandas.yml)
- [Workflow](.github/workflows/pandas.yml)
- [Measurement script](scripts/measure_pandas.py)
- [Pinned pandas source](https://github.com/pandas-dev/pandas/tree/717bcd3eda554a0b2e826889f9e30efbd88f00cd)
- [Upstream CI](https://github.com/pandas-dev/pandas/blob/717bcd3eda554a0b2e826889f9e30efbd88f00cd/.github/workflows/unit-tests.yml)
- [Upstream build task](https://github.com/pandas-dev/pandas/blob/717bcd3eda554a0b2e826889f9e30efbd88f00cd/pixi.toml)

## What counts as a useful finding

A faster warm build is only part of the story. We report environment creation, compilation, tests, cache attachment/transfer, and whole-job duration separately. A cache hit that costs more to restore than it saves is relevant feedback too. We will inspect ccache hit statistics before attributing an improvement to compiler caching.

Namespace's documentation distinguishes changing the runner label from adopting cache volumes. This experiment explicitly configures persistent caches rather than assuming the runner migration does that automatically. Sources: [runner setup](https://namespace.so/docs/solutions/github-actions), [cache action](https://github.com/namespacelabs/nscloud-cache-action).

## Scope and limitations

This is one bounded contributor-workflow experiment, not the complete pandas CI matrix. It omits database service containers, coverage reporting, multiple Python versions, and unrelated tests. It keeps the upstream `py312` environment and underlying editable Meson build command, adds ccache, limits compiler parallelism, and selects two existing test files. Provider hardware differences are recorded, and one run per phase cannot establish statistically reliable performance claims. No package is published and no upstream repository is changed.

## Reproduce

Connect this repository to Namespace's GitHub app, then create a Linux AMD64 profile with cache volumes enabled. Dispatch `pandas.yml` for `github` or `namespace`, in order `cold`, `warm`, `edited`, waiting for each run to complete. Pass the actual Namespace profile label. Keep the cohort fixed across phases; use a new cohort for an independent cold trial. A cold run fails if it finds existing experiment cache files.

Earlier Vite feasibility measurements remain in the root of `results/` and `RESULTS.md`. They are separate from the pandas experiment.
