

## Actual pinned parser attempt blocked by NCEI delivery outage | 2026-11-19

GitHub Actions run [44531684748](https://github.com/markeetox/LUPITA/actions/runs/44531684748) successfully checked out the repository and installed the exact pinned IQuOD wodpy commit 116480b257a227ce38281d3836c40812246e5156 (package wodpy==2.0.0b0, wheel SHA-256 7840471d8d867da54d5fbc53eb9fe374320b0588f0f103c704d93f4f3ce12763). The run failed at the NOAA WODSelect GLD download: NCEI returned HTTP 503 on all retry attempts. Consequently the ETOPO artifact download, actual parsing, join, and comparison steps were skipped. No parser parity result exists yet.

NCEI's public Alerts page currently reports WODSelect performance issues (Nov 5–7, 2026) and broader data-access delays through Nov 30 associated with its cloud migration, including intermittent degraded order-fulfillment services. This is consistent with the observed service-side failure but does not prove the specific cause of this 503. Sources: https://www.ncei.noaa.gov/alerts and https://www.ncei.noaa.gov/access.

Next: retry the same exact GLD download after NCEI service recovery, preserving the expected source SHA-256 c75b110c4eba09c0a55aed34cf31d12f2693d3053fad09216d2794ff370fb0e3. Do not replace the requested GLD archive with a different dataset or accept the preliminary parser transcription as parity. The pinned parser installation is now verified; the real archive execution remains blocked solely at source delivery. No production behavior changed.


## Actual parser run: package installed; NOAA output endpoint unavailable from runner | 2026-11-19

The first actual-run attempt, [run 44531684748](https://github.com/markeetox/LUPITA/actions/runs/44531684748), installed the exact pinned IQuOD `wodpy` commit successfully, but NOAA's WODSelect output URL returned HTTP 503 on all download retries. A second attempt confirmed the same response. This does not prove the file expired; the user-submitted WODSelect files were still within the stated 72-hour availability window at the time. The actual GLD archive remains available in the ChatGPT working upload, but the GitHub runner cannot directly access that session-local file.

Prepared a controlled fallback branch `research-wod-gld-input-20261119` from `main`. Its workflow copy listens only for the original GLD gzip being uploaded to `research-inputs/ocldb1794949360.1820758.GLD.gz`, then verifies the expected source SHA-256 `c75b110c4eba09c0a55aed34cf31d12f2693d3053fad09216d2794ff370fb0e3`, downloads the exact ETOPO artifact, runs the installed pinned parser, and uploads the join output. The branch is temporary and must be deleted after the run and results are captured. Upload page: `https://github.com/markeetox/LUPITA/upload/research-wod-gld-input-20261119/research-inputs`.

The `main` workflow remains manual-only; no production data or prediction behavior changed. Full parser parity remains pending until the original archive is available to the GitHub runner and the resulting CSV can be compared with the preliminary local join.
