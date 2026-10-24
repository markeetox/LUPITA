# Brief for Jules: add the Fish Forecast filter to Seabound

Read this whole file first. It explains where the data is, how it gets there, exactly what the app should fetch, and what to build.
Everything below was checked against the real published files (section 9 shows how to re-check).

---

## 1. What this is, in plain words

A separate project (repo `markeetox/lupita`) predicts, every hour, **where and when 8 fish species are likely to be biting off South Florida**
(mahi-mahi, sailfish, wahoo, yellowtail snapper, mutton snapper, cobia, snook, tarpon). It combines NOAA and NASA ocean data, tides,
moon, cold fronts, depth and reef maps, and published fish habitat research.

That project writes its results as **plain files on the internet** (JSON and PNG). **Seabound does not call a server and does not
compute anything.** It only downloads those files and shows them: a fish filter, a heat layer on the map, areas to tap, and a details
sheet with the fish's picture, description and best time of day.

## 2. Where everything lives (read this carefully)

| Question | Answer |
|---|---|
| Repo | `https://github.com/markeetox/lupita` (renamed from `here-fishy-fishy`; the old name still redirects, but use `lupita`) |
| Which branch holds the data? | **`data`** (NOT `main`). `main` holds the code. If you open the repo you land on `main`, where there is no `api/` folder. Switch the branch dropdown to `data`. |
| Folder inside that branch | `api/v1/` |
| **Base URL the app must use** | `https://raw.githubusercontent.com/markeetox/lupita/data/api/v1/` |
| Production later | `https://markeetox.github.io/lupita/api/v1/` (GitHub Pages; same files, a faster CDN). Not switched on yet. |

**Put the base URL in exactly one constant/config value.** Every link inside the files is *relative to the base URL*, so changing hosts
later means changing that one value.

The `data` branch also has other files at its top level (`fish.json`, `heat.json`, `latest.json`, ...). **Those are internal and may change
without notice. Only ever read things under `api/v1/`.**

## 3. How the files get there (so you understand what the app can and cannot expect)

```
NOAA / NASA / FWC data
        |
        v
GitHub Action "Pull ocean data"  (runs automatically every hour, using the code on the `main` branch)
        |  downloads data, scores every fish, draws the heat pictures
        v
writes files into the `data` branch under api/v1/
        |
        v
Seabound  --- HTTP GET only --->  raw.githubusercontent.com/markeetox/lupita/data/api/v1/...
```

Consequences:
- It is **static files**: read-only, no login, no API key, GET requests only. Nothing the app does can change them.
- Files are **refreshed about once an hour**. The CDN caches for about 5 minutes. Polling more often than every 15 minutes is pointless.
- If the hourly job fails, **the old files stay in place** (so the app keeps working) but they get old. Every file has `generated_utc`;
  the app must show how old the data is (rule 3 in section 6).

## 4. What the app does, step by step

1. **GET `index.json`** (about 4 KB). This lists the fish and today's overall conditions.
2. Build the **fish filter** from `index.json -> species[]` (do not hard-code the list: new fish will appear here automatically).
   Each entry gives `id`, `name`, `color`, `image.url`, `status`, `message`, `area_count`.
3. User picks a fish. **GET `species/<id>.json`** (a few KB).
4. **Draw the heat layer:** if `heat` is not null, show the picture `heat/<id>.png` on the map covering `heat.bounds`
   (`[west, south, east, north]`). It is already coloured and transparent: do not recolour it.
5. **Draw the areas:** one marker per `today.areas[]` at `coords` (`[longitude, latitude]`), optionally the outline from `zone` (GeoJSON).
6. User taps an area -> **details sheet**: fish picture, name, score, reasons, best bite window, details rows, about the fish.
7. Somewhere reachable (info screen): `disclaimer`, `attribution` and "updated N minutes ago".

Optional layers from the same API: `closures.json` (no-fishing zones, GeoJSON) and `stream.json` (Gulf Stream edge line, GeoJSON).

## 5. File reference, with real examples

All paths are relative to `https://raw.githubusercontent.com/markeetox/lupita/data/api/v1/`.

