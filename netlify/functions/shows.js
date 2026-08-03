// PuneScreens showtimes engine: parses live sessions from District's server-rendered venue pages.
// CDN-cached 30 min => timings refresh automatically all day.
function walk(o, ctx, out) {
  if (Array.isArray(o)) { o.forEach(x => walk(x, ctx, out)); return; }
  if (!o || typeof o !== "object") return;
  const nm = o.movieName || o.filmName || o.eventName ||
    (typeof o.name === "string" && o.name.length > 2 && o.name.length < 80 && !/^https?:/.test(o.name) ? o.name : null) || ctx;
  const tEntry = Object.entries(o).find(([k, v]) =>
    /time/i.test(k) && typeof v === "string" && /^\d{1,2}:\d{2}\s?(AM|PM)$/i.test(v.trim()));
  if (tEntry && nm) {
    const tag = Object.values(o).find(v =>
      typeof v === "string" && v !== tEntry[1] && /^[A-Z0-9 \[\]\-+]{2,14}$/.test(v.trim()) && /[A-Z]{2}/.test(v)) || "";
    (out[nm] = out[nm] || new Set()).add(tEntry[1].trim().toUpperCase() + (tag ? "|" + tag.trim() : ""));
  }
  Object.values(o).forEach(v => walk(v, nm, out));
}
exports.handler = async (event) => {
  const p = (event.queryStringParameters || {}).p || "";
  if (!/^[a-z0-9\-]+-cd\d+$/i.test(p))
    return { statusCode: 400, headers: { "Access-Control-Allow-Origin": "*" }, body: JSON.stringify({ ok: false, err: "bad slug" }) };
  try {
    const r = await fetch("https://www.district.in/movies/" + p, {
      headers: { "User-Agent": "Mozilla/5.0 (compatible; punescreens/1.0)" } });
    if (!r.ok) throw new Error("http " + r.status);
    const html = await r.text();
    const m = html.match(/<script id="__NEXT_DATA__"[^>]*>([\s\S]*?)<\/script>/);
    const out = {};
    if (m) { try { walk(JSON.parse(m[1]), null, out); } catch (e) {} }
    // fallback: visible pattern scrape
    if (!Object.keys(out).length) {
      const rx = /(\d{1,2}:\d{2}\s?(?:AM|PM))/gi; let mm; const times = [];
      while ((mm = rx.exec(html))) times.push(mm[1].toUpperCase());
      if (times.length) out["Now playing"] = new Set(times.slice(0, 12));
    }
    const movies = Object.entries(out)
      .filter(([k]) => k && k.length < 80)
      .map(([k, v]) => ({ movie: k, shows: [...v].map(s => { const [t, tag] = s.split("|"); return { t, tag: tag || "" }; }) }))
      .filter(x => x.shows.length).slice(0, 20);
    return { statusCode: 200,
      headers: { "Content-Type": "application/json", "Cache-Control": "public, s-maxage=1800", "Access-Control-Allow-Origin": "*" },
      body: JSON.stringify({ ok: movies.length > 0, fetchedAt: new Date().toISOString(), url: "https://www.district.in/movies/" + p, movies }) };
  } catch (e) {
    return { statusCode: 200, headers: { "Content-Type": "application/json", "Cache-Control": "public, s-maxage=300", "Access-Control-Allow-Origin": "*" },
      body: JSON.stringify({ ok: false, err: String(e && e.message || e) }) };
  }
};
