#!/usr/bin/env python3
"""PuneScreens v3 — real seat maps for the Top 10, layout-accurate 3D, movie pairings."""
import csv, json, math, os

TECH = {
 "INOX Megaplex Phoenix MoM (Wakad)": dict(area="Wakad", chain="PVR INOX", proj="4K Laser", sound="Dolby Atmos", tags=["IMAX Laser","MX4D","Insignia"]),
 "PVR ICON The Pavillion": dict(area="SB Road", chain="PVR INOX", proj="4K", sound="Dolby Atmos", tags=["ICON"]),
 "PVR Kumar Pacific": dict(area="Swargate", chain="PVR INOX", proj="2K", sound="Dolby 7.1", tags=[]),
 "PVR Phoenix Marketcity": dict(area="Viman Nagar", chain="PVR INOX", proj="2K", sound="Dolby 7.1", tags=["4DX","Gold Class"]),
 "PVR Grand Highstreet (Hinjawadi)": dict(area="Hinjawadi", chain="PVR INOX", proj="4K Laser", sound="Dolby Atmos", tags=["P[XL]","RealD 3D"]),
 "PVR Director's Cut KOPA": dict(area="Koregaon Park", chain="PVR INOX", proj="4K Laser", sound="Dolby Atmos", tags=["Director's Cut","ICE"]),
 "INOX Bund Garden": dict(area="Bund Garden", chain="PVR INOX", proj="2K", sound="Dolby 7.1", tags=["Insignia"]),
 "INOX Jai Ganesh Vision (Akurdi)": dict(area="Akurdi", chain="PVR INOX", proj="2K", sound="Dolby 7.1", tags=[]),
 "INOX Elpro City Square (Chinchwad)": dict(area="Chinchwad", chain="PVR INOX", proj="2K", sound="Dolby Atmos", tags=["3D"]),
 "INOX Royale Heritage (NIBM)": dict(area="NIBM", chain="PVR INOX", proj="2K", sound="Dolby Digital", tags=[]),
 "Cinepolis Westend (Aundh)": dict(area="Aundh", chain="Cinepolis", proj="2K Xenon", sound="Dolby Atmos", tags=["IMAX"]),
 "Cinepolis Seasons Mall": dict(area="Magarpatta", chain="Cinepolis", proj="2K", sound="Dolby 7.1", tags=["VIP"]),
 "MovieMax Amanora": dict(area="Hadapsar", chain="MovieMax", proj="2K", sound="Dolby 7.1", tags=[]),
 "MovieMax Gold Mariplex": dict(area="Kalyani Nagar", chain="MovieMax", proj="2K", sound="Dolby 7.1", tags=["Gold"]),
 "Miraj Spine City (Moshi)": dict(area="Moshi", chain="Miraj", proj="2K", sound="Dolby Atmos", tags=[]),
 "Rajhans 93 Avenue": dict(area="Fatima Nagar", chain="Rajhans", proj="2K", sound="Dolby Atmos", tags=["3D"]),
 "Connplex Luxuriance Tribeca": dict(area="NIBM/Undri", chain="Connplex", proj="2K", sound="Dolby 7.1", tags=["Luxury"]),
 "City Pride Kothrud": dict(area="Kothrud", chain="City Pride", proj="4K", sound="Dolby Atmos", tags=["3D"]),
 "City Pride Satara Road": dict(area="Market Yard", chain="City Pride", proj="2K", sound="Dolby Digital", tags=["Gold Class"]),
 "City Pride R-Deccan": dict(area="Deccan", chain="City Pride", proj="2K", sound="Dolby Digital", tags=["Micro-plex"]),
 "City Pride Abhiruchi": dict(area="Sinhagad Rd", chain="City Pride", proj="2K", sound="Dolby Digital", tags=["3D"]),
 "City Pride Mangala": dict(area="Shivajinagar", chain="City Pride", proj="2K", sound="Dolby Digital", tags=[]),
 "City Pride Royal (Pimple Saudagar)": dict(area="Pimple Saudagar", chain="City Pride", proj="Laser", sound="Dolby Atmos", tags=[]),
 "City Pride Kharadi": dict(area="Kharadi", chain="City Pride", proj="4K Laser", sound="Dolby Atmos", tags=["Dolby Cinema","HFR 3D"]),
 "E-Square University Road": dict(area="University Rd", chain="E-Square", proj="4K", sound="Dolby 7.1", tags=[]),
 "E-Square Xion (Hinjawadi)": dict(area="Hinjawadi", chain="E-Square", proj="2K", sound="Dolby Atmos", tags=[]),
 "E-Square EPIQ (Hinjawadi Ph2)": dict(area="Hinjawadi Ph2", chain="E-Square", proj="Barco RGB 4K Laser", sound="64-ch Dolby Atmos", tags=["EPIQ"]),
 "Victory (Camp)": dict(area="Camp", chain="Independent", proj="Digital", sound="Basic", tags=["Heritage 1938"]),
 "Rahul 70MM": dict(area="Shivajinagar", chain="Independent", proj="Digital", sound="Basic", tags=["Heritage 70mm"]),
 "Vilux Talkies (Khadki)": dict(area="Khadki", chain="Independent", proj="Digital", sound="Basic", tags=["Heritage"]),
 "Ashok (Pimpri)": dict(area="Pimpri", chain="Independent", proj="Digital", sound="Basic", tags=["Heritage"]),
 "Vasant (Budhwar Peth)": dict(area="Budhwar Peth", chain="Independent", proj="Digital", sound="Basic", tags=["Heritage"]),
 "Alaka Talkies": dict(area="Sadashiv Peth", chain="Independent", proj="Digital", sound="Basic", tags=["Heritage"]),
}
PROJ_PTS = {"4K Laser":25,"Barco RGB 4K Laser":25,"Laser":22,"4K":18,"Digital":8,"2K":10,"2K Xenon":10}
SOUND_PTS = {"64-ch Dolby Atmos":25,"Dolby Atmos":20,"Dolby 7.1":12,"Dolby Digital":10,"Basic":5}
CLS_PTS = {"plf":18,"luxury":10,"standard":6,"single":2}

