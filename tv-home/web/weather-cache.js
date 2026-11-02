// Small shared policy: accepted readings expire even if the weather service stays down.
(function (root) {
  "use strict";
  var MAX_AGE = 2 * 60 * 60 * 1000;
  function key(place) { return [place.lat, place.lon, place.timezone || "auto"].join("/"); }
  function valid(w) {
    return w && typeof w.temp === "number" && isFinite(w.temp) &&
      typeof w.code === "number" && isFinite(w.code);
  }
  var api = {
    record: function (place, weather, now) {
      return valid(weather) ? { place: key(place), weather: weather, accepted: now } : null;
    },
    read: function (record, place, now) {
      if (!record || record.place !== key(place) || !valid(record.weather) ||
          typeof record.accepted !== "number" || !isFinite(record.accepted) ||
          record.accepted > now || now - record.accepted >= MAX_AGE) return null;
      return record.weather;
    }
  };
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.WeatherCache = api;
})(this);
