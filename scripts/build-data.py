#!/usr/bin/env python3
"""Build US Open 2026 men's and women's 128-player catalogs.

Sources (see scripts/sources/):
  - Wikipedia wikitext for the 2026 US Open men's/women's singles draws
  - ATP/WTA rankings of Monday 24 August 2026 (TennisUpToDate / livetennis.eu)
  - ESPN ATP/WTA lists of 27 August 2026 for ages and players outside the top-100 snapshot
  - Wikipedia seed lists for 2025 US Open and 2026 AO / RG / Wimbledon
  - Wikipedia 2026 ATP Tour and 2026 WTA Tour for notable titles

Odds are a form-weighted desk model (last 12 months, hard-court bump), not betting lines.
Percents in each draw sum to 100. Eliminated players are 0%; remaining mass is renormalized.
Missing stats are stored as null and rendered as an em dash in the UI.
"""

from __future__ import annotations

import json
import math
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "scripts" / "sources"
OUT = ROOT / "public" / "data"

FLAG_COUNTRY = {
    "GER": "Germany",
    "ESP": "Spain",
    "CAN": "Canada",
    "SRB": "Serbia",
    "ITA": "Italy",
    "AUS": "Australia",
    "USA": "United States",
    "FRA": "France",
    "CZE": "Czechia",
    "NOR": "Norway",
    "MON": "Monaco",
    "ARG": "Argentina",
    "CHI": "Chile",
    "BEL": "Belgium",
    "GBR": "Great Britain",
    "PER": "Peru",
    "KAZ": "Kazakhstan",
    "BUL": "Bulgaria",
    "POR": "Portugal",
    "NED": "Netherlands",
    "POL": "Poland",
    "GRE": "Greece",
    "HUN": "Hungary",
    "SVK": "Slovakia",
    "JPN": "Japan",
    "CRO": "Croatia",
    "PAR": "Paraguay",
    "HKG": "Hong Kong",
    "CHN": "China",
    "SUI": "Switzerland",
    "ROU": "Romania",
    "PHI": "Philippines",
    "UKR": "Ukraine",
    "LAT": "Latvia",
    "AUT": "Austria",
    "COL": "Colombia",
    "MEX": "Mexico",
    "DEN": "Denmark",
    "EGY": "Egypt",
    "TUR": "Turkey",
    "INA": "Indonesia",
    "THA": "Thailand",
    "UZB": "Uzbekistan",
    "KOR": "South Korea",
    "TPE": "Chinese Taipei",
    "BRA": "Brazil",
    "RSA": "South Africa",
}

# Wikipedia often omits a flag for athletes competing as neutrals.
EMPTY_FLAG_COUNTRY = {
    "aryna sabalenka": "Belarus",
    "daniil medvedev": "Russia",
    "andrey rublev": "Russia",
    "mirra andreeva": "Russia",
    "diana shnaider": "Russia",
    "anna kalinskaya": "Russia",
    "ekaterina alexandrova": "Russia",
    "roman safiullin": "Russia",
    "polina iatcenko": "Russia",
    "kristina liutova": "Russia",
    "anastasia zakharova": "Russia",
}

ALIASES = {
    "xin wang": "xinyu wang",
    "wang xinyu": "xinyu wang",
    "xiy wang": "xiyu wang",
    "wang xiyu": "xiyu wang",
    "ka pliskova": "karolina pliskova",
    "cys lee": "carol young suh lee",
    "jj wolf": "j j wolf",
    "j. j. wolf": "j j wolf",
    "alex eala": "alexandra eala",
    "darja vidmanova": "darja vidmanova",
    "ludmilla samsonova": "liudmila samsonova",
    "mccartney kessler": "mccartney kessler",
    "catherine mcnally": "caty mcnally",
    "chak lam coleman wong": "coleman wong",
    "tommy paul (tennis)": "tommy paul",
    "ann li (tennis)": "ann li",
    "shang juncheng": "juncheng shang",
    "alexander shevchenko": "aleksandr shevchenko",
    "daniel vallejo": "adolfo daniel vallejo",
    "ad vallejo": "adolfo daniel vallejo",
    "yuliia starodubtseva": "yulia starodubtseva",
    "martin damm (born 2003)": "martin damm",
}