rows = list(csv.DictReader(open("pune-screens-estimated.csv")))
areas = [float(r["area_sqft"]) for r in rows]
amax, amin = max(areas), min(areas)
screens = []
for r in rows:
    v = r["venue"]; t = TECH[v]
    a = float(r["area_sqft"]); seats = int(r["seats"])
    w, h = float(r["width_ft"]), float(r["height_ft"])
    size_pts = 30 * (a - amin) / (amax - amin)
    special = 0
    if "Dolby Cinema" in r["screen"]: special = 7
    if r["screen"] == "IMAX" and "Laser" in t["proj"]: special = 7
    if r["screen"] == "EPIQ": special = 6
    score = size_pts + PROJ_PTS[t["proj"]] + SOUND_PTS[t["sound"]] + CLS_PTS[r["class"]] + special
    nrows = max(3, round(math.sqrt(seats) / 1.35))
    per_row = max(4, round(seats / nrows))
    best_row = min(nrows, max(1, round((1.2 * w - 0.4 * w) / 3.6) + 1))
    best_seat = math.ceil(per_row / 2)
    row_letter = chr(64 + best_row) if best_row <= 26 else str(best_row)
    screens.append(dict(v=v, s=r["screen"], cls=r["class"], area=t["area"], chain=t["chain"],
        proj=t["proj"], snd=t["sound"], tags=t["tags"], seats=seats, w=w, h=h,
        conf=r["dimension_confidence"], score=score, rows=nrows, pr=per_row, brn=best_row,
        br=row_letter, bs=best_seat, rel=round(a / (sum(areas)/len(areas)), 2)))
mx = max(s["score"] for s in screens)
for s in screens: s["score"] = round(s["score"] / mx * 100, 1)
screens.sort(key=lambda x: -x["score"])
data = json.dumps(screens, separators=(",", ":"))

