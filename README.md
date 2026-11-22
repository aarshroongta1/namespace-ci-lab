# What does a warm dependency cache actually save in Vite CI?

An independent, small Namespace experiment by Aarsh Roongta. **Experiment in progress; no Namespace performance results yet.**

I use Vite for my portfolio. This experiment runs a slice of Vite's existing CI on a pinned public revision: dependency installation, `pnpm run build`, and `pnpm run test-unit`. It does not claim to run the complete upstream matrix or browser tests.

## The question

Does persistent dependency storage improve the developer feedback loop after a source edit, and how much time remains in rebuilding and testing?

For each provider, run three fresh CI jobs in order: cold dependency store, warm identical revision, then a source comment edit with the same lockfile. No `node_modules`, build outputs, or test results are reused. The comment edit is a controlled source-change probe, not a feature implementation.

GitHub uses `actions/cache` for the pnpm store. Namespace uses `nscloud-cache-action` with an enabled cache volume on a dedicated profile. A fresh cohort isolates the GitHub cache; a fresh dedicated Namespace profile/volume is required for another genuinely cold trial. Do not label a reused volume cold.

Both use Linux x86_64, Node 22 and pnpm 12.21.0. Hardware metadata and command exit codes are captured. Provider hardware and cache mechanisms differ; one trial is illustrative, not a statistical benchmark. Command timing excludes checkout, Node/pnpm setup, cache restore/save, artifact upload and queueing. Overall job timestamps in Actions provide those additional costs. A warm store does not imply a warm compiled build.

## Evidence

- [Pinned Vite source](https://github.com/vitejs/vite/tree/3567471998e3da315675086f44368e266c9c0e33)
- [Original CI](https://github.com/vitejs/vite/blob/3567471998e3da315675086f44368e266c9c0e33/.github/workflows/ci.yml)
- [Experiment workflow](.github/workflows/experiment.yml)
- [Measurement script](scripts/measure.py)
- Raw JSON and full command logs are attached to each Actions run; completed results will be checked into `results/`.

## Product research

Namespace provides configurable GitHub Actions runners, persistent cache volumes, remote Docker builders and interactive debugging. Its getting-started guide distinguishes the initial runner-label migration from adopting cache volumes. Cache setup is therefore part of this experiment, rather than assuming a one-line runner switch automatically persists pnpm dependencies.

Sources: [GitHub Actions guide](https://namespace.so/docs/solutions/github-actions), [cache action source](https://github.com/namespacelabs/nscloud-cache-action), [Namespace](https://namespace.so/).

## Reproduce

Dispatch `experiment.yml` with provider `github` or `namespace`, then phases `cold`, `warm`, `edited`, waiting for each to finish. Keep the cohort fixed for all three. For Namespace, first connect this repository to the Namespace Runners GitHub app and create a Linux AMD64 profile with a cache volume. Use a small comparable shape and the actual profile label. No upstream PR, secrets, or upstream workflow changes are needed.
