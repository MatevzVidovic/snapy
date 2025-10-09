# Argument Capture Design

- Decorate target functions with something like `@capture_args()` so every live call funnels through a wrapper that logs `(args, kwargs, return)` bundles. The wrapper should live in a shared helper (e.g. `snapy/capture.py:12`) and call the original function via `functools.wraps`.
- Serialize payloads to disk with `dill` (per the note in `plan/my_features.md`) so complex objects survive round-trip. Keep the serializer behind a thin interface so you can swap formats later and add compression if captured blobs get large.
- Apply a retention policy: e.g. store files under `captures/{qualname}/timestamp.pkl` and prune to the two most recent bundles. Maintain an index JSON alongside each function to track metadata (call count, hashes) and let the decorator skip capture once the quota is met.
- For replay during snap tests, expose a loader that returns the most recent capture for a given function or a deterministic pick (e.g. by hash). Tests can then call `load_capture("module.fn")` and feed the stored arguments directly into the function under test, or assert that the stored return matches the current output.
- Guard the capture path with an environment toggle (`SNAPY_CAPTURE=1`) so production runs without capture overhead unless explicitly enabled. Consider thread/process safety: use file locks or atomic rename when writing capture files to prevent corruption under concurrent calls.
- Capture failures should fail gracefully: log and move on so production traffic is unaffected.
- Add a CLI or simple viewer to inspect stored captures, diff them, and clear old ones.
- When wrapping functions that already use decorators, ensure order doesn’t interfere (your decorator should be outermost so it sees the true call arguments).