RESULT_CANON = {
    "champion": "W",
    "winner": "W",
    "final": "F",
    "runner-up": "F",
    "semifinals": "SF",
    "semifinal": "SF",
    "quarterfinals": "QF",
    "quarterfinal": "QF",
    "fourth round": "R16",
    "third round": "R32",
    "second round": "R64",
    "first round": "R128",
    "withdrew": "WD",
}

HARD_TITLES = {
    "men": {
        "Carlos Alcaraz": ["2025 US Open", "2026 Australian Open"],
        "Jannik Sinner": ["2026 Indian Wells", "2026 Miami Open"],
        "Alex de Minaur": ["2026 Rotterdam"],
        "Daniil Medvedev": ["2026 Dubai"],
        "Ben Shelton": ["2026 Canadian Open"],
        "Arthur Fils": ["2026 Cincinnati"],
    },
    "women": {
        "Aryna Sabalenka": ["2025 US Open", "2026 Brisbane", "2026 Indian Wells", "2026 Miami Open"],
        "Elena Rybakina": ["2026 Australian Open"],
        "Jessica Pegula": ["2026 Dubai"],
        "Coco Gauff": ["2026 Cincinnati"],
        "Iga Świątek": ["2026 Canadian Open"],
        "Elina Svitolina": ["2026 Auckland"],
        "Mirra Andreeva": ["2026 Adelaide"],
        "Elisabetta Cocciaretto": ["2026 Hobart"],
    },
}

OTHER_TITLES = {
    "men": {
        "Alexander Zverev": ["2026 French Open"],
        "Jannik Sinner": ["2026 Monte-Carlo", "2026 Madrid", "2026 Rome", "2026 Wimbledon"],
    },
    "women": {
        "Mirra Andreeva": ["2026 French Open"],
        "Linda Nosková": ["2026 Berlin", "2026 Wimbledon"],
        "Karolína Muchová": ["2026 Doha"],
        "Elina Svitolina": ["2026 Rome"],
        "Marta Kostyuk": ["2026 Madrid"],
        "Madison Keys": ["2026 Eastbourne"],
    },
}

