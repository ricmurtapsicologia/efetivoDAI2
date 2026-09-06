#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RANKS = ['Sd/Cb', 'Sgt/SubTen', 'Ten', 'Cap', 'Maj', 'Ten-Cel']
ALLOWED_PERSONNEL = {'rank','name','org','subunit'}

def extract_assignment(path: Path, variable: str):
    text = path.read_text(encoding='utf-8')
    match = re.search(rf"window\.{re.escape(variable)}\s*=\s*(.*?);(?:\r?\n|$)", text, re.S)
    if not match:
        raise AssertionError(f'{path}: window.{variable} não encontrado')
    return json.loads(match.group(1))

def classify(rank: str):
    v = str(rank or '').lower().replace('º','').strip()
    if 'ten cel' in v or 'ten-cel' in v or v == 'cel': return 'Ten-Cel'
    if v.startswith('maj'): return 'Maj'
    if v.startswith('cap'): return 'Cap'
    if 'sub ten' in v or 'subten' in v or 'sgt' in v: return 'Sgt/SubTen'
    if 'ten' in v: return 'Ten'
    if v.startswith('cb') or v.startswith('sd'): return 'Sd/Cb'
    return None

def main() -> int:
    errors = []
    data_path = ROOT/'data'/'data.js'
    tpb_path = ROOT/'data'/'tpb.js'
    index = (ROOT/'index.html').read_text(encoding='utf-8')
    css = (ROOT/'assets'/'css'/'main.css').read_text(encoding='utf-8')
    app = (ROOT/'assets'/'js'/'app.js').read_text(encoding='utf-8')

    try:
        meta = extract_assignment(data_path,'DAI2_META')
        ddqod = extract_assignment(data_path,'DAI2_DDQOD')
        personnel = extract_assignment(data_path,'DAI2_PERSONNEL')
        tpb_meta = extract_assignment(tpb_path,'DAI_TPB_META')
        try:
            tpb = extract_assignment(tpb_path,'DAI_TPB')
        except Exception:
            rows = extract_assignment(tpb_path,'DAI_TPB_ROWS')
            tpb = [dict(rank=r[0],name=r[1],lotacao=r[2],status=r[3],dispensa=bool(r[4]),cycle=r[5],participation=r[6],dateToConfirm=bool(r[7]),history=r[8]) for r in rows]
    except Exception as exc:
        print(f'FATAL: {exc}')
        return 1

    for i,row in enumerate(personnel,1):
        extra = set(row)-ALLOWED_PERSONNEL
        if extra:
            errors.append(f'personnel row {i}: campos não permitidos {sorted(extra)}')
        if not all(str(row.get(k,'')).strip() for k in ('rank','name','org')):
            errors.append(f'personnel row {i}: campos obrigatórios vazios')
    if len({str(r['name']).casefold() for r in personnel}) != len(personnel):
        errors.append('nomes duplicados no efetivo')
    public_data_text = data_path.read_text(encoding='utf-8')
    if '"number":' in public_data_text:
        errors.append('campo number/Nº BM detectado na camada pública')
    if '"phone":' in public_data_text or 'DAI2_BIRTHDAYS' in public_data_text:
        errors.append('telefone/aniversário detectado na camada pública')

    planned = sum(sum(int(g.get(r,0) or 0) for r in RANKS) for g in ddqod.values())
    if planned != 101:
        errors.append(f'DDQOD previsto = {planned}, esperado 101')
    if len(personnel) != 84:
        errors.append(f'efetivo = {len(personnel)}, esperado 84')
    if sum(int(ddqod.get('SEMAD',{}).get(r,0) or 0) for r in RANKS) != 0:
        errors.append('SEMAD não pode criar vaga prevista no DDQOD consultado')

    by_org = Counter(r['org'] for r in personnel)
    claro = 0
    excess_non_semad = 0
    for org,grades in ddqod.items():
        ex = Counter(classify(r['rank']) for r in personnel if r['org']==org)
        for rank in RANKS:
            p = int(grades.get(rank,0) or 0)
            e = int(ex.get(rank,0) or 0)
            claro += max(p-e,0)
            if org != 'SEMAD':
                excess_non_semad += max(e-p,0)
    if claro != 23:
        errors.append(f'claro por P/G = {claro}, esperado 23')
    if excess_non_semad != 5:
        errors.append(f'excedentes em P/G do DDQOD = {excess_non_semad}, esperado 5')
    if by_org.get('SEMAD',0) != 1:
        errors.append('SEMAD deve ter 1 militar extra-DDQOD')

    done = sum(1 for r in tpb if r.get('status')=='feito')
    not_done = len(tpb)-done
    dispensed = sum(1 for r in tpb if r.get('dispensa'))
    actionable = sum(1 for r in tpb if r.get('status')!='feito' and not r.get('dispensa'))
    date_to_confirm = sum(1 for r in tpb if r.get('status')=='feito' and r.get('dateToConfirm'))
    expected = tpb_meta.get('expected',{})
    observed = {'scope':len(tpb),'done':done,'notDone':not_done,'dispensed':dispensed,'actionable':actionable,'dateToConfirm':date_to_confirm}
    for key,val in observed.items():
        if int(expected.get(key,-1)) != val:
            errors.append(f'TPB {key} = {val}, esperado {expected.get(key)}')

    tpb_text = tpb_path.read_text(encoding='utf-8')
    if re.search(r'/20(?:27|28|29)', tpb_text):
        errors.append('ano divergente de 2026 propagado no histórico TPB')
    if int(tpb_meta.get('sourceWarnings', 0)) != 4:
        errors.append(f'avisos de qualidade TPB = {tpb_meta.get("sourceWarnings")}, esperado 4')

    if 'runtime-updates.js' in index:
        errors.append('index ainda carrega runtime-updates.js')
    if 'chart.js' in index.lower() or 'chart.js' in app.lower():
        errors.append('dependência Chart.js ainda presente')
    if re.search(r'https?://[^"\']+\.(?:jpg|jpeg|png|webp)', index+css, re.I):
        errors.append('imagem remota obrigatória detectada')
    if '.innerHTML' in app:
        errors.append('uso de innerHTML detectado no app')
    if 'const safeStorage' not in app or "safeStorage.get('dai2_help_seen_v2')" not in app:
        errors.append('persistência resiliente do onboarding ausente')
    if 'prefers-reduced-motion' not in css:
        errors.append('prefers-reduced-motion ausente')
    if 'viewport-fit=cover' not in index:
        errors.append('viewport mobile/safe-area incompleto')
    if 'mobile-nav' not in index or 'mobile-nav' not in css:
        errors.append('navegação mobile-first ausente')
    if '<dialog' not in index:
        errors.append('diálogos nativos/acessíveis ausentes')
    if 'data/tpb.js' not in index:
        errors.append('fonte TPB não carregada')
    if 'Pesquisar militar por nome, Nr BM' in index:
        errors.append('placeholder ainda oferece busca por Nº BM')
    if '2.0.0' not in index:
        errors.append('cache/versionamento v2.0.0 ausente')

    payload = {
        'ok': not errors,
        'version': meta.get('version'),
        'ddqod_planned': planned,
        'personnel': len(personnel),
        'claro_pg': claro,
        'excess_pg_ddqod': excess_non_semad,
        'semad_extra_ddqod': by_org.get('SEMAD',0),
        'tpb': observed,
        'errors': errors,
    }
    print(json.dumps(payload,ensure_ascii=False,indent=2))
    return 0 if not errors else 1

if __name__ == '__main__':
    sys.exit(main())
