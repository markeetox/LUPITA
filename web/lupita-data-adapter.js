(function (root) {
  "use strict";

  function finiteNumber(value) {
    if (value === null || value === undefined || value === "") return null;
    const number = Number(value);
    return Number.isFinite(number) ? number : null;
  }

  function normalizeArea(speciesId, area, index) {
    if (!area || typeof area !== "object") return null;
    const coords = Array.isArray(area.coords) && area.coords.length >= 2
      ? [finiteNumber(area.coords[0]), finiteNumber(area.coords[1])]
      : null;
    if (!coords || coords.some(value => value === null)) return null;

    const zone = area.zone && typeof area.zone === "object" ? area.zone : null;
    let ring = null;
    let rings = null;
    if (zone && zone.type === "Polygon" && Array.isArray(zone.coordinates)) {
      ring = zone.coordinates[0] || null;
    } else if (zone && zone.type === "MultiPolygon" && Array.isArray(zone.coordinates)) {
      rings = zone.coordinates.map(polygon => polygon && polygon[0]).filter(Array.isArray);
    }

    const details = Array.isArray(area.details) ? area.details : [];
    const reasons = Array.isArray(area.reasons) ? area.reasons : [];
    const score = finiteNumber(area.score);

    return {
      id: String(area.id || (speciesId + "-area-" + (index + 1))),
      species: String(speciesId),
      title: String(area.title || ("Area " + (index + 1))),
      coords,
      score,
      confidence: String(area.confidence || "Unknown"),
      confidence_basis: Array.isArray(area.confidence_basis) ? area.confidence_basis : [],
      active_factor_count: finiteNumber(area.active_factor_count),
      data_coverage: finiteNumber(area.data_coverage),
      environmental_data_coverage: finiteNumber(area.environmental_data_coverage),
      factor_diagnostics: Array.isArray(area.factor_diagnostics) ? area.factor_diagnostics : [],
      reasons: reasons.map(reason => [String(reason && reason.tag || "modeled"), String(reason && reason.text || "")]),
      location: details.map(detail => [String(detail && detail.label || "Detail"), String(detail && detail.value || "")]),
      timing: area.timing && typeof area.timing === "object" ? area.timing : null,
      sea: area.sea && typeof area.sea === "object" ? area.sea : null,
      ring,
      rings,
      zone,
      api_v1: true
    };
  }

  function normalizeSpeciesDetail(detail) {
    if (!detail || typeof detail !== "object" || !detail.id) {
      throw new TypeError("Species detail must include an id");
    }
    const today = detail.today && typeof detail.today === "object" ? detail.today : {};
    const areas = Array.isArray(today.areas) ? today.areas : [];
    return {
      id: String(detail.id),
      name: String(detail.name || detail.id),
      status: String(today.status || "unknown"),
      message: String(today.message || ""),
      generated_utc: detail.generated_utc || null,
      areas: areas.map((area, index) => normalizeArea(detail.id, area, index)).filter(Boolean)
    };
  }

  function haversineKm(lat1, lon1, lat2, lon2) {
    const rad = value => value * Math.PI / 180;
    const dLat = rad(lat2 - lat1);
    const dLon = rad(lon2 - lon1);
    const a = Math.sin(dLat / 2) ** 2 +
      Math.cos(rad(lat1)) * Math.cos(rad(lat2)) * Math.sin(dLon / 2) ** 2;
    return 6371.0088 * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  }

  function rankOpportunities(spots, speciesIds, center, limit) {
    const maxItems = Number.isInteger(limit) && limit > 0 ? limit : 3;
    const lat = finiteNumber(center && center.lat);
    const lon = finiteNumber(center && (center.lng !== undefined ? center.lng : center.lon));
    if (lat === null || lon === null) return [];

    return (Array.isArray(speciesIds) ? speciesIds : []).map(speciesId => {
      const ranked = (Array.isArray(spots) ? spots : [])
        .filter(spot => spot && spot.species === speciesId &&
          finiteNumber(spot.score) !== null &&
          Array.isArray(spot.coords) && finiteNumber(spot.coords[0]) !== null && finiteNumber(spot.coords[1]) !== null)
        .map(spot => ({
          ...spot,
          distance_km: haversineKm(lat, lon, Number(spot.coords[1]), Number(spot.coords[0]))
        }))
        .sort((a, b) => Number(b.score) - Number(a.score) || a.distance_km - b.distance_km)
        .slice(0, maxItems);
      return { speciesId, spots: ranked };
    }).filter(group => group.spots.length > 0);
  }

  const api = { normalizeArea, normalizeSpeciesDetail, rankOpportunities, haversineKm };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (root) root.LupitaDataAdapter = api;
})(typeof window !== "undefined" ? window : globalThis);
