/* Bright Mind Kids prayer times: computed entirely in the browser.
   Standard astronomical method (sun declination and equation of time). */
(function (root) {
  var RAD = Math.PI / 180, DEG = 180 / Math.PI;
  function sin(d) { return Math.sin(d * RAD); }
  function cos(d) { return Math.cos(d * RAD); }
  function tan(d) { return Math.tan(d * RAD); }
  function asin(x) { return Math.asin(x) * DEG; }
  function acos(x) { return Math.acos(x) * DEG; }
  function atan2(y, x) { return Math.atan2(y, x) * DEG; }
  function acot(x) { return Math.atan(1 / x) * DEG; }
  function fix(a, b) { a = a - b * Math.floor(a / b); return a < 0 ? a + b : a; }

  var METHODS = {
    MWL:     { name: 'Muslim World League', fajr: 18, isha: 17 },
    MOROCCO: { name: 'Morocco (Ministry of Habous)', fajr: 19, isha: 17 },
    MAKKAH:  { name: 'Umm al-Qura, Makkah', fajr: 18.5, ishaMin: 90 },
    EGYPT:   { name: 'Egyptian General Authority', fajr: 19.5, isha: 17.5 },
    ISNA:    { name: 'North America (ISNA)', fajr: 15, isha: 15 },
    KARACHI: { name: 'Karachi (University of Islamic Sciences)', fajr: 18, isha: 18 },
    FRANCE:  { name: 'France (UOIF, 12°)', fajr: 12, isha: 12 },
    TURKEY:  { name: 'Turkey (Diyanet)', fajr: 18, isha: 17 },
    GULF:    { name: 'Gulf region', fajr: 19.5, ishaMin: 90 }
  };

  function julian(y, m, d) {
    if (m <= 2) { y -= 1; m += 12; }
    var A = Math.floor(y / 100), B = 2 - A + Math.floor(A / 4);
    return Math.floor(365.25 * (y + 4716)) + Math.floor(30.6001 * (m + 1)) + d + B - 1524.5;
  }
  function sun(jd) {
    var D = jd - 2451545.0;
    var g = fix(357.529 + 0.98560028 * D, 360);
    var q = fix(280.459 + 0.98564736 * D, 360);
    var L = fix(q + 1.915 * sin(g) + 0.020 * sin(2 * g), 360);
    var e = 23.439 - 0.00000036 * D;
    var RA = atan2(cos(e) * sin(L), cos(L)) / 15;
    return { decl: asin(sin(e) * sin(L)), eqt: q / 15 - fix(RA, 24) };
  }

  /* opts: {lat, lng, tz (hours), method key, asr: 1 (Shafi/Maliki) or 2 (Hanafi), date: {y,m,d}} */
  function compute(o) {
    var M = METHODS[o.method] || METHODS.MWL;
    var jd = julian(o.date.y, o.date.m, o.date.d) - o.lng / (15 * 24);
    function noon(t) { return fix(12 - sun(jd + t / 24).eqt, 24); }
    function hourAngleTime(alt, t, dir) { // alt: sun altitude in degrees (negative = below horizon)
      var s = sun(jd + t / 24), n = noon(t);
      var c = (sin(alt) - sin(s.decl) * sin(o.lat)) / (cos(s.decl) * cos(o.lat));
      if (c < -1 || c > 1) return NaN;
      return n + dir * acos(c) / 15;
    }
    function asrTime(t) {
      var s = sun(jd + t / 24);
      var alt = acot(o.asr + tan(Math.abs(o.lat - s.decl)));
      return hourAngleTime(alt, t, 1);
    }
    var est = { fajr: 5, sunrise: 6, dhuhr: 12, asr: 13, maghrib: 18, isha: 19 }, t = est;
    for (var it = 0; it < 2; it++) {
      var g = {};
      for (var k0 in est) g[k0] = isNaN(t[k0]) ? est[k0] : t[k0];
      t = {
        fajr: hourAngleTime(-M.fajr, g.fajr, -1),
        sunrise: hourAngleTime(-0.833, g.sunrise, -1),
        dhuhr: noon(g.dhuhr),
        asr: asrTime(g.asr),
        maghrib: hourAngleTime(-0.833, g.maghrib, 1),
        isha: M.ishaMin ? NaN : hourAngleTime(-M.isha, g.isha, 1)
      };
    }
    // high-latitude fallback (one-seventh of the night)
    var night = 24 - (t.maghrib - t.sunrise);
    if (isNaN(t.fajr) || t.sunrise - t.fajr > night / 2) t.fajr = t.sunrise - night / 7;
    if (M.ishaMin) t.isha = t.maghrib + M.ishaMin / 60;
    else if (isNaN(t.isha) || t.isha - t.maghrib > night / 2) t.isha = t.maghrib + night / 7;
    var adj = { dhuhr: 1 / 60, maghrib: 1 / 60 }; // safety margins commonly applied
    var out = {};
    for (var k2 in t) out[k2] = fix(t[k2] + o.tz - o.lng / 15 + (adj[k2] || 0), 24);
    return out;
  }
  function qibla(lat, lng) {
    var kLat = 21.4225, kLng = 39.8262;
    return fix(atan2(sin(kLng - lng), cos(lat) * tan(kLat) - sin(lat) * cos(kLng - lng)), 360);
  }
  root.PrayTimesBMK = { compute: compute, qibla: qibla, METHODS: METHODS };
})(typeof window !== 'undefined' ? window : globalThis);
