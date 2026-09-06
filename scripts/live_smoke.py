#!/usr/bin/env python3
"""30-point post-deploy smoke test for the public DAI/2 GitHub Pages site."""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from urllib.parse import urljoin

BASE = "https://ricmurtapsicologia.github.io/efetivoDAI2/"
RANKS = ["Sd/Cb", "Sgt/SubTen", "Ten", "Cap", "Maj", "Ten-Cel"]


def fetch(path: str, timeout: int = 20) -> tuple[int, str]:
    url = urljoin(BASE, path)
    sep = "&" if "?" in url else "?"
    req = urllib.request.Request(url + sep + f"smoke={int(time.time())}", headers={"User-Agent": "DAI2-live-smoke/2.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return int(resp.status), resp.read().decode("utf-8")


def assignment(text: str, name: str):
    m = re.search(rf"window\.{re.escape(name)}\s*=\s*(.*?);(?:\r?\n|$)", text, re.S)
    if not m:
        raise AssertionError(f"window.{name} não encontrado")
    return json.loads(m.group(1))


def classify(rank: str) -> str | None:
    v = str(rank or "").lower().replace("º", "").strip()
    if "ten cel" in v or "ten-cel" in v or v == "cel": return "Ten-Cel"
    if v.startswith("maj"): return "Maj"
    if v.startswith("cap"): return "Cap"
    if "sub ten" in v or "subten" in v or "sgt" in v: return "Sgt/SubTen"
    if "ten" in v: return "Ten"
    if v.startswith("cb") or v.startswith("sd"): return "Sd/Cb"
    return None


def main() -> int:
    # Wait briefly for Pages/CDN convergence after a main push.
    last_error = None
    for _ in range(18):
        try:
            s, live_data = fetch("data/data.js?v=2.0.0")
            if s == 200 and '"version":"2.0.0"' in live_data:
                break
        except Exception as exc:  # pragma: no cover - network convergence
            last_error = exc
        time.sleep(5)
    else:
        print(f"FAIL: Pages não convergiu para v2.0.0: {last_error}")
        return 1

    index_status, index = fetch("")
    data_status, live_data = fetch("data/data.js?v=2.0.0")
    tpb_status, live_tpb = fetch("data/tpb.js?v=2026.09.03")
    app_status, app = fetch("assets/js/app.js?v=2.0.0")
    css_status, css = fetch("assets/css/main.css?v=2.0.0")

    meta = assignment(live_data, "DAI2_META")
    ddqod = assignment(live_data, "DAI2_DDQOD")
    personnel = assignment(live_data, "DAI2_PERSONNEL")
    tpb_meta = assignment(live_tpb, "DAI_TPB_META")
    rows = assignment(live_tpb, "DAI_TPB_ROWS")
    tpb = [
        {"rank":r[0], "name":r[1], "lotacao":r[2], "status":r[3], "dispensa":bool(r[4]),
         "cycle":r[5], "participation":r[6], "dateToConfirm":bool(r[7]), "history":r[8]}
        for r in rows
    ]

    planned = sum(sum(int(grades.get(rank, 0) or 0) for rank in RANKS) for grades in ddqod.values())
    by_org = Counter(p["org"] for p in personnel)
    claro = 0
    excess = 0
    for org, grades in ddqod.items():
        existing = Counter(classify(p["rank"]) for p in personnel if p["org"] == org)
        for rank in RANKS:
            p = int(grades.get(rank, 0) or 0)
            e = int(existing.get(rank, 0) or 0)
            claro += max(p - e, 0)
            if org != "SEMAD":
                excess += max(e - p, 0)

    done = sum(1 for r in tpb if r["status"] == "feito")
    not_done = len(tpb) - done
    dispensed = sum(1 for r in tpb if r["dispensa"])
    actionable = sum(1 for r in tpb if r["status"] != "feito" and not r["dispensa"])
    date_to_confirm = sum(1 for r in tpb if r["status"] == "feito" and r["dateToConfirm"])

    tests = [
        ("01 URL pública responde HTTP 200", index_status == 200),
        ("02 título v2 correto", "<title>DAI/2 · Efetivo e TPB 2026</title>" in index),
        ("03 viewport mobile-first presente", "viewport-fit=cover" in index),
        ("04 CSS v2 referenciado", "assets/css/main.css?v=2.0.0" in index),
        ("05 data.js v2 referenciado", "data/data.js?v=2.0.0" in index),
        ("06 TPB 03/09 referenciado", "data/tpb.js?v=2026.09.03" in index),
        ("07 app.js v2 referenciado", "assets/js/app.js?v=2.0.0" in index),
        ("08 runtime-updates não é carregado", "runtime-updates.js" not in index),
        ("09 data.js público responde 200", data_status == 200),
        ("10 metadado da versão é 2.0.0", meta.get("version") == "2.0.0"),
        ("11 Nº BM não está na base pública", '"number":' not in live_data and "Nr BM" not in live_data),
        ("12 telefone não está na base pública", '"phone":' not in live_data),
        ("13 aniversários não estão na base pública", "DAI2_BIRTHDAYS" not in live_data),
        ("14 DDQOD é parseável e possui órgãos", isinstance(ddqod, dict) and len(ddqod) >= 18),
        ("15 previsto DDQOD = 101", planned == 101),
        ("16 base nominal pública é parseável", isinstance(personnel, list)),
        ("17 efetivo existente = 84", len(personnel) == 84),
        ("18 SEMAD previsto = 0", sum(int(ddqod.get("SEMAD", {}).get(r, 0) or 0) for r in RANKS) == 0),
        ("19 SEMAD possui 1 extra-DDQOD", by_org.get("SEMAD", 0) == 1),
        ("20 Silvana está na AFAS", any(p["name"] == "Silvana Tiengo" and p["org"] == "AFAS" for p in personnel)),
        ("21 Claro DDQOD por P/G = 23", claro == 23),
        ("22 excedentes em P/G DDQOD = 5", excess == 5),
        ("23 tpb.js público responde 200", tpb_status == 200),
        ("24 corte TPB = 03/09/2026", tpb_meta.get("cutoff") == "03/09/2026"),
        ("25 escopo TPB DAI = 85", len(tpb) == 85),
        ("26 TPB feito = 69", done == 69),
        ("27 TPB não feito = 16", not_done == 16),
        ("28 dispensas definitivas = 9", dispensed == 9),
        ("29 exigem ação = 7 e data a conferir = 15", actionable == 7 and date_to_confirm == 15),
        ("30 app/CSS respondem e gates de UI estão no bundle", app_status == 200 and css_status == 200 and ".innerHTML" not in app and "prefers-reduced-motion" in css and "mobile-nav" in css),
    ]

    failed = [name for name, ok in tests if not ok]
    for name, ok in tests:
        print(f"{'PASS' if ok else 'FAIL'} | {name}")
    print(f"RESULTADO: {len(tests)-len(failed)}/{len(tests)}")
    if failed:
        print("FALHAS:")
        for item in failed: print(f"- {item}")
        return 1
    print("SMOKE PÚBLICO: APROVADO 30/30")
    return 0


if __name__ == "__main__":
    sys.exit(main())