CURATED_NOTES = {
    "Carlos Alcaraz": "Defending champion. First singles appearance in over four months after a wrist injury at Barcelona; missed Roland Garros and Wimbledon.",
    "Alexander Zverev": "No. 1 seed after Jannik Sinner withdrew with a right-knee injury. 2026 French Open champion and Wimbledon finalist.",
    "Novak Djokovic": "Eliminated in the first round by Mariano Navone — his first US Open opening-round loss. Physically ailing late in the five-setter.",
    "Mariano Navone": "Upset No. 4 Novak Djokovic in five sets on Arthur Ashe Stadium.",
    "Arthur Fils": "Arrives as the Cincinnati champion at a career-high ranking.",
    "Flavio Cobolli": "2026 French Open runner-up; first Masters 1000 semifinal in Cincinnati.",
    "Stan Wawrinka": "Final major appearance. 2016 US Open champion, in on a late wildcard.",
    "Gaël Monfils": "Final major appearance; wildcard.",
    "Arthur Fery": "Reached the 2026 Wimbledon semifinals as a wildcard.",
    "Grigor Dimitrov": "Came through qualifying; ranking has slid after an injury-hit stretch.",
    "Rafael Jódar": "Teenager seeded at a major after a sharp ranking rise.",
    "Learner Tien": "Australian Open quarterfinalist; still a teenager.",
    "Cameron Norrie": "Eliminated in the first round by Luca Van Assche.",
    "Aryna Sabalenka": "Two-time defending champion and world No. 1. Won Indian Wells and Miami in 2026; Australian Open runner-up. No. 1 ranking is on the line.",
    "Elena Rybakina": "2026 Australian Open champion. Retired from her Cincinnati quarterfinal with injury; fitness watch. Reaching the semifinals would lock No. 1.",
    "Jessica Pegula": "Cincinnati runner-up and Dubai champion. Can take No. 1 only by winning the title with Rybakina losing before the semifinals.",
    "Coco Gauff": "Cincinnati champion and 2023 US Open winner. Wimbledon semifinalist. Same No. 1 path as Pegula.",
    "Mirra Andreeva": "2026 French Open champion, still 19.",
    "Linda Nosková": "2026 Wimbledon champion, still 21.",
    "Karolína Muchová": "2026 Wimbledon runner-up.",
    "Iga Świątek": "Canadian Open champion. Lost the 2026 Wimbledon title in the third round.",
    "Amanda Anisimova": "2025 US Open runner-up.",
    "Venus Williams": "Age 46 wildcard; oldest woman in the US Open singles main draw since 1981.",
    "Sofia Kenin": "Wildcard. Beat Venus Williams in the latest-start match in tournament history.",
    "Kristina Liutova": "Qualifier. First woman born in the 2010s to play a major singles main draw.",
    "Maja Chwalińska": "French Open runner-up as a qualifier in June; now seeded.",
    "Sára Bejlek": "Cincinnati semifinalist after beating Sabalenka; top-30 debut.",
    "Alexandra Eala": "Highest Grand Slam seeding ever for a player from the Philippines.",
    "Zheng Qinwen": "Came through qualifying after a ranking drop.",
    "Thea Frodin": "Wildcard from the USTA Girls' 18s National Championship; opens against Rybakina.",
    "Barbora Krejčíková": "Eliminated in the first round by Kamilla Rakhimova.",
    "Loïs Boisson": "Entered on a protected ranking.",
    "Aoi Ito": "Entered on a protected ranking.",
    "Mananchaya Sawangkaew": "Entered on a protected ranking (Victoria Mboko withdrew with a left-knee injury).",
    "Nadia Podoroska": "Entered on a protected ranking.",
    "Juncheng Shang": "Entered on a protected ranking.",
    "Thanasi Kokkinakis": "Entered on a protected ranking.",
    "Filip Misolic": "Entered on a protected ranking.",
    "Carlos Taberner": "Entered on a protected ranking after Sinner's withdrawal.",
}


def fold(name: str) -> str:
    name = name.replace("\u00a0", " ").strip()
    name = unicodedata.normalize("NFKD", name)
    name = "".join(ch for ch in name if not unicodedata.combining(ch))
    name = name.lower()
    name = name.replace(".", " ")
    name = re.sub(r"\s+", " ", name)
    name = re.sub(r"\s*\(tennis\)\s*", " ", name)
    name = re.sub(r"\s*\(born \d{4}\)\s*", " ", name)
    name = name.strip()
    return ALIASES.get(name, name)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def index_rankings(payload: dict) -> dict[str, dict]:
    out = {}
    for name, rank, points, country in payload["players"]:
        out[fold(name)] = {
            "name": name,
            "rank": rank,
            "points": points,
            "country": country,
            "source": payload["asOf"],
        }
    return out