# ---------------- TOP 10 with REAL seat layouts ----------------
# layout rows are FRONT-to-BACK; each row: [letter, [[nSeats, class], ...]]
# classes: cl classic, cp classic+, pr prime, pp picture-perfect, p+ prime plus,
#          xl XL, el extra-legroom, rc recliner, ry royal recliner, sf sofa, gd gold, sv silver
def R(l, segs): return [l, segs]
TOP10 = [
 dict(id="wakad_imax", v="INOX Megaplex, Phoenix Mall of the Millennium", s="IMAX", area="Wakad",
  tech="IMAX XT 4K Laser · Dolby Atmos · 1.90:1", w=60,h=33,conf="verified (KDCloudy)", seats=262,
  lay=[R("L",[[17,"cl"]]),R("K",[[21,"cl"]]),R("J",[[4,"cp"],[17,"cp"],[4,"cp"]]),R("I",[[4,"cp"],[17,"cp"],[4,"cp"]]),
       R("H",[[4,"pr"],[17,"pr"],[4,"pr"]]),R("G",[[4,"pr"],[17,"pr"],[4,"pr"]]),
       R("F",[[4,"pr"],[17,"pp"],[4,"pr"]]),R("E",[[4,"pr"],[17,"pp"],[4,"pr"]]),
       R("D",[[4,"pr"],[17,"pp"],[4,"pr"]]),R("C",[[4,"pr"],[17,"pp"],[4,"pr"]]),
       R("B",[[16,"rc"]]),R("A",[[2,"rc"],[6,"rc"]])],
  best=dict(row="D",seat=13,label="Row D · Seat 13 — dead centre of the Picture Perfect block"),
  avoid="Recliner rows A–B sit too deep for the 1.90:1 frame; row L is neck-crane territory.",
  playing=[["The Odyssey (IMAX 2D)","Shot 100% on IMAX film cameras — this screen is its home turf"]]),
 dict(id="epiq", v="E-Square EPIQ, Hinjawadi Ph 2", s="EPIQ", area="Hinjawadi",
  tech="Barco RGB 4K Laser · 64-ch Dolby Atmos · 1.89:1 wall-to-wall", w=59,h=31,conf="published (Qube)", seats=310,
  lay=[R(chr(65+i),[[22,"pr"]]) for i in range(14)],
  best=dict(row="G",seat=11,label="Row G · Seat 11 — the 64-channel Atmos sweet spot"),
  avoid="Nothing yet — opened Mar 2026, Pune's newest premium hall.",
  playing=[["Spider-Man: Brand New Day","First Hollywood film mastered for EPIQ; expanded 1.90 frame edge-to-edge"]]),
 dict(id="dolby", v="City Pride Kharadi", s="Audi 6 — Dolby Cinema", area="Kharadi",
  tech="Dual Christie 4K RGB Laser · Dolby Vision · 61-ch Atmos · 2.1:1", w=55,h=26.2,conf="fan-measured (Shrey Tyagi + KDCloudy)", seats=310,
  lay=[R("A",[[22,"cl"]]),R("B",[[22,"cl"]]),R("C",[[22,"cl"]]),R("D",[[22,"xl"]]),R("E",[[22,"xl"]]),R("F",[[22,"xl"]]),R("G",[[22,"xl"]]),
       R("H",[[22,"pr"]]),R("J",[[22,"pr"]]),R("K",[[22,"pr"]]),R("L",[[22,"pr"]]),R("M",[[22,"pr"]]),R("N",[[22,"pr"]]),R("P",[[12,"sf"]])],
  best=dict(row="J",seat=11,label="Row J · Seat 11 — centre of the Dolby Vision + Atmos field"),
  avoid="Rear 'sofa' row seats are ordinary, not recliners — pay for position, not the name.",
  playing=[["Spider-Man: Brand New Day","Called the #1 way to watch it in India with IMAX locked out"]]),
 dict(id="westend_imax", v="Cinepolis Nexus Westend Mall", s="IMAX", area="Aundh",
  tech="IMAX Dual Xenon 2K · 1.90:1 — oldest IMAX tech in the city", w=55,h=31,conf="verified (KDCloudy)", seats=283,
  lay=[R(chr(65+i),[[19,"cl"]]) for i in range(5)]+[R(c,[[20,"pr"]]) for c in "FGHIJKLMN"]+[R("O",[[8,"rc"]])],
  best=dict(row="H",seat=10,label="Row H · Seat 10 — mid-hall centre"),
  avoid="Row O recliners: a divider rod sits in your sightline (real complaint). 'LieMAX' rep — Wakad beats it.",
  playing=[["The Odyssey (IMAX 2D)","Same film as Wakad but on 2K xenon — go Wakad if you can"]]),
 dict(id="pxl", v="PVR Grand Highstreet, Hinjawadi", s="P[XL]", area="Hinjawadi",
  tech="4K Laser · Dolby Atmos · flat wall-to-wall", w=50,h=27,conf="recalculated from real seat map", seats=401,
  lay=[R("A",[[25,"cl"]]),R("B",[[6,"cl"],[14,"cl"],[6,"cl"]])]+
      [R(c,[[6,"pr"],[14,"pr"],[6,"pr"]]) for c in "CDEFGHJK"]+
      [R("L",[[6,"el"],[14,"el"],[6,"el"]]),R("M",[[6,"p+"],[15,"p+"],[6,"p+"]]),R("N",[[6,"p+"],[15,"p+"],[6,"p+"]]),
       R("P",[[5,"p+"],[13,"p+"],[5,"p+"]]),R("Q",[[5,"p+"],[13,"p+"],[5,"p+"]]),
       R("R",[[4,"rc"],[4,"rc"],[4,"rc"],[4,"rc"]])],
  best=dict(row="L",seat=13,label="Row L · Seat 13 — the Extra Legroom row; PVR literally built the sweet spot"),
  avoid="Rows A–C put a 50-ft screen in your lap. 401 seats — book the centre early.",
  playing=[["The Odyssey (P[XL])","Big-canvas epic on the wall-to-wall flat screen"],["Spider-Man 3D (P[XL])","Expanded 1.90 frame fills the flat screen"]]),
 dict(id="kothrud1", v="City Pride Kothrud", s="Audi 1", area="Kothrud",
  tech="4K · Dolby Atmos (renovated) · Gold/Silver", w=52,h=24,conf="model-estimated", seats=527,
  lay=[R(c,[[31,"sv"]]) for c in "ABCDEFGH"]+[R(c,[[31,"gd"]]) for c in "IJKLMNPQR"],
  best=dict(row="M",seat=16,label="Row M · Seat 16 — Gold class centre in Maharashtra's first multiplex"),
  avoid="Silver front rows under a 525-seat hall's rake. No recliners anywhere.",
  playing=[["Dhamaal 4","Gold-class crowd-pleaser energy"]]),
 dict(id="esq5", v="E-Square University Road", s="Screen 5", area="University Rd",
  tech="4K projector · Dolby 7.1 · 584 seats — Pune's biggest hall", w=54,h=24.5,conf="model-estimated", seats=584,
  lay=[R(c,[[32,"sv"]]) for c in "ABCDEFGHIJ"]+[R(c,[[33,"gd"]]) for c in "KLMNPQRS"],
  best=dict(row="M",seat=17,label="Row M · Seat 17 — Gold centre with 583 other people roaring"),
  avoid="2003-era hall: sit Gold centre or don't bother.",
  playing=[["Mass entertainers","584 seats of single-screen energy in a multiplex shell"]]),
 dict(id="icon", v="PVR ICON, The Pavillion Mall", s="Flagship Audi (263)", area="SB Road",
  tech="4K · Dolby Atmos · ICON premium", w=40,h=18,conf="recalculated from real seat map", seats=263,
  lay=[R("A",[[10,"cl"],[10,"cl"]]),R("B",[[10,"cl"],[10,"cl"]])]+
      [R(c,[[10,"pr"],[10,"pr"]]) for c in "CDEFGHJ"]+
      [R("K",[[10,"p+"],[10,"p+"]]),R("L",[[10,"p+"],[10,"p+"]]),R("M",[[9,"p+"],[10,"p+"]]),R("N",[[10,"p+"]]),R("P",[[14,"rc"]])],
  best=dict(row="J",seat=10,label="Row J · Seat 10 — centre aisle-side of the Prime block"),
  avoid="Row N is half-width beside the entrance vomitory — light spill on late arrivals.",
  playing=[["Spider-Man 3D","Prime-time 3D shows run here"],["Dhamaal 4","Comfort pick"]]),
 dict(id="ice", v="PVR Director's Cut, KOPA Mall", s="ICE Theatre", area="Koregaon Park",
  tech="4K Laser · Dolby Atmos · LED side panels · scope screen", w=33,h=14,conf="recalculated from real seat map", seats=184,
  lay=[R(c,[[12,"pr"],[4,"pr"]]) for c in "ABCDEFG"]+
      [R("H",[[12,"p+"],[4,"p+"]]),R("J",[[12,"p+"],[4,"p+"]]),R("K",[[12,"p+"],[6,"p+"]]),R("L",[[11,"p+"],[11,"p+"]])],
  best=dict(row="F",seat=7,label="Row F · Seat 7 — where the LED side panels wrap your peripheral vision"),
  avoid="Last row L: the side-panel effect fades at the back.",
  playing=[["Spider-Man (ICE 2D)","5 shows a day — the panels sell the swing shots"]]),
 dict(id="insignia", v="INOX Megaplex, Phoenix MoM", s="Insignia", area="Wakad",
  tech="4K Laser · Dolby Atmos · every seat a Royal Recliner", w=30,h=16,conf="recalculated from real seat map", seats=49,
  lay=[R("E",[[9,"ry"]]),R("D",[[9,"ry"]]),R("C",[[9,"ry"]]),R("B",[[11,"ry"]]),R("A",[[11,"ry"]])],
  best=dict(row="B",seat=6,label="Row B · Seat 6 — but honestly, all 49 are recliners"),
  avoid="Nothing. That's the point of paying for Insignia.",
  playing=[["Cocktail 2","Dialogue drama + recliner = correct"],["The Odyssey (Insignia)","3 hours is a recliner film"]]),
]
top10 = json.dumps(TOP10, separators=(",", ":"))

