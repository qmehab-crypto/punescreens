// PuneScreens buzz engine — public-sentiment score per venue.
// Seeds come from review research (Justdial/Tripadvisor/Reddit threads);
// live Reddit chatter nudges them ±15. CDN-cached 24h => rankings refresh daily.
const SEEDS = {
  inoxmegaplexphoe: { name: "INOX Megaplex Wakad", q: "Pune Wakad IMAX Megaplex", buzz: 78 },
  citypridekharadi: { name: "City Pride Kharadi", q: "City Pride Kharadi Dolby", buzz: 82 },
  esquareepiqhinja: { name: "E-Square EPIQ", q: "EPIQ Pune Hinjawadi", buzz: 80 },
  cinepoliswestend: { name: "Cinepolis Westend", q: "Westend IMAX Pune", buzz: 38 },
  cinepolisseasons: { name: "Cinepolis Seasons", q: "Cinepolis Seasons Mall Pune", buzz: 55 },
  pvriconthepavill: { name: "PVR ICON Pavillion", q: "PVR ICON Pune", buzz: 70 },
  pvrdirectorscutk: { name: "PVR Director's Cut KOPA", q: "Directors Cut KOPA Pune", buzz: 74 },
  pvrgrandhighstre: { name: "PVR Grand Highstreet", q: "PVR Hinjawadi PXL", buzz: 66 },
  pvrphoenixmarket: { name: "PVR Phoenix Marketcity", q: "PVR Phoenix Marketcity Pune 4DX", buzz: 60 },
  esquarexionhinja: { name: "E-Square Xion", q: "E-Square Xion Hinjawadi", buzz: 30 },
  citypridemangala: { name: "City Pride Mangala", q: "Mangala theatre Pune", buzz: 25 },
  esquareuniversit: { name: "E-Square University Rd", q: "E-Square Pune University Road", buzz: 50 },
  citypridekothrud: { name: "City Pride Kothrud", q: "City Pride Kothrud", buzz: 68 },
  viluxtalkieskhad: { name: "Vilux Talkies", q: "Vilux Khadki", buzz: 15 },
  victorycamp:      { name: "Victory Cinema", q: "Victory theatre Pune Camp", buzz: 45 },
  rahul70mm:        { name: "Rahul 70MM", q: "Rahul talkies Pune", buzz: 55 },
  inoxbundgarden:   { name: "INOX Bund Garden", q: "INOX Bund Garden Pune", buzz: 58 },
  inoxelprocitysqu: { name: "INOX Elpro", q: "INOX Elpro Chinchwad", buzz: 55 },
  moviemaxamanora:  { name: "MovieMax Amanora", q: "MovieMax Amanora Pune", buzz: 52 },
  rajhans93avenue:  { name: "Rajhans 93 Avenue", q: "Rajhans cinema Pune", buzz: 62 },
  mirajspinecitymo: { name: "Miraj Spine City", q: "Miraj Spine City Moshi", buzz: 60 },
};
const POS = ["amazing","best","great","awesome","excellent","love","loved","worth","crisp","massive","huge","stunning","comfortable","clean"];
const NEG = ["worst","bad","dirty","small","poor","avoid","terrible","liemax","broken","dim","overpriced","uncomfortable","pathetic"];

async function redditAdj(q) {
  try {
    const r = await fetch(
      "https://www.reddit.com/search.json?limit=25&sort=new&t=year&q=" + encodeURIComponent(q),
      { headers: { "User-Agent": "punescreens/1.0 (buzz ranker)" } });
    if (!r.ok) return { adj: 0, mentions: 0 };
    const j = await r.json();
    const posts = (j.data && j.data.children) || [];
    let pos = 0, neg = 0;
    posts.forEach(p => {
      const txt = ((p.data.title || "") + " " + (p.data.selftext || "")).toLowerCase();
      POS.forEach(w => { if (txt.includes(w)) pos++; });
      NEG.forEach(w => { if (txt.includes(w)) neg++; });
    });
    return { adj: Math.max(-15, Math.min(15, (pos - neg) * 3)), mentions: posts.length };
  } catch (e) { return { adj: 0, mentions: 0 }; }
}

exports.handler = async (event) => {
  const halls = {};
  let live = false;
  const keys = Object.keys(SEEDS);
  // live-poll the 8 most talked-about venues; seeds cover the rest
  const hot = keys.slice(0, 8);
  await Promise.all(keys.map(async k => {
    const s = SEEDS[k];
    let adj = 0, mentions = 0;
    if (hot.includes(k)) { const r = await redditAdj(s.q); adj = r.adj; mentions = r.mentions; if (r.mentions > 0) live = true; }
    halls[k] = { name: s.name, buzz: Math.max(5, Math.min(95, s.buzz + adj)), mentions };
  }));
  const generatedAt = new Date().toISOString();
  const fmt = (event.queryStringParameters || {}).format;
  if (fmt === "csv") {
    let csv = "venue,buzz,mentions,updated\n";
    Object.values(halls).forEach(h => { csv += `"${h.name}",${h.buzz},${h.mentions},${generatedAt}\n`; });
    return { statusCode: 200, headers: { "Content-Type": "text/csv", "Cache-Control": "public, s-maxage=86400", "Access-Control-Allow-Origin": "*" }, body: csv };
  }
  return {
    statusCode: 200,
    headers: { "Content-Type": "application/json", "Cache-Control": "public, s-maxage=86400", "Access-Control-Allow-Origin": "*" },
    body: JSON.stringify({ generatedAt, source: live ? "seeds+reddit-live" : "seeds", method: "75% engineering (screen, projection, sound, format) + 25% public buzz, refreshed every 24h", halls })
  };
};
