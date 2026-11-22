I tried Namespace on a small slice of pandas CI: a source build and 4,045 groupby tests. With populated caches, the builds were almost identical at ~32 seconds, but the whole jobs took 76 seconds on Namespace versus 131 on GitHub. The setup/cache overhead was the interesting part.

I also hit an onboarding cache miss on the first repeat and added a cache-hit guard rather than assuming the second run was warm. A more prominent cache-state summary could make that first experience clearer. I wrote up the small experiment with the workflow and raw runs here: https://github.com/aarshroongta1/namespace-ci-lab

I'm interested in a summer engineering internship and would love to help build tools like this.
