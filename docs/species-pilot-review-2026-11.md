# LUPITA South Florida Pilot Species Review

Status: research baseline for model design. No species profiles are modified by this document.

## Audit baseline

The validator inspected 130 profiles:
- 127 require biological research or model rebuilding.
- 125 are classified as needing a model rebuild.
- 3 profiles are structurally invalid: snook, tarpon, and yellowtail snapper.
- The audit found no active-factor incompatibility with the two current scoring engines, but that does not establish biological validity.

Bonefish and permit each have only one active factor: sea-surface temperature at weight 0.35. Their current site scores cannot distinguish a seagrass flat from a sandy flat, a channel edge, or a spawning reef.

## 1. Common snook (*Centropomus undecimalis*)

### Model role
Inshore estuarine species. A useful test of habitat features, temperature stress, seasonal movement, salinity, and inlet or river connectivity.

### Evidence already available
- FWC describes common snook in coastal inshore waters, mangrove shorelines, seagrass beds, beaches, and around structure. It reports a cold limit below 60°F and a broad salinity tolerance.
- FWC describes Florida spawning from approximately April/May through September/October, with spawning at coastal river mouths and major inlets. It also describes movement between upper-estuary overwintering areas and higher-salinity spawning areas.
- A peer-reviewed Tampa Bay study shows that adult movement and spawning-site use are more complex than a simple annual migration rule. Some fish remain in estuaries, and spawning-site fidelity varies.
- South Florida Everglades telemetry research identifies freshwater flow and water-level change as important movement context. Temperature and salinity alone explained only a small part of the movement variation in that study.

### Current model problems
- The site scorer treats site kind as structure type. This makes an inlet/cut/flat label stand in for mangrove, seagrass, reef, or other actual habitat.
- The adult preferred temperature band is not established by the juvenile habitat evidence currently cited in the profile.
- Falling-tide and low-light preferences remain angler-derived, not proven universal preferences.
- Salinity and freshwater-flow context are not currently modeled at the required spatial and temporal resolution.

### Pilot direction
Separate estuarine habitat suitability from seasonal spawning movement and current conditions. Keep the cold-stress gate only where the source supports its use and define whether it applies to adult survival, feeding activity, or regional occurrence.