| Path | What |
|---|---|
| `index.json` | Start here |
| `species/<id>.json` | One fish: description + today's areas |
| `heat/<id>.png` | Transparent heat overlay picture (about 200 KB). Only for fish with a heat layer. |
| `heat/<id>.json` | Same data as raw numbers (optional) |
| `img/<id>.png` | The fish picture, transparent PNG |
| `closures.json`, `stream.json` | Optional GeoJSON layers |

Fish ids: `mahi-mahi`, `sailfish`, `wahoo`, `yellowtail-snapper`, `mutton-snapper`, `cobia`, `snook`, `tarpon`. (The `img/` folder can contain
extra pictures for fish that are not in `index.json`. Ignore them: use only the URLs that `index.json` gives you.)

### index.json (real, trimmed)
```json
{
  "api_version": 1,
  "generated_utc": "2026-10-23T18:15:25.128403+00:00",
  "experimental": true,
  "disclaimer": "Experimental. Scores show where conditions match published habitat preferences and have not been checked ag...",
  "region": {
    "name": "south_florida",
    "bounds": [
      -81.01,
      24.49,
      "..."
    ]
  },
  "conditions": {
    "moon": {
      "illumination": 0.967,
      "phase": "waxing gibbous",
      "text": "97% lit, waxing gibbous; full moon in 2 days"
    },
    "front": {
      "state": "none",
      "source": null,
      "time": null,
      "text": null
    },
    "sea": {
      "now": {
        "level": "fair",
        "label": "Fair",
        "wind_kn": 5.1,
        "wave_ft": 2.6,
        "text": "Fair: NE wind 5 kn, waves 3 ft at 14 s (Virginia Key, FL, 4 km away; waves: Hollywood Beach, FL, 28 km away)",
        "missing": []
      },
      "outlook": {
        "level": "fair",
        "max_wind_kn": 17,
        "at": "2026-10-24T17:00:00+00:00",
        "text": "Forecast: winds up to 17 kn from the NE around 1:00 PM (fair for most boats)"
      }
    }
  },
  "species": [
    {
      "id": "cobia",
      "name": "Cobia",
      "scientific_name": "Rachycentron canadum",
      "color": "#c084fc",
      "image": {
        "url": "img/cobia.png",
        "kind": "illustration",
        "credit": "Original illustration",
        "license": ""
      },
      "status": "ok",
      "message": "",
      "area_count": 20,
      "has_timing": false,
      "heat": {
        "png": "heat/cobia.png",
        "bounds": [
          -81.01,
          24.49,
          "..."
        ]
      },
      "details": "species/cobia.json"
    }
  ],
  "layers": {
    "closures": "closures.json",
    "gulf_stream_edge": "stream.json"
  },
  "attribution": [
    "NOAA National Data Buoy Center (buoy readings)",
    "NOAA CO-OPS (tide predictions)"
  ]
}
```
- `status`: `ok` = show areas; `no_favorable_areas` = conditions poor right now (show `message`); `unavailable` = not enough data (show `message`).
- `heat` is `null` for **snook and tarpon** (they are scored at named inlets, not on a grid): show their areas, no heat layer.
- `conditions.sea.now.level` is one of `good`, `fair`, `rough`, `dangerous`.

