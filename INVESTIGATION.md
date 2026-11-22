# Why the initial Namespace runner migration missed the compiler cache

## Symptom

The original runner-only migration restored the GitHub cache archive but hit only 3 of 59 cacheable compiler calls. Most native code recompiled, and passing checks took 248 seconds in that trial.

## Root cause

GitHub's compiler process had `LANG=C.UTF-8` and no `LC_ALL`. The Namespace runner used here had `LANG=C.UTF-8` and `LC_ALL=C.UTF-8`.

Ccache 4.9.1 hashes locale variables because they affect localized compiler warnings. The extra `LC_ALL` field changed the cache key even though the effective locale was the same. This was an environment compatibility issue, not evidence of slower Namespace compute.

[Official ccache documentation](https://ccache.dev/manual/4.9.1.html#config_sloppiness) · [Debug workflow](.github/workflows/cache-diagnosis.yml)

## Evidence

- [GitHub compiler input](results/cache-diagnosis/github-debug/base.ccache-input-text)
- [Namespace compiler input](results/cache-diagnosis/namespace-debug/base.ccache-input-text)
- [Input and header comparison](results/cache-diagnosis/comparison.txt)
- Compiler file hashes, sizes and modification times matched. The Python/NumPy header and selected system-header manifests checked also matched.
- The representative COMMON and DIRECT ccache input text becomes identical when the extra `LC_ALL` entry is removed. The source-code hash also matches.

The original archive was immutable: the migration hit its primary GitHub cache key, so actions/cache skipped saving the newly compiled Namespace results. Rerunning that configuration would keep restoring the old entries. [Cache action behavior](https://github.com/actions/cache#usage)

## Fix and causal verification

Run the same build/test script with the redundant override removed:

```sh
env -u LC_ALL python3 scripts/measure_pandas.py
```

`LANG=C.UTF-8` remains set. No cache validation is disabled, and no dependencies, compiler, source edit, tests, or archive key change.

A control dispatch ran GitHub, unchanged Namespace, and fixed Namespace against the same original archive. Diagnostic logging was off for these timings:

| Configuration | Dispatch to passing checks | Source build | Compiler-cache hits |
|---|---:|---:|---:|
| GitHub | 126s | 34.81s | 59/59 |
| Namespace unchanged | 225s | 157.18s | 3/59 |
| Namespace with LC_ALL unset | 80s | 24.38s | 59/59 |

All passed 4,045 tests, with 2 skipped. [Job links and complete timings](LOCALE_RESULTS.md)

## Regression check

`scripts/assert_compiler_reuse.py` rejects the unchanged diagnostic statistics (3/59) and accepts the fixed statistics (59/59). The verification workflow now checks that full compiler-cache reuse remains intact.

This distinguishes restoring an archive successfully from reusing its compiler outputs successfully. The controlled before/after cache-hit result verifies the cause; one timing trial per configuration illustrates the performance impact without establishing a broad benchmark.

## Suggestion for Namespace

Add a ccache migration note showing that locale variables affect cache keys. Check whether the Ubuntu runner's default locale environment can match GitHub's; otherwise show the normalization step when users bring an existing compiler cache. Recommend checking compiler hit statistics in addition to the cache action's restore status.

No issue or external message has been sent. Earlier Cache Volume results remain available in the repository; this investigation isolates the runner-migration issue.