### Research sources
- [FWC Common Snook profile](https://myfwc.com/wildlifehabitats/profiles/saltwater/snook/snook/)
- [FWC Sketch of the Common Snook in Florida](https://myfwc.com/research/saltwater/fish/snook/sketch-common-snook/)
- [Spawning Site Selection and Contingent Behavior in Common Snook](https://pmc.ncbi.nlm.nih.gov/articles/PMC4084985/)
- [Primed and cued: freshwater flows and spawning migrations in the Florida Everglades](https://pmc.ncbi.nlm.nih.gov/articles/PMC9655820/)
- [The role of freshwater discharges on Common Snook movements and distribution](https://academic.oup.com/mcf/article/18/2/vtag002/8526360)

## 2. Atlantic tarpon (*Megalops atlanticus*)

### Model role
Migratory coastal and estuarine species. Tests regional seasonal presence, temperature-linked movement, life-stage differences, and connectivity among creeks, bays, passes, and coastal waters.

### Evidence already available
- Two decades of satellite tagging documented large-scale Atlantic tarpon migrations, regional connectivity, estuarine use, and spawning locations.
- Florida Keys tagging research cited in the current profile reports seasonal adult presence concentrated in spring and early summer. The profile's application of Keys timing to the Miami area is explicitly an assumption and should remain provisional until locally tested.
- A 2025 south Florida study found juvenile tarpon of 25–35 cm moved out of mangrove creek habitat in response to temperatures below 20°C. This is juvenile evidence, not an adult threshold.
- Research on juvenile tarpon in the U.S. Virgin Islands describes temperature-related changes in lagoon use, while adult Florida migration studies report movement associated with the 26°C isotherm. These are different populations and life stages.

### Current model problems
- The profile combines adult seasonal movement and juvenile temperature response without a clear life-stage boundary.
- Tide and low-light factors are angler guidance.
- Structure type currently means site kind, not habitat structure.
- Inactive salinity configuration has malformed range/ideal settings and must be corrected before the profile can pass structural validation.

### Pilot direction
Build separate adult migration and juvenile nursery-habitat evidence groups. Do not apply the juvenile 20°C response as an adult gate. Keep tide/light timing provisional and separate from seasonal presence.

### Research sources
- [Migrations and movements of Atlantic tarpon revealed by two decades of satellite tagging](https://onlinelibrary.wiley.com/doi/full/10.1111/faf.12430)
- [New study reveals international movements of Atlantic tarpon](https://news.miami.edu/rosenstiel/stories/2020/01/new-study-reveals-international-movements-of-atlantic-tarpon-need-for-protection.html)
- [Low temperature cues ontogenetic shifts by juvenile Atlantic tarpon in south Florida](https://pmc.ncbi.nlm.nih.gov/articles/PMC12710809/)
- [Florida Museum Tarpon profile](https://www.floridamuseum.ufl.edu/discover-fish/species-profiles/tarpon)

## 3. Bonefish (*Albula vulpes*)

### Model role
Shallow-water flats specialist with a distinct offshore spawning migration. Tests the separation of foraging habitat, pre-spawning staging habitat, and offshore spawning habitat.

### Evidence already available
- Acoustic telemetry in the northern Florida Keys documented use of shallow foraging habitat and suggested that deeper channels may provide refuge from rapid temperature changes. The study's observed site fidelity was limited, so it does not justify assigning fixed home ranges to every fish.
- NOAA-hosted peer-reviewed research from the Bahamas linked bonefish home ranges to a pre-spawning aggregation site. This is useful Caribbean comparative evidence, not a direct Biscayne Bay calibration.
- Florida research on juvenile Albula spp. found positive catches across a range of water-quality conditions and shallow depths. Because that study covers Albula spp. and juveniles, it should not be used as a direct adult preferred-temperature range for *A. vulpes*.

### Current model problems
- The current profile is generic and uses only sea-surface temperature.
- Its profile description and source references are generic NOAA landing-page links, not species-specific evidence.
- A site kind of flat is not enough to represent seagrass, sand, mud, or hard-bottom habitat.
- Spawning habitat is offshore and should not be scored as if it were the same as shallow flats habitat.

### Pilot direction
Create distinct shallow-flat foraging and spawning-migration dimensions. Add habitat attributes only when supported by mapped habitat data. Treat spawning phase as a regional seasonal movement feature, not a flat suitability score.

### Research sources
- [Movements and site fidelity of bonefish in the northern Florida Keys](https://doi.org/10.3354/meps291237)
- [NOAA: Bonefish home range to spawning site linkages (Bahamas study)](https://www.fisheries.noaa.gov/resource/peer-reviewed-research/bonefish-albula-vulpes-home-range-spawning-site-linkages-support)
- [FAU research on South Florida and Bahamas bonefish habitat gaps](https://digitalcommons.fau.edu/etd_general/1021/)
- [Florida research on juvenile Albula spp. habitat preferences](https://academic.oup.com/mcf/article/17/3/vtaf003/8137700)

## 4. Permit (*Trachinotus falcatus*)

### Model role
Flats forager connected to offshore spawning reefs. Tests habitat-network modeling and the difference between a species' feeding habitat and spawning habitat.

### Evidence already available
- Acoustic telemetry of 45 permit near the lower Florida Keys found high connectivity between nearshore flats shallower than 3 m and Florida Reef Tract habitats around 15–40 m. About 75% of tagged fish were detected in both habitat types.
- Reef occupancy peaked March through September, with the highest detections in April and May. The study interprets flats primarily as foraging habitat and reefs as spawning habitat.
- The Florida Museum describes permit foraging on flats and intertidal areas, moving into shallow water on incoming tides from deeper channels and basins. It also describes offshore reef, jetty, and wreck use.
- A 2023 angler and guide survey found reported declines in permit fishing quality, particularly on flats in the Upper Florida Keys and Biscayne Bay. This is valuable local ecological knowledge, but it is survey evidence and should not be treated as a direct abundance time series.

### Current model problems
- The current profile is generic and uses only sea-surface temperature.
- It cannot distinguish flats foraging habitat from offshore spawning structures.
- A single seasonal factor cannot describe both occupancy and spawning aggregation dynamics.
- Tide preference should not be generalized across flats, channels, and offshore spawning sites without evidence.

### Pilot direction
Represent the flats-to-reef habitat connection explicitly. Separate foraging habitat suitability from seasonal reef occupancy and spawning aggregation timing. Do not assume a nearby flat is itself a spawning site.

### Research sources
- [Seasonal occupancy and connectivity amongst nearshore flats and reef habitats by permit](https://pubmed.ncbi.nlm.nih.gov/31823365/)
- [Florida Museum Permit profile](https://www.floridamuseum.ufl.edu/discover-fish/species-profiles/permit/)
- [Permit fishing quality and conservation threats in the Florida Keys](https://aquila.usm.edu/gcr/vol34/iss1/3/)
- [Permit aggregation fishery dynamics and depredation in the Florida Keys](https://www.sciencedirect.com/science/article/pii/S016578362600038X)

## 5. Mahi-mahi (*Coryphaena hippurus*)

### Model role
Offshore pelagic species. Tests gridded environmental layers, current edges, convergence, temperature, and the need for floating-habitat observations.

### Evidence already available
- NOAA describes Atlantic mahi-mahi as pelagic, near-surface fish in tropical and subtropical waters across the Atlantic, Gulf, and Caribbean. Larger males favor open ocean, while females and smaller males are commonly associated with floating objects and Sargassum.
- Satellite-tagging research on fish released in the Florida Straits and Gulf of Mexico found tagged mahi spent about 95% of their time in 25–29°C water, with occasional deep dives. The study also identified northward movement associated with the Gulf Stream.
- FWC describes the Gulf Stream and its edges, eddies, color changes, and floating Sargassum as important offshore pelagic habitat features.

### Current model problems
- The current grid profile uses temperature, gradients, chlorophyll, convergence, bottom depth, and estimated Gulf Stream edge. Several factors are provisional or weakly supported.
- Sargassum is identified as an important habitat association but is inactive because a dependable Sargassum layer is not yet integrated.
- Bottom depth is only a proxy for offshore location; it is not the depth occupied by the fish.
- Relative gradient scoring ranks today's strongest edge, which is not equivalent to a biologically meaningful absolute threshold.

### Pilot direction
Keep this as the offshore grid-model test case. Separate water-mass/current-edge conditions from direct floating-habitat observations. Keep Sargassum inactive until the data source and spatial coverage are dependable. Preserve bottom depth as a clearly labeled offshore-context proxy, not a fish-depth preference.

### Research sources
- [NOAA Atlantic Mahi-Mahi species profile](https://www.fisheries.noaa.gov/species/atlantic-mahi-mahi)
- [NOAA Atlantic Mahi-Mahi resources](https://www.fisheries.noaa.gov/species/atlantic-mahi-mahi/resources)
- [Remote Predictions of Mahi-Mahi Spawning in the Open Ocean Using Summarized Accelerometry Data](https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2021.626082/full)
- [NC Sea Grant: Mahi-Mahi temperature and depth from satellite tags](https://ncseagrant.ncsu.edu/hooklinescience/what-depth-and-water-temperature-do-mahi-mahi-prefer/)
- [FWC Marine Fisheries Habitats](https://myfwc.com/wildlifehabitats/habitat/marine/)

## Pilot decisions

| Species | Spatial mode | Primary modeling challenge | Do not assume |
|---|---|---|---|
| Snook | Sites + future habitat layers | Estuarine habitat and seasonal movement | One adult temperature optimum or one universal tide preference |
| Tarpon | Sites + future habitat layers | Adult migration versus juvenile nursery use | Juvenile temperature response applies to adults |
| Bonefish | Sites + future habitat layers | Flats foraging versus offshore spawning migration | A generic flat site is suitable habitat |
| Permit | Sites + reef/grid connection | Flats foraging versus reef spawning | Flats and spawning reefs are interchangeable |
| Mahi-mahi | Grid | Pelagic fronts and floating habitat | Bottom depth equals fish depth or every visible edge is productive |

## Work not authorized by this research baseline

This document does not change numeric factor ranges, weights, gates, timing maps, site eligibility, or live outputs. Those changes should be made only after the framework is approved by tests and each factor has a direct, applicable source.
