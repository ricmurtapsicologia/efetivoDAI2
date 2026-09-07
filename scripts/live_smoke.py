#!/usr/bin/env python3
"""30-point post-deploy smoke: layout, invariantes, WhatsApp, a11y e UX."""
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
RANKS = ["Sd/Cb","Sgt/SubTen","Ten","Cap","Maj","Ten-Cel"]
BANNED = [
    "BGBM a localizar","Ato de movimentação","A vincular","A localizar",
    "base interna autorizada","neutralizados na camada executiva",
    "Rastreabilidade: data/período da evidência a recuperar","addTrace(",
    "DAI2_EMAILS","DAI2_BIRTHDAYS","mailto:"
]


def fetch(path, timeout=20):
    url = urljoin(BASE, path)
    sep = "&" if "?" in url else "?"
    req = urllib.request.Request(url + sep + f"smoke={int(time.time())}", headers={"User-Agent":"DAI2-live-smoke/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return int(response.status), response.read().decode("utf-8")


def fetch_status(path, timeout=20):
    try:
        status, _ = fetch(path, timeout=timeout)
        return status
    except urllib.error.HTTPError as exc:
        return int(exc.code)
    except Exception:
        return 0


def assignment(text, name):
    match = re.search(rf"window\.{re.escape(name)}\s*=\s*(.*?);(?:\r?\n|$)", text, re.S)
    if not match:
        raise AssertionError(name)
    return json.loads(match.group(1))


def normalize_phone(raw):
    digits = re.sub(r'\D', '', str(raw or ''))
    if digits.startswith('55') and len(digits) >= 12:
        digits = digits[2:]
    if len(digits) == 10:
        digits = digits[:2] + '9' + digits[2:]
    return '55' + digits if len(digits) == 11 else ''


def classify(rank):
    value = str(rank or '').lower().replace('º','').strip()
    if 'ten cel' in value or 'ten-cel' in value or value == 'cel': return 'Ten-Cel'
    if value.startswith('maj'): return 'Maj'
    if value.startswith('cap'): return 'Cap'
    if 'sub ten' in value or 'subten' in value or 'sgt' in value: return 'Sgt/SubTen'
    if 'ten' in value: return 'Ten'
    if value.startswith('cb') or value.startswith('sd'): return 'Sd/Cb'
    return None


def main():
    last = None
    for _ in range(30):
        try:
            status, index = fetch("")
            if status == 200 and 'assets/js/app.js?v=2.5.0' in index and 'data/contacts.js?v=2026.09.07' in index and 'class="banner"' in index:
                break
        except Exception as exc:
            last = exc
        time.sleep(5)
    else:
        print(f"FAIL: Pages não convergiu para interface 2.5.0: {last}")
        return 1

    index_status, index = fetch("")
    data_status, data = fetch("data/data.js?v=2.0.0")
    contacts_status, contacts_text = fetch("data/contacts.js?v=2026.09.07")
    tpb_status, tpb_text = fetch("data/tpb.js?v=2026.09.06-public")
    app_status, app = fetch("assets/js/app.js?v=2.5.0")
    css_status, css = fetch("assets/css/main.css?v=2.3.0")
    hero_status, hero_text = fetch("assets/hero-source.json")

    ddqod = assignment(data, "DAI2_DDQOD")
    personnel = assignment(data, "DAI2_PERSONNEL")
    contacts = assignment(contacts_text, "DAI2_CONTACTS")
    contacts_meta = assignment(contacts_text, "DAI2_CONTACTS_META")
    tpb_meta = assignment(tpb_text, "DAI_TPB_META")
    tpb_rows = assignment(tpb_text, "DAI_TPB_ROWS")
    hero_meta = json.loads(hero_text)

    planned = sum(sum(int(grades.get(rank,0) or 0) for rank in RANKS) for grades in ddqod.values())
    by_org = Counter(person["org"] for person in personnel)
    claro = 0
    excess = 0
    for org, grades in ddqod.items():
        existing = Counter(classify(person["rank"]) for person in personnel if person["org"] == org)
        for rank in RANKS:
            planned_rank = int(grades.get(rank,0) or 0)
            existing_rank = int(existing.get(rank,0) or 0)
            claro += max(planned_rank-existing_rank, 0)
            if org != "SEMAD":
                excess += max(existing_rank-planned_rank, 0)

    expected = tpb_meta.get("expected", {})
    names = {person['name'] for person in personnel}
    contact_names = set(contacts)
    valid_contacts = all(normalize_phone(raw) for raw in contacts.values())
    silvana_phone = normalize_phone(contacts.get('Silvana Tiengo'))
    hero_id = 'photo-1778876087506-47da0c3e6d98'
    frontend = index + "\n" + app + "\n" + contacts_text + "\n" + tpb_text

    tests = [
      ("01 URL pública responde HTTP 200", index_status == 200),
      ("02 layout original: splash presente", 'id="splash"' in index),
      ("03 layout original: onboarding presente", 'id="onboarding"' in index),
      ("04 hero corporativo governado presente", hero_id in css and hero_status == 200 and hero_id in hero_meta.get('image_url','')),
      ("05 layout original: container presente", 'class="container"' in index),
      ("06 layout original: dados gerais presente", 'class="general-data"' in index),
      ("07 bloco visual de privacidade removido", 'birthdayPanel' not in index and 'Proteção de dados' not in index and 'Privacidade da camada pública' not in index),
      ("08 layout original: 18 blocos", index.count('class="block"') == 18),
      ("09 redesign estrutural removido", 'mobile-nav' not in index and 'section-card' not in index and 'org-grid' not in index),
      ("10 CSS 2.3 carregado", css_status == 200 and 'assets/css/main.css?v=2.3.0' in index),
      ("11 app 2.5 carregado", app_status == 200 and 'assets/js/app.js?v=2.5.0' in index),
      ("12 diretório WhatsApp carregado", contacts_status == 200 and 'data/contacts.js?v=2026.09.07' in index and contacts_meta.get('display') == 'public'),
      ("13 cobertura WhatsApp = 84/84", len(contacts) == 84 and contact_names == names and valid_contacts),
      ("14 WhatsApp direto de Silvana normaliza corretamente", silvana_phone == '5531991743862'),
      ("15 ação WhatsApp direta no app", 'normalizeWhatsApp' in app and 'https://wa.me/${phone}?text=' in app and 'whatsapp-number' in app),
      ("16 e-mail/aniversário não publicados", 'DAI2_EMAILS' not in frontend and 'DAI2_BIRTHDAYS' not in frontend and 'mailto:' not in frontend),
      ("17 texto técnico de claro removido", 'Claro calculado por posto/graduação' not in app),
      ("18 previsto DDQOD = 101", planned == 101),
      ("19 efetivo = 84", len(personnel) == 84),
      ("20 SEMAD previsto 0 e extra-DDQOD 1", sum(int(ddqod["SEMAD"].get(rank,0) or 0) for rank in RANKS) == 0 and by_org.get("SEMAD",0) == 1),
      ("21 Silvana está na AFAS", any(person["name"] == "Silvana Tiengo" and person["org"] == "AFAS" for person in personnel)),
      ("22 Claro P/G = 23", claro == 23),
      ("23 excedente P/G DDQOD = 5", excess == 5),
      ("24 TPB carregado e redesenhado", tpb_status == 200 and not tpb_rows and 'Situação do TPB 2026' in index and 'tpb-overview' in app),
      ("25 corte TPB = 03/09/2026", tpb_meta.get("cutoff") == "03/09/2026"),
      ("26 escopo TPB = 85", int(expected.get("scope",-1)) == 85),
      ("27 TPB concluído = 69", int(expected.get("done",-1)) == 69),
      ("28 não concluído = 16 / dispensas = 9", int(expected.get("notDone",-1)) == 16 and int(expected.get("dispensed",-1)) == 9),
      ("29 exigem ação = 7 / sem data = 15", int(expected.get("actionable",-1)) == 7 and int(expected.get("dateToConfirm",-1)) == 15),
      ("30 a11y/UX/limite estrutural", not any(term in frontend for term in BANNED) and '.innerHTML' not in app and 'prefers-reduced-motion' in css and 'viewport-fit=cover' in index and 'role="dialog"' in index and 'class="skip-link"' in index and 'function trapFocus' in app and 'aria-expanded="false"' in index and not re.search(r'<div class="numbers">\s*Previsto:', index)),
    ]

    failed = [name for name, ok in tests if not ok]
    for name, ok in tests:
        print(f"{'PASS' if ok else 'FAIL'} | {name}")
    print(f"RESULTADO: {30-len(failed)}/30")
    if failed:
        print("FALHAS:")
        for item in failed:
            print("-", item)
        return 1
    print("SMOKE PÚBLICO: APROVADO 30/30 — UI 2.5, WhatsApp direto visível e hero governado")
    return 0


if __name__ == "__main__":
    sys.exit(main())
