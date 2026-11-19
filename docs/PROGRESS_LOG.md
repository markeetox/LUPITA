

## 2026-11-19 | Pinned wodpy installation succeeded; NOAA source delivery returned HTTP 503

Dispatched actual-parser workflow [44531684748](https://github.com/markeetox/LUPITA/actions/runs/44531684748). GitHub Actions successfully installed the exact IQuOD wodpy commit 116480b257a227ce38281d3836c40812246e5156 (wodpy==2.0.0b0; built wheel SHA-256 7840471d8d867da54d5fbc53eb9fe374320b0588f0f103c704d93f4f3ce12763). The NOAA GLD download step then received HTTP 503 on every retry. The ETOPO download, actual package parser run, full join, and comparison were skipped. This is not parser parity and produced no scientific join result.

The NCEI Alerts page reports broader data-access delays through Nov 30 during its cloud migration, including intermittent degraded order fulfillment; this is consistent with the observed failure but does not establish its specific cause. Sources: https://www.ncei.noaa.gov/alerts and https://www.ncei.noaa.gov/access.

Next: retry the exact original WODSelect GLD archive after NCEI recovery, verify its expected SHA-256 c75b110c4eba09c0a55aed34cf31d12f2693d3053fad09216d2794ff370fb0e3, then run the exact pinned parser and compare every cast/level to the preliminary join. Do not substitute another dataset or call the preliminary transcription verified. No production behavior changed.


## 2026-11-19 | Actual parser runner installed pinned wodpy; NOAA file transfer blocked

GitHub Actions successfully installed IQuOD `wodpy` at commit `116480b257a227ce38281d3836c40812246e5156` in actual-run [44531684748](https://github.com/markeetox/LUPITA/actions/runs/44531684748), but the NCEI WODSelect output URL returned HTTP 503 on repeated attempts. The run did not reach the ETOPO download or actual GLD parsing stages. This is a transfer/service failure, not a parser failure, and does not establish that the WODSelect file expired.

Created temporary branch `research-wod-gld-input-20261119` with a branch-specific workflow that will run automatically when the original GLD gzip is uploaded to `research-inputs/ocldb1794949360.1820758.GLD.gz`. The workflow validates the uploaded file against its known SHA-256 before parsing. Upload page: `https://github.com/markeetox/LUPITA/upload/research-wod-gld-input-20261119/research-inputs`. After the workflow completes, download artifact `wod-gld-actual-parser-parity`, compare actual output to the preliminary local join, and delete the temporary branch. Main workflow is manual-only; no production changes.