### species/<id>.json (real example: snook, trimmed)
```json
{
  "api_version": 1,
  "generated_utc": "2026-10-23T18:15:25.128403+00:00",
  "id": "snook",
  "name": "Common snook",
  "scientific_name": "Centropomus undecimalis",
  "color": "#60a5fa",
  "image": {
    "url": "img/snook.png",
    "kind": "illustration",
    "credit": "Original illustration",
    "license": ""
  },
  "about": {
    "size": "Up to about 48 in (50 lb) per FWC; Florida state record 45 lb 12 oz",
    "diet": "Fish and large crustaceans; pinfish, anchovies and shrimp are major prey in one ...",
    "behavior": "Ambush predator that faces moving water and waits for prey to be carried down th...",
    "spawning": "April through October in Florida, with peaks around June to September. Spawning ..."
  },
  "today": {
    "status": "ok",
    "message": "",
    "area_count": 8,
    "areas": [
      {
        "id": "snook-1",
        "title": "Government Cut (inlet)",
        "score": 0.795,
        "confidence": "Low",
        "coords": [
          -80.135,
          25.767
        ],
        "zone": {
          "type": "Polygon",
          "coordinates": "[[ [lon,lat], [lon,lat], ... ]]"
        },
        "reasons": [
          {
            "tag": "static",
            "text": "This is an inlet. Snook gather in inlets and passes to ambush bait on the tide, and to spawn in summer."
          },
          {
            "tag": "measured",
            "text": "Water is 26.8 C, comfortably above the cold limit where snook stop feeding."
          }
        ],
        "details": [
          {
            "label": "Position",
            "value": "25.767 N, 80.135 W"
          },
          {
            "label": "Water temp",
            "value": "26.8 C (Virginia Key, FL buoy, 5 km away)"
          },
          {
            "label": "Tide",
            "value": "Rising at Virginia Key. Next: High 7:37 PM, Low 1:44 AM, High 8:11 AM"
          }
        ],
        "timing": {
          "start": "2026-10-23T18:15:25.128403+00:00",
          "step_min": 60,
          "scores": [
            50,
            50,
            50,
            50,
            78,
            74,
            94,
            94,
            "..."
          ],
          "window": {
            "start": "2026-10-24T00:15:25.128403+00:00",
            "end": "2026-10-24T03:15:25.128403+00:00",
            "score": 0.944
          },
          "why": [
            "It is night, when snook feed around inlet lights and channels."
          ],
          "evidence": "angler_lore",
          "note": ""
        },
        "sea": {
          "level": "fair",
          "text": "Fair: NE wind 5 kn, waves 3 ft at 14 s (Virginia Key, FL, 5 km away; waves: Hollywood Beach, FL, 26 km away)"
        }
      },
      "..."
    ]
  },
  "heat": null
}
```
- `coords` and every GeoJSON position are **[longitude, latitude]** (not lat, lon).
- `zone` is a GeoJSON `Polygon` or `MultiPolygon`.
- `score` is 0 to 1 (show as a percentage). `confidence` is `Low` or `Medium`. The scores are experimental: never present them as certainty.
- `reasons[].tag`: `measured`, `modeled`, `seasonal`, `static` (a chip such as Measured / Modeled / Seasonal / Mapped).
- `timing` is `null` for fish with no reliable time-of-day information (mahi-mahi and cobia today): show "No reliable timing information yet".
  Otherwise: `scores` = 24 numbers (0 to 100), one per hour starting at `start`; `window` = the best stretch (`start`, `end`, `score`) or `null`
  when nothing stands out (then show `note`); `why` = short strings explaining the window.
  All times are **UTC ISO strings: convert to the phone's local time** (`DateTime.parse(s).toLocal()`).
- `details` rows have free-text `label` and `value` (depth, temperature, tide, moon, current, no-fishing check, and so on). Show them as a list.
  Labels seen so far: Position, Water depth, Surface temp, Chlorophyll, Current, Gulf Stream, Tide, Light, Moon, Weather, Boat conditions,
  Wind outlook, Nearest inlet, Nearest buoy, No-fishing check / zone / zones, plus reef or wreck names.
- `sea` is `null` or `{level, text}`. If `level` is `rough` or `dangerous`, show a visible warning on that area.

### heat block (real example: mahi-mahi)
```json
{
  "bounds": [
    -81.01,
    24.49,
    -78.49,
    27.01
  ],
  "width": 126,
  "height": 126,
  "png": "heat/mahi-mahi.png",
  "scores": "heat/mahi-mahi.json",
  "legend": {
    "min_score": 0.45,
    "note": "Brighter means a better match. Cells below the minimum are transparent."
  }
}
```
`bounds` order is **[west, south, east, north]**. For `flutter_map` that is `LatLngBounds(LatLng(south, west), LatLng(north, east))`.

## 6. Rules the app must follow

1. **Ignore fields you do not know and tolerate missing optional ones.** Fields are only ever added inside `v1`. A change that removes or
   renames a field would be published as `/v2/`.
2. **Never trust the list of fish or statuses to be fixed.** Drive the UI from `index.json`. Treat an unknown `status` as `unavailable`.
3. **Show data age.** Compute `now - generated_utc`. If it is over 3 hours, show a visible "Forecast is N hours old" notice (the hourly job
   may be failing). If the network is down, show the last cached copy with "Offline: showing data from <time>".
