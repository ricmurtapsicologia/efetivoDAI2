#!/usr/bin/env python3
from __future__ import annotations

import json, re, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RANKS = ['Sd/Cb','Sgt/SubTen','Ten','Cap','Maj','Ten-Cel']
ALLOWED_PERSONNEL = {'rank','name','org','subunit'}
BANNED_FRONTEND = [
    'BGBM a localizar', 'Ato de movimentação', 'A vincular', 'A localizar',
    'base interna autorizada', 'neutralizados na camada executiva',
    'Rastreabilidade: data/período da evidência a recuperar', 'addTrace('
]

def extract_assignment(path: Path, variable: str):
    text = path.read_text(encoding='utf-8')
    m = re.search(rf"window\.{re.escape(variable)}\s*=\s*(.*?);(?:\r?\n|$)", text, re.S)
    if not m:
        raise AssertionError(f'{path}: window.{variable} não encontrado')
    return json.loads(m.group(1))

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
    errors=[]
    data_path=ROOT/'data'/'data.js'
    contacts_path=ROOT/'data'/'contacts.js'
    tpb_path=ROOT/'data'/'tpb.js'
    index=(ROOT/'index.html').read_text(encoding='utf-8')
    css=(ROOT/'assets'/'css'/'main.css').read_text(encoding='utf-8')
    app=(ROOT/'assets'/'js'/'app.js').read_text(encoding='utf-8')

    try:
        meta=extract_assignment(data_path,'DAI2_META')
        ddqod=extract_assignment(data_path,'DAI2_DDQOD')
        personnel=extract_assignment(data_path,'DAI2_PERSONNEL')
        contacts=extract_assignment(contacts_path,'DAI2_CONTACTS')
        birthdays=extract_assignment(contacts_path,'DAI2_BIRTHDAYS')
        tpb_meta=extract_assignment(tpb_path,'DAI_TPB_META')
        rows=extract_assignment(tpb_path,'DAI_TPB_ROWS')
        tpb=[dict(rank=r[0],name=r[1],lotacao=r[2],status=r[3],dispensa=bool(r[4]),cycle=r[5],participation=r[6],dateToConfirm=bool(r[7]),history=r[8]) for r in rows]
    except Exception as exc:
        print(f'FATAL: {exc}')
        return 1

    for i,row in enumerate(personnel,1):
        extra=set(row)-ALLOWED_PERSONNEL
        if extra: errors.append(f'personnel row {i}: campos não permitidos {sorted(extra)}')
        if not all(str(row.get(k,'')).strip() for k in ('rank','name','org')):
            errors.append(f'personnel row {i}: campos obrigatórios vazios')
    if len({str(r['name']).casefold() for r in personnel}) != len(personnel):
        errors.append('nomes duplicados no efetivo')
    public_data=data_path.read_text(encoding='utf-8')
    if '"number":' in public_data:
        errors.append('Nº BM detectado na camada pública')

    names={r['name'] for r in personnel}
    if set(contacts) != names:
        missing=sorted(names-set(contacts)); extra=sorted(set(contacts)-names)
        if missing: errors.append(f'contatos ausentes para {len(missing)} militar(es): {missing[:5]}')
        if extra: errors.append(f'contatos sem militar correspondente: {extra[:5]}')
    bad_phones=[name for name,phone in contacts.items() if len(re.sub(r'\D','',str(phone))) not in (10,11,12,13)]
    if bad_phones: errors.append(f'telefones inválidos: {bad_phones[:5]}')
    unknown_birthdays=sorted(set(birthdays)-names)
    if unknown_birthdays: errors.append(f'aniversários sem militar correspondente: {unknown_birthdays[:5]}')

    planned=sum(sum(int(g.get(r,0) or 0) for r in RANKS) for g in ddqod.values())
    by_org=Counter(r['org'] for r in personnel)
    claro=0; excess=0
    for org,grades in ddqod.items():
        ex=Counter(classify(r['rank']) for r in personnel if r['org']==org)
        for rank in RANKS:
            p=int(grades.get(rank,0) or 0); e=int(ex.get(rank,0) or 0)
            claro += max(p-e,0)
            if org!='SEMAD': excess += max(e-p,0)
    if planned!=101: errors.append(f'DDQOD previsto={planned}, esperado 101')
    if len(personnel)!=84: errors.append(f'efetivo={len(personnel)}, esperado 84')
    if by_org.get('SEMAD',0)!=1: errors.append('SEMAD deve ter 1 extra-DDQOD')
    if sum(int(ddqod.get('SEMAD',{}).get(r,0) or 0) for r in RANKS)!=0:
        errors.append('SEMAD não pode ter vaga prevista no DDQOD consultado')
    if claro!=23: errors.append(f'claro P/G={claro}, esperado 23')
    if excess!=5: errors.append(f'excedente P/G DDQOD={excess}, esperado 5')

    done=sum(1 for r in tpb if r['status']=='feito')
    not_done=len(tpb)-done
    disp=sum(1 for r in tpb if r['dispensa'])
    action=sum(1 for r in tpb if r['status']!='feito' and not r['dispensa'])
    check=sum(1 for r in tpb if r['status']=='feito' and r['dateToConfirm'])
    observed={'scope':len(tpb),'done':done,'notDone':not_done,'dispensed':disp,'actionable':action,'dateToConfirm':check}
    for k,v in observed.items():
        if int(tpb_meta.get('expected',{}).get(k,-1))!=v:
            errors.append(f'TPB {k}={v}, esperado {tpb_meta.get("expected",{}).get(k)}')
    if re.search(r'/20(?:27|28|29)', tpb_path.read_text(encoding='utf-8')):
        errors.append('ano divergente de 2026 propagado no histórico TPB')

    required_layout=['id="splash"','id="onboarding"','class="banner"','class="container"','class="general-data"','class="color-legend"','class="row"','class="block"','id="birthdayPanel"','id="militaryList"','id="modal"','id="normasModal"']
    for token in required_layout:
        if token not in index: errors.append(f'layout original ausente: {token}')
    if index.count('class="block"') != 18:
        errors.append(f'layout original: {index.count("class=\"block\"")} blocos, esperado 18')
    if 'mobile-nav' in index or 'section-card' in index or 'org-grid' in index:
        errors.append('redesign estrutural detectado; layout original deve ser preservado')

    if 'data/contacts.js?v=2026.09.05' not in index or 'data/tpb.js?v=2026.09.03' not in index or 'assets/js/app.js?v=2.2.0' not in index or 'assets/css/main.css?v=2.1.0' not in index:
        errors.append('versionamento/referências do frontend incompletos')
    if 'runtime-updates.js' in index: errors.append('runtime-updates ainda carregado')
    if 'chart.js' in index.lower() or 'chart.js' in app.lower(): errors.append('Chart.js ainda é dependência')
    if 'Nr BM' in index: errors.append('UI ainda oferece Nº BM')
    if '.innerHTML' in app: errors.append('innerHTML detectado')
    if 'const safeStorage' not in app or 'dai2_onboarding_seen_v2' not in app:
        errors.append('persistência resiliente do onboarding ausente')
    if 'prefers-reduced-motion' not in css: errors.append('prefers-reduced-motion ausente')
    if 'viewport-fit=cover' not in index: errors.append('viewport-fit=cover ausente')
    if 'role="dialog"' not in index or 'close-button' not in index: errors.append('modal acessível incompleto')
    if 'id="tpbToggleBtn"' not in index or 'id="tpbModal"' not in index: errors.append('TPB não integrado ao layout original')
    if 'background-color:' not in css or 'url(' not in css: errors.append('fallback visual para imagens decorativas ausente')
    if 'https://wa.me/' not in app or 'Enviar WhatsApp' not in app:
        errors.append('envio direto por WhatsApp ausente')
    if 'renderBirthdaysPrivacy' in app or 'Aniversários não são publicados' in app:
        errors.append('placeholder de privacidade de aniversários ainda visível')
    for phrase in BANNED_FRONTEND:
        if phrase in app or phrase in index:
            errors.append(f'resíduo de bastidor no frontend: {phrase}')

    payload={'ok':not errors,'version':meta.get('version'),'layout':'original-preserved','ddqod_planned':planned,'personnel':len(personnel),'contacts':len(contacts),'birthdays':len(birthdays),'claro_pg':claro,'excess_pg_ddqod':excess,'semad_extra_ddqod':by_org.get('SEMAD',0),'tpb':observed,'errors':errors}
    print(json.dumps(payload,ensure_ascii=False,indent=2))
    return 0 if not errors else 1

if __name__=='__main__':
    sys.exit(main())
