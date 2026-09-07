#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RANKS = ['Sd/Cb','Sgt/SubTen','Ten','Cap','Maj','Ten-Cel']
ALLOWED_PERSONNEL = {'rank','name','org','subunit'}
EXPECTED_TPB = {'scope':85,'done':69,'notDone':16,'dispensed':9,'actionable':7,'dateToConfirm':15}
BANNED_FRONTEND = [
    'BGBM a localizar', 'Ato de movimentação', 'A vincular', 'A localizar',
    'base interna autorizada', 'neutralizados na camada executiva',
    'Rastreabilidade: data/período da evidência a recuperar', 'addTrace(',
    'DAI2_CONTACTS', 'DAI2_EMAILS', 'DAI2_BIRTHDAYS', 'mailto:'
]
PRIVATE_PUBLIC_FILES = [
    ROOT/'data'/'contacts.js',
    ROOT/'data'/'emails.js',
    ROOT/'assets'/'js'/'email-actions.js',
]


def extract_assignment(path: Path, variable: str):
    text = path.read_text(encoding='utf-8')
    match = re.search(rf"window\.{re.escape(variable)}\s*=\s*(.*?);(?:\r?\n|$)", text, re.S)
    if not match:
        raise AssertionError(f'{path}: window.{variable} não encontrado')
    return json.loads(match.group(1))


def classify(rank: str):
    value = str(rank or '').lower().replace('º','').strip()
    if 'ten cel' in value or 'ten-cel' in value or value == 'cel': return 'Ten-Cel'
    if value.startswith('maj'): return 'Maj'
    if value.startswith('cap'): return 'Cap'
    if 'sub ten' in value or 'subten' in value or 'sgt' in value: return 'Sgt/SubTen'
    if 'ten' in value: return 'Ten'
    if value.startswith('cb') or value.startswith('sd'): return 'Sd/Cb'
    return None


