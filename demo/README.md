# Visual CI replay

Public demo: https://www.aarshroongta.com/demo/namespace

The four buildless files here are copied into the portfolio's `public/namespace-ci/` directory. Vercel rewrites `/demo/namespace` to `namespace-ci/index.html`.

`python3 scripts/export_demo.py` rebuilds data.json from the actual run JSON, job metadata, JUnit results, and compiler-cache logs. Setup and finish combine GitHub job timestamps with the measured command durations. Timelines are reconstructed stage summaries, not a trace of individual compiler events.

Replay runs on a 12-second compressed timescale. Pause, scrub, skip to the result, inspect stages, or choose a different scenario. Reduced-motion users see final results. There are no live CI requests or paid calls.