def parse_seed_results(path: Path) -> dict[str, str]:
    text = path.read_text()
    results: dict[str, str] = {}
    # Seed lines look like: 1. Carlos Alcaraz(champion) 2. Jannik Sinner(semifinals)
    for m in re.finditer(
        r"\d+\.\s+([A-ZÁÉÍÓÚÄÖÜČĆŠŽŁÑ][^0-9(]{1,60}?)\s*\(([^)]+)\)",
        text,
    ):
        raw_name = m.group(1).strip()
        raw_name = re.sub(r"\s+", " ", raw_name)
        result = m.group(2).split(",")[0].strip().lower()
        # skip "withdrew due to..." only keeping the round token
        token = None
        for key, canon in RESULT_CANON.items():
            if result.startswith(key):
                token = canon
                break
        if token is None and "withdrew" in result:
            token = "WD"
        if token and fold(raw_name) not in {"click on the seed number of a player to go to their draw section"}:
            results[fold(raw_name)] = token
    # Champion/runner-up infobox as backup
    champ = re.search(r"Champion\s*\|\s*(?:[A-Za-z ]+\s+)?\[?\[?([^\]\n|]+)", text)
    runner = re.search(r"Runner-up\s*\|\s*(?:[A-Za-z ]+\s+)?\[?\[?([^\]\n|]+)", text)
    if champ:
        results.setdefault(fold(champ.group(1)), "W")
    if runner:
        results.setdefault(fold(runner.group(1)), "F")
    return results


