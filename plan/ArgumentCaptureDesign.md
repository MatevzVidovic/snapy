# Argument Capture Design

- Decorate target functions with something like `@capture()` so every live call funnels through a wrapper that logs `(args, kwargs, return)` bundles. The wrapper should live in a shared helper (e.g. `snapy/capture.py:12`) and call the original function via `functools.wraps`.
- Serialize payloads to disk with `dill` (per the note in `plan/my_features.md`) so complex objects survive round-trip. Keep the serializer behind a thin interface so you can swap formats later and add compression if captured blobs get large.
- Apply a retention policy: e.g. store files under `captures/{qualname}/timestamp.pkl` and prune to the two most recent bundles. Maintain an index JSON alongside each function to track metadata (call count, hashes) and let the decorator skip capture once the quota is met.
- For replay during snap tests, expose a loader that returns the most recent capture for a given function or a deterministic pick (e.g. by hash). Tests can then call `load_capture("module.fn")` and feed the stored arguments directly into the function under test, or assert that the stored return matches the current output.
- Guard the capture path with an environment toggle (`SNAPY_CAPTURE_ENABLED=1`) so production runs without capture overhead unless explicitly enabled. Consider thread/process safety: use file locks or atomic rename when writing capture files to prevent corruption under concurrent calls.
- Capture failures should fail gracefully: log and move on so production traffic is unaffected.
- Add a CLI or simple viewer to inspect stored captures, diff them, and clear old ones.
- When wrapping functions that already use decorators, ensure order doesn’t interfere (your decorator should be outermost so it sees the true call arguments).



Plan:
- capture handler nima vec init. Raje ima povsod base_path kot argument svojih metod
- prilagoditev da stvari drugje za to v redu delajo
- v test_syrupy naredit mock metode, ki shranjujejo v path alla:   
poimenovanje shranjevanja je tako:
module path / test fn name / wrapper_fn name / (če je to snap test) pickle file name / hash
Tako v snap testih iščemo enake argumente samo za trenutni pickle name, torej veliko manj za preverit
- In imamo max allowed float("inf)
- v plus_mock imamo potem fn plus_wrapper ki ima v sebi potem plus().
In če je plus_wrapper že imel take argumente (vidimo v capture load) potem samo returnamo to.
Če še ni imel, poženemo plus wrapper (na njim je @capture torej se bo zdaj shranilo).
- V testu imamo pogledamo za dotenv spremenljivko SIDE_EFFECT_CAPTURE=True.
Če je ta false ali none, in ne najdemo matching signaturea v loaded captures, damo Exception.
Ko poganjamo snapshot update, naredimo:
SIDE_EFFECT_CAPTURE=True pytest --snapshot-update

ZAPIŠI - with snap capture you could be capturing from production/staging env.
But there, objects might be humongus (like huge ML models).
We suggest you build a testing env, that essentially a staging env, where you make sure all objects are as small as possible.
This will make storing these tests much much more managable.
If sth cannot be made small, maybe exclude it from capture (this feature needs to be added)
and recreate as close as a faximile as you can manually in the test code.