PAIR = json.dumps([
 dict(m="The Odyssey", g="Nolan epic · shot on IMAX film", pick="INOX Megaplex Wakad — IMAX", why="The only Pune screen doing justice to full-frame IMAX photography. Laser, 60-ft, Atmos.", alt="Westend IMAX (xenon) · P[XL] Hinjawadi · Director's Cut KOPA"),
 dict(m="Spider-Man: Brand New Day", g="Superhero · expanded 1.90 frame · no IMAX in India", pick="City Pride Kharadi — Dolby Cinema", why="With IMAX locked by The Odyssey, the dual-laser Dolby Vision hall is the #1 way to see it in India.", alt="E-Square EPIQ (mastered for it) · 4DX Marketcity for the ride · ICE KOPA"),
 dict(m="Dhamaal 4", g="Comedy", pick="INOX Megaplex Wakad — Insignia", why="Comedies don't need 60-ft screens; they need recliners and popcorn service.", alt="City Pride Kothrud Gold · Rajhans recliners"),
 dict(m="Evil Dead Burn", g="Horror", pick="Cinepolis Seasons — 4DX", why="Horror + motion seats + air blasts = the jump-scare multiplier.", alt="Director's Cut KOPA late show"),
 dict(m="Cocktail 2", g="Romance/drama", pick="INOX Bund Garden — Insignia", why="Dialogue film. Buy comfort, not canvas.", alt="Director's Cut KOPA · MovieMax Gold"),
], separators=(",", ":"))


html = open("app_template.html").read()
os.makedirs("punescreens", exist_ok=True)
out = html.replace("__DATA__", data).replace("__TOP10__", top10).replace("__PAIR__", PAIR)
open("punescreens/index.html","w").write(out)
open("punescreens/netlify.toml","w").write('[build]\n  publish = "."\n')
open("punescreens/README.md","w").write("# PuneScreens\n\nKnow your screen. Pune's halls, ranked - with the best seat in every one.\n\nStatic single-file app. Deploy: drag folder to https://app.netlify.com/drop or import repo in Netlify (no build command, publish dir `.`).\n")
print("built v4:", os.path.getsize("punescreens/index.html")//1024, "KB")