def wiki_link_name(team: str) -> str:
    link = re.search(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", team)
    if not link:
        return re.sub(r"[{}'\[\]]", "", team).strip()
    name = link.group(1).strip()
    name = re.sub(r"\s*\(tennis\)\s*", "", name)
    name = re.sub(r"\s*\(born \d{4}\)\s*", "", name)
    return name.strip()


def parse_draw(wikitext: str, best_of: int) -> list[dict]:
    sections = re.split(r"\{\{16TeamBracket-Compact-Tennis[35]", wikitext)
    players: list[dict] = []
    global_slot = 0
    for section in sections[1:]:
        end = section.find("\n}}")
        body = section[: end if end != -1 else None]
        by_idx: dict[int, dict] = {}
        for m in re.finditer(r"\|\s*RD1-seed(\d{2})\s*=([^\n]*)", body):
            by_idx.setdefault(int(m.group(1)), {})["seed"] = m.group(2).strip()
        for m in re.finditer(r"\|\s*RD1-team(\d{2})\s*=([^\n]*)", body):
            by_idx.setdefault(int(m.group(1)), {})["team"] = m.group(2).strip()
        for m in re.finditer(r"\|\s*RD1-score(\d{2})-(\d+)\s*=([^\n]*)", body):
            by_idx.setdefault(int(m.group(1)), {}).setdefault("scores", {})[
                int(m.group(2))
            ] = m.group(3).strip()
        rd2: dict[int, str] = {}
        for m in re.finditer(r"\|\s*RD2-team(\d{2})\s*=([^\n]*)", body):
            raw = m.group(2).strip()
            name = wiki_link_name(raw) if "[[" in raw else ""
            if name:
                rd2[int(m.group(1))] = name
        for idx in range(1, 17):
            row = by_idx.get(idx, {})
            team = row.get("team", "")
            flag_m = re.search(r"\{\{flagicon\|([^}]*)\}\}", team)
            flag = (flag_m.group(1) if flag_m else "").strip()
            name = wiki_link_name(team)
            scores = row.get("scores", {})
            has_score = any(re.sub(r"['\s]", "", v) for v in scores.values())
            players.append(
                {
                    "slot": global_slot,
                    "section": (global_slot // 16) + 1,
                    "pair": global_slot // 2,
                    "seed_raw": row.get("seed", ""),
                    "name": name,
                    "flag": flag,
                    "bold": "'''" in team,
                    "has_score": has_score,
                    "rd2_names": rd2,
                }
            )
            global_slot += 1
    if len(players) != 128:
        raise SystemExit(f"expected 128 players, got {len(players)}")
    # Resolve R1 outcomes
    for pair in range(64):
        a, b = players[pair * 2], players[pair * 2 + 1]
        winner = None
        if a["bold"] and not b["bold"]:
            winner = a
        elif b["bold"] and not a["bold"]:
            winner = b
        else:
            for cand in (a, b):
                if any(fold(cand["name"]) == fold(n) for n in a["rd2_names"].values()):
                    winner = cand
                    break
        a_opp, b_opp = b["name"], a["name"]
        if winner is a:
            a["status"] = "still_in"
            b["status"] = "eliminated"
            a["r1_result"] = "W"
            b["r1_result"] = "L"
        elif winner is b:
            b["status"] = "still_in"
            a["status"] = "eliminated"
            b["r1_result"] = "W"
            a["r1_result"] = "L"
        elif a["has_score"] or b["has_score"]:
            a["status"] = b["status"] = "still_in"
            a["r1_result"] = b["r1_result"] = "in_progress"
        else:
            a["status"] = b["status"] = "not_yet_played"
            a["r1_result"] = b["r1_result"] = None
        a["r1_opponent"] = a_opp
        b["r1_opponent"] = b_opp
    # Next opponent: R1 opponent until that match is over; then R2 opponent or winner-of.
    for pair in range(64):
        a, b = players[pair * 2], players[pair * 2 + 1]
        other_pair = pair ^ 1
        oa, ob = players[other_pair * 2], players[other_pair * 2 + 1]
        r2_known = None
        if oa["status"] == "still_in" and oa.get("r1_result") == "W" and ob["status"] == "eliminated":
            r2_known = oa["name"]
        elif ob["status"] == "still_in" and ob.get("r1_result") == "W" and oa["status"] == "eliminated":
            r2_known = ob["name"]
        for p in (a, b):
            if p["status"] == "eliminated":
                p["next_opponent"] = None
            elif p.get("r1_result") == "W":
                p["next_opponent"] = r2_known or f"Winner of {oa['name']} vs {ob['name']}"
            else:
                p["next_opponent"] = p["r1_opponent"]
    return players


def parse_entry(seed_raw: str) -> tuple[int | None, str | None]:
    raw = seed_raw.strip()
    if raw.isdigit():
        return int(raw), None
    if raw in {"Q", "WC", "LL", "PR"}:
        return None, raw
    return None, None


def lookup(table: dict, name: str, extra: dict | None = None):
    key = fold(name)
    if key in table:
        return table[key]
    if extra and key in extra:
        return extra[key]
    # last-name, first-name swap for "Wang Xinyu"
    parts = key.split()
    if len(parts) == 2:
        swapped = fold(f"{parts[1]} {parts[0]}")
        if swapped in table:
            return table[swapped]
        if extra and swapped in extra:
            return extra[swapped]
    return None


def gs_label(code: str | None) -> str | None:
    return {
        "W": "W",
        "F": "F",
        "SF": "SF",
        "QF": "QF",
        "R16": "R16",
        "R32": "R32",
        "R64": "R64",
        "R128": "R128",
        "WD": "WD",
    }.get(code or "")


def rating_for(player: dict, tour: str) -> float:
    """Compressed form rating so a 7-round bracket stays in desk-model range.

    Rank points (24 Aug 2026) are the spine. Last-12-month Grand Slam results
    get a hard-court bump (US Open 2025, Australian Open 2026). This is not Elo
    used by ATP/WTA and not a betting line.
    """
    points = player.get("rankPoints")
    if not points:
        rank = player["rank"] or 180
        points = max(40.0, 2200.0 / rank)
    elo = 1380.0 + 255.0 * math.log10(points + 100.0)
    bonuses = {"W": 32, "F": 18, "SF": 10, "QF": 5, "R16": 2, "R32": 1, "R64": 0, "R128": 0, "WD": 0}
    gs = player["snapshot"]
    for key, mult in (
        ("uso2025", 1.35),
        ("ao2026", 1.35),
        ("rg2026", 0.80),
        ("wimbledon2026", 0.88),
    ):
        elo += bonuses.get(gs.get(key) or "", 0) * mult
    titles = gs.get("titles") or []
    hard_keys = {fold(k): v for k, v in HARD_TITLES.get(tour, {}).items()}
    other_keys = {fold(k): v for k, v in OTHER_TITLES.get(tour, {}).items()}
    hard = hard_keys.get(fold(player["name"])) or []
    other = other_keys.get(fold(player["name"])) or []
    elo += 8 * len([t for t in titles if t in hard])
    elo += 4 * len([t for t in titles if t in other])
    if fold(player["name"]) in {fold("Carlos Alcaraz"), fold("Aryna Sabalenka")}:
        elo += 22  # defending US Open champion
    if fold(player["name"]) == fold("Aryna Sabalenka"):
        elo += 28  # two-time defending on this hard court
    if fold(player["name"]) == fold("Carlos Alcaraz"):
        elo -= 18  # four-month wrist layoff; missed RG and Wimbledon
    if fold(player["name"]) == fold("Alexander Zverev"):
        elo += 22  # No. 1 seed, French Open champion, full schedule
    if fold(player["name"]) == fold("Elena Rybakina"):
        elo -= 18  # Cincinnati quarterfinal retirement
    if player["entry"] == "Q":
        elo -= 6
    if player["entry"] == "LL":
        elo -= 8
    if player["entry"] == "WC" and fold(player["name"]) not in {
        fold("Stan Wawrinka"),
        fold("Gaël Monfils"),
        fold("Sofia Kenin"),
        fold("Venus Williams"),
        fold("Sloane Stephens"),
    }:
        elo -= 8
    if player["age"] and player["age"] >= 39:
        elo -= 6
    if player["age"] and player["age"] <= 17:
        elo -= 4
    return elo


def beat_prob(elo_a: float, elo_b: float, best_of: int) -> float:
    # Wider scale = less favorite-heavy through seven rounds.
    scale = 470.0 if best_of == 5 else 420.0
    return 1.0 / (1.0 + 10 ** ((elo_b - elo_a) / scale))


def title_probs(players: list[dict], elos: list[float], best_of: int) -> list[float]:
    n = len(players)
    eliminated = {i for i, p in enumerate(players) if p["status"] == "eliminated"}

    def subtree(start: int, end: int) -> dict[int, float]:
        if end - start == 1:
            i = start
            return {i: 0.0 if i in eliminated else 1.0}
        mid = (start + end) // 2
        left = subtree(start, mid)
        right = subtree(mid, end)
        out: dict[int, float] = {}
        left_mass = sum(left.values())
        right_mass = sum(right.values())

        def side_out(own: dict[int, float], opp: dict[int, float], opp_mass: float) -> None:
            for i, pi in own.items():
                if pi == 0.0:
                    out[i] = 0.0
                    continue
                if opp_mass == 0.0:
                    out[i] = pi  # walkover; the other half is already out
                    continue
                acc = 0.0
                for j, pj in opp.items():
                    if pj == 0.0:
                        continue
                    acc += pj * beat_prob(elos[i], elos[j], best_of)
                out[i] = pi * acc

        side_out(left, right, right_mass)
        side_out(right, left, left_mass)
        return out

    raw = subtree(0, n)
    probs = [raw[i] for i in range(n)]
    for i in eliminated:
        probs[i] = 0.0
    total = sum(probs)
    if total <= 0:
        raise SystemExit("all probabilities vanished")
    probs = [p / total for p in probs]
    # Round to 2 decimals summing to 100.00; eliminated stay 0.00
    pcts = [0.0 if i in eliminated else round(p * 100.0, 2) for i, p in enumerate(probs)]
    live = [i for i in range(n) if i not in eliminated]
    drift = round(100.0 - sum(pcts), 2)
    # Fix rounding drift on the current favorite among remaining players
    if live:
        fav = max(live, key=lambda i: pcts[i])
        pcts[fav] = round(pcts[fav] + drift, 2)
    return pcts


def notes_for(p: dict, tour: str) -> str:
    bits: list[str] = []
    curated = CURATED_NOTES.get(p["name"])
    if curated:
        bits.append(curated)
    if p["entry"] == "Q" and "qualif" not in " ".join(bits).lower():
        bits.append("Reached the main draw through qualifying.")
    if p["entry"] == "WC" and "wildcard" not in " ".join(bits).lower():
        bits.append("Entered on a wildcard.")
    if p["entry"] == "LL":
        bits.append("Entered as a lucky loser.")
    if p["entry"] == "PR" and "protected" not in " ".join(bits).lower():
        bits.append("Entered on a protected ranking.")
    if p["status"] == "eliminated" and p.get("r1_opponent"):
        line = f"Eliminated in the first round by {p['r1_opponent']}."
        if line not in " ".join(bits):
            bits.append(line)
    if p["status"] == "still_in" and p.get("r1_result") == "W":
        bits.append("Through to the second round.")
    if p["age"] is not None and p["age"] >= 39 and "Age" not in " ".join(bits):
        bits.append(f"Age {p['age']}.")
    if p["age"] is not None and p["age"] <= 17 and "2010s" not in " ".join(bits):
        bits.append(f"Age {p['age']}.")
    if p["rank"] is not None and p["rank"] <= 40 and p["seed"] is None and p["entry"] is None:
        bits.append("Unseeded inside the ranking band used for the draw.")
    text = " ".join(bits).strip()
    return text or ""


def build_catalog(tour: str) -> dict:
    best_of = 5 if tour == "men" else 3
    wiki = (SRC / f"wiki-2026-us-open-{tour}s-singles.wikitext").read_text()
    draw = parse_draw(wiki, best_of)
    rank_file = SRC / ("atp-rankings-2026-08-24.json" if tour == "men" else "wta-rankings-2026-08-24.json")
    espn_file = SRC / ("espn-atp-2026-08-27.json" if tour == "men" else "espn-wta-2026-08-27.json")
    ranks = index_rankings(load_json(rank_file))
    espn = load_json(espn_file)
    ages = {fold(k): v for k, v in espn["ages"].items() if v is not None}
    extra_ranks = {fold(k): v for k, v in espn.get("ranks", {}).items()}
    wiki_pr = {
        "men": {
            "juncheng shang": 56,
            "thanasi kokkinakis": 84,
            "filip misolic": 101,
            "carlos taberner": 107,
        },
        "women": {
            "lois boisson": 38,
            "aoi ito": 87,
            "mananchaya sawangkaew": 100,
            "nadia podoroska": 106,
        },
    }[tour]
    wiki_ages = {
        "venus williams": 46,  # Wikipedia 2026 US Open women's singles
    }
    gs = {
        "uso2025": parse_seed_results(SRC / "gs" / f"2025-uso-{tour}.md"),
        "ao2026": parse_seed_results(SRC / "gs" / f"2026-ao-{tour}.md"),
        "rg2026": parse_seed_results(SRC / "gs" / f"2026-rg-{tour}.md"),
        "wimbledon2026": parse_seed_results(SRC / "gs" / f"2026-wimbledon-{tour}.md"),
    }
    hard_titles = HARD_TITLES[tour]
    other_titles = OTHER_TITLES[tour]

    catalog_players = []
    for p in draw:
        seed, entry = parse_entry(p["seed_raw"])
        r = lookup(ranks, p["name"])
        rank = r["rank"] if r else extra_ranks.get(fold(p["name"])) or wiki_pr.get(fold(p["name"]))
        points = r["points"] if r else None
        country = None
        if p["flag"]:
            country = FLAG_COUNTRY.get(p["flag"], p["flag"])
        elif r:
            country = r["country"]
        else:
            country = EMPTY_FLAG_COUNTRY.get(fold(p["name"]))
        age = ages.get(fold(p["name"])) or wiki_ages.get(fold(p["name"]))
        titles: list[str] = []
        key = fold(p["name"])
        for k, v in HARD_TITLES[tour].items():
            if fold(k) == key:
                titles.extend(v)
        for k, v in OTHER_TITLES[tour].items():
            if fold(k) == key:
                titles.extend(v)
        titles = list(dict.fromkeys(titles))
        snap = {
            "wlOverall": None,
            "wlHard": None,
            "titles": titles,
            "uso2025": gs_label(gs["uso2025"].get(fold(p["name"]))),
            "ao2026": gs_label(gs["ao2026"].get(fold(p["name"]))),
            "rg2026": gs_label(gs["rg2026"].get(fold(p["name"]))),
            "wimbledon2026": gs_label(gs["wimbledon2026"].get(fold(p["name"]))),
            "notes": "",
        }
        # Alcaraz missed RG and Wimbledon
        if fold(p["name"]) == fold("Carlos Alcaraz"):
            snap["rg2026"] = snap["rg2026"] or "WD"
            snap["wimbledon2026"] = snap["wimbledon2026"] or "WD"
        player = {
            "id": re.sub(r"[^a-z0-9]+", "-", fold(p["name"])).strip("-"),
            "name": p["name"],
            "country": country,
            "countryCode": p["flag"] or None,
            "seed": seed,
            "entry": entry,
            "age": age,
            "rank": rank,
            "rankPoints": points,
            "status": p["status"],
            "nextOpponent": p.get("next_opponent"),
            "r1Opponent": p.get("r1_opponent"),
            "slot": p["slot"],
            "snapshot": snap,
        }
        catalog_players.append(player)

    elos = [rating_for(pl, tour) for pl in catalog_players]
    odds = title_probs(catalog_players, elos, best_of)
    for pl, pct in zip(catalog_players, odds):
        pl["titleOdds"] = pct
        pl["snapshot"]["notes"] = notes_for(pl, tour)

    catalog_players_sorted = sorted(
        catalog_players, key=lambda x: (-x["titleOdds"], x["slot"])
    )
    s = round(sum(p["titleOdds"] for p in catalog_players_sorted), 2)
    zeros = [p for p in catalog_players_sorted if p["status"] == "eliminated"]
    if any(p["titleOdds"] != 0 for p in zeros):
        raise SystemExit("eliminated player has non-zero odds")
    if abs(s - 100.0) > 0.01:
        raise SystemExit(f"{tour} odds sum to {s}, not 100")
    if len({p["name"] for p in catalog_players_sorted}) != 128:
        raise SystemExit("duplicate or missing names")

    return {
        "draw": "men" if tour == "men" else "women",
        "event": "2026 US Open",
        "generatedAt": "2026-08-31",
        "rankingsDate": "2026-08-24",
        "modelNote": "form-weighted, last 12 months, hard-court bump, not betting odds",
        "sources": [
            "Wikipedia: 2026 US Open men's and women's singles draws (retrieved 31 Aug 2026)",
            "ATP/WTA rankings of Monday 24 August 2026",
            "ESPN ATP/WTA rankings of 27 August 2026 (ages; players outside the 24 Aug top 100)",
            "Wikipedia: 2025 US Open, 2026 Australian Open, 2026 French Open, 2026 Wimbledon seed lists",
            "Wikipedia: 2026 ATP Tour and 2026 WTA Tour title tables",
        ],
        "players": catalog_players_sorted,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for tour, filename in (("men", "men.json"), ("women", "women.json")):
        catalog = build_catalog(tour)
        (OUT / filename).write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n")
        top = catalog["players"][:6]
        elim = sum(1 for p in catalog["players"] if p["status"] == "eliminated")
        nyp = sum(1 for p in catalog["players"] if p["status"] == "not_yet_played")
        print(f"{tour}: 128 players, odds={sum(p['titleOdds'] for p in catalog['players']):.2f}, eliminated={elim}, not_yet_played={nyp}")
        for p in top:
            print(f"  {p['titleOdds']:6.2f}%  {p['name']}  ({p['status']})")


if __name__ == "__main__":
    main()