def main() -> int:
    errors = []
    data_path = ROOT/'data'/'data.js'
    tpb_path = ROOT/'data'/'tpb.js'
    index = (ROOT/'index.html').read_text(encoding='utf-8')
    css = (ROOT/'assets'/'css'/'main.css').read_text(encoding='utf-8')
    app = (ROOT/'assets'/'js'/'app.js').read_text(encoding='utf-8')

    try:
        meta = extract_assignment(data_path, 'DAI2_META')
        ddqod = extract_assignment(data_path, 'DAI2_DDQOD')
        personnel = extract_assignment(data_path, 'DAI2_PERSONNEL')
        tpb_meta = extract_assignment(tpb_path, 'DAI_TPB_META')
        tpb_rows = extract_assignment(tpb_path, 'DAI_TPB_ROWS')
    except Exception as exc:
        print(f'FATAL: {exc}')
        return 1

    for index_row, row in enumerate(personnel, 1):
        extra = set(row) - ALLOWED_PERSONNEL
        if extra:
            errors.append(f'personnel row {index_row}: campos não permitidos {sorted(extra)}')
        if not all(str(row.get(key, '')).strip() for key in ('rank','name','org')):
            errors.append(f'personnel row {index_row}: campos obrigatórios vazios')
    if len({str(row['name']).casefold() for row in personnel}) != len(personnel):
        errors.append('nomes duplicados no efetivo')
    public_data = data_path.read_text(encoding='utf-8')
    if '"number":' in public_data:
        errors.append('Nº BM detectado na camada pública')

    for private_path in PRIVATE_PUBLIC_FILES:
        if private_path.exists():
            errors.append(f'arquivo pessoal não permitido na camada pública: {private_path.relative_to(ROOT)}')
    if tpb_rows:
        errors.append(f'TPB nominal publicado: {len(tpb_rows)} registro(s); esperado 0')
    frontend = '\n'.join((index, app, tpb_path.read_text(encoding='utf-8')))
    for phrase in BANNED_FRONTEND:
        if phrase in frontend:
            errors.append(f'dado/ação privada no frontend público: {phrase}')
    if re.search(r'https://wa\.me/(?:\+?55)?\d', frontend):
        errors.append('WhatsApp com número de destinatário embutido no frontend público')

    planned = sum(sum(int(grades.get(rank,0) or 0) for rank in RANKS) for grades in ddqod.values())
    by_org = Counter(row['org'] for row in personnel)
    claro = 0
    excess = 0
    for org, grades in ddqod.items():
        existing = Counter(classify(row['rank']) for row in personnel if row['org'] == org)
        for rank in RANKS:
            planned_rank = int(grades.get(rank,0) or 0)
            existing_rank = int(existing.get(rank,0) or 0)
            claro += max(planned_rank - existing_rank, 0)
            if org != 'SEMAD':
                excess += max(existing_rank - planned_rank, 0)
    if planned != 101: errors.append(f'DDQOD previsto={planned}, esperado 101')
    if len(personnel) != 84: errors.append(f'efetivo={len(personnel)}, esperado 84')
    if by_org.get('SEMAD',0) != 1: errors.append('SEMAD deve ter 1 extra-DDQOD')
    if sum(int(ddqod.get('SEMAD',{}).get(rank,0) or 0) for rank in RANKS) != 0:
        errors.append('SEMAD não pode ter vaga prevista no DDQOD consultado')
    if claro != 23: errors.append(f'claro P/G={claro}, esperado 23')
    if excess != 5: errors.append(f'excedente P/G DDQOD={excess}, esperado 5')

    observed_tpb = {key:int(tpb_meta.get('expected',{}).get(key,-1)) for key in EXPECTED_TPB}
    for key, expected in EXPECTED_TPB.items():
        if observed_tpb[key] != expected:
            errors.append(f'TPB agregado {key}={observed_tpb[key]}, esperado {expected}')

    required_layout = [
        'id="splash"','id="onboarding"','class="banner"','class="container"',
        'class="general-data"','class="color-legend"','class="row"','class="block"',
        'id="militaryList"','id="modal"','id="normasModal"','id="tpbModal"'
    ]
    for token in required_layout:
        if token not in index: errors.append(f'layout original ausente: {token}')
    if index.count('class="block"') != 18:
        errors.append(f'layout original: {index.count("class=\"block\"")} blocos, esperado 18')
    if 'mobile-nav' in index or 'section-card' in index or 'org-grid' in index:
        errors.append('redesign estrutural detectado; layout original deve ser preservado')
    if re.search(r'<div class="numbers">\s*Previsto:', index):
        errors.append('dados de efetivo duplicados/hardcoded no HTML dos blocos')
    if 'Total Previsto: 101' in index or 'Total Existente: 84' in index or 'Total Claro: 23' in index:
        errors.append('totais canônicos duplicados/hardcoded no HTML')

    required_refs = [
        'data/tpb.js?v=2026.09.06-public',
        'assets/js/app.js?v=2.4.0',
        'assets/css/main.css?v=2.2.0'
    ]
    if any(ref not in index for ref in required_refs):
        errors.append('versionamento/referências do frontend incompletos')
    forbidden_refs = ['data/contacts.js','data/emails.js','assets/js/email-actions.js']
    if any(ref in index for ref in forbidden_refs):
        errors.append('referência a dados pessoais ainda presente no index')
    if 'runtime-updates.js' in index: errors.append('runtime-updates ainda carregado')
    if 'chart.js' in index.lower() or 'chart.js' in app.lower(): errors.append('Chart.js ainda é dependência')
    if 'Nr BM' in index: errors.append('UI ainda oferece Nº BM')
    if '.innerHTML' in app: errors.append('innerHTML detectado')
    if 'const safeStorage' not in app or 'dai2_onboarding_seen_v3' not in app:
        errors.append('persistência resiliente do onboarding v3 ausente')
    if 'prefers-reduced-motion' not in css: errors.append('prefers-reduced-motion ausente')
    if 'viewport-fit=cover' not in index: errors.append('viewport-fit=cover ausente')
    if 'class="skip-link"' not in index: errors.append('skip-link ausente')
    if 'role="dialog"' not in index or 'close-button' not in index: errors.append('modal acessível incompleto')
    if 'aria-haspopup="dialog"' not in index: errors.append('gatilhos de modal sem aria-haspopup')
    if 'aria-expanded="false"' not in index: errors.append('controles expansíveis sem aria-expanded inicial')
    if 'function trapFocus' not in app: errors.append('focus trap dos modais ausente')
    if "setAttribute('inert'" not in app: errors.append('isolamento do conteúdo de fundo dos modais ausente')
    if 'Proteção de dados' in index or 'birthdayPanel' in index or 'Privacidade da camada pública' in index:
        errors.append('bloco visual de privacidade deveria estar removido')
    if 'Claro calculado por posto/graduação' in app:
        errors.append('texto explicativo de claro deveria estar removido')
    if 'https://wa.me/?text=' not in app or 'whatsapp-action' not in app:
        errors.append('ação WhatsApp por militar ausente')
    if 'Situação do TPB 2026' not in index or 'tpb-overview' not in app:
        errors.append('TPB intuitivo 2.4 incompleto')
    if 'photo-1521737711867-e3b97375f902' not in css:
        errors.append('hero corporativo de alta resolução ausente')

    payload = {
        'ok': not errors,
        'version': meta.get('version'),
        'interface': '2.4.0',
        'layout': 'original-preserved-refined',
        'public_contacts': 'not-embedded',
        'whatsapp_action': 'per-person-share-without-public-number',
        'ddqod_planned': planned,
        'personnel': len(personnel),
        'claro_pg': claro,
        'excess_pg_ddqod': excess,
        'semad_extra_ddqod': by_org.get('SEMAD',0),
        'tpb_aggregate': observed_tpb,
        'errors': errors,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    sys.exit(main())