4. **Cache.** Store the last successful `index.json` and `species/<id>.json` (raw JSON text + download time). Refresh when the app opens or
   resumes if the cache is older than 30 minutes, and on pull-to-refresh. Cache the pictures with the usual image cache.
5. **Be gentle:** HTTPS only, 10 second timeout, at most 2 retries, never poll faster than every 15 minutes.
6. **Show text as plain text.** Do not render it as HTML. Do not execute or follow anything inside the files.
7. **Always show** the `disclaimer` and `attribution` from `index.json` somewhere in the app (an info screen is fine). Each fish picture is an original
   illustration unless `image.kind` is `photo`; for a photo, show its `credit`.
8. **Do not invent regulations.** Legal size, bag limits and seasons are intentionally NOT in the API (they vary by area and change). Show a button
   that opens `about.regulations_link` (FWC) and the `about.regulations_note` text when present.

## 7. What to build (tasks and acceptance checks)

Create a self-contained feature folder, for example `lib/features/fish_forecast/`, and use whatever state management Seabound already uses.
A starting point (untested, written without the Flutter SDK) is in the repo: `docs/seabound_client.dart` on the `main` branch. Check it against
the real package versions before relying on it.

**Real sample responses** (a snapshot, for test fixtures only) are in this repo at `docs/api-sample/v1/` on the `main` branch. They go stale within hours, so never read them in the running app; the app reads the live URL.

| # | Task | Done when |
|---|---|---|
| T1 | One config constant for the base URL | Changing it is the only change needed to switch hosts |
| T2 | Models + JSON parsing for index, species, area, timing, heat | Unit tests parse the real examples above (save real files as test fixtures) and survive missing optional fields |
| T3 | API client (timeout, retries, error types) | A 404 or timeout gives a clear error object, not a crash |
| T4 | Repository with cache and staleness info | Offline shows cached data with its age; stale (over 3 h) is flagged |
| T5 | Fish filter UI (chips or a sheet) | Shows picture, name, area count; fish with `status != ok` are greyed with their `message`; selecting one loads its file |
| T6 | Map layers for the selected fish | Heat PNG at `bounds`; markers at `coords`; tapping a marker opens the sheet; fish with `heat == null` show markers only; opacity adjustable |
| T7 | Details sheet | Picture, name, scientific name, score %, confidence, reasons with tag chips, best-window chart (24 bars, window highlighted, local time), details rows, about (size, diet, behavior, depth, spawning, lifespan), FWC button |
| T8 | Info screen | Disclaimer, attribution list, "updated N min ago" |
| T9 | Tests | Parsing tests, a repository cache test, and a widget test for the three `status` values and for `timing == null` |

## 8. Do NOT

- Do not read anything outside `api/v1/` (especially not the top-level `fish.json`, `heat.json`, `latest.json`).
- Do not compute scores, tides, moon phases or heat in the app. The numbers in the files are the single source of truth.
- Do not hard-code the fish list, colours, descriptions or image links: they come from the files.
- Do not write to the repo or call any GitHub API. A plain GET of the file URLs is all that is needed.
- Do not put keys or secrets anywhere: there are none.

## 9. Check your work against the real files

```
curl -s https://raw.githubusercontent.com/markeetox/lupita/data/api/v1/index.json | head -c 600
curl -s https://raw.githubusercontent.com/markeetox/lupita/data/api/v1/species/snook.json | head -c 600
curl -sI https://raw.githubusercontent.com/markeetox/lupita/data/api/v1/heat/mahi-mahi.png      # expect HTTP 200, content-type image/png
curl -sI https://raw.githubusercontent.com/markeetox/lupita/data/api/v1/img/mahi-mahi.png
```
In a browser you can also see the files on GitHub: open `https://github.com/markeetox/lupita`, change the branch from `main` to `data`, open `api/v1`.

## 10. Known limits (be honest with users)

- **Experimental.** Scores show where conditions match published habitat research. They are not yet checked against real catches.
- Time-of-day advice comes from local captains' reports ("angler lore"), not studies. The `evidence` field says so.
- Gulf Stream edge and currents are approximate (25 km satellite data).
- If NOAA's satellite server refuses the hourly request, the files stop updating and `generated_utc` falls behind. The app's staleness notice (rule 3) is the safeguard.
