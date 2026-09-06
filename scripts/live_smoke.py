#!/usr/bin/env python3
"""30-point post-deploy smoke test: layout original + WhatsApp/e-mail + frontend limpo."""
from __future__ import annotations
import json,re,sys,time,urllib.request
from collections import Counter
from urllib.parse import urljoin

BASE="https://ricmurtapsicologia.github.io/efetivoDAI2/"
RANKS=["Sd/Cb","Sgt/SubTen","Ten","Cap","Maj","Ten-Cel"]
BANNED=["BGBM a localizar","Ato de movimentação","A vincular","A localizar","base interna autorizada","neutralizados na camada executiva","Rastreabilidade: data/período da evidência a recuperar","addTrace("]

def fetch(path,timeout=20):
    url=urljoin(BASE,path); sep="&" if "?" in url else "?"
    req=urllib.request.Request(url+sep+f"smoke={int(time.time())}",headers={"User-Agent":"DAI2-live-smoke/2.3"})
    with urllib.request.urlopen(req,timeout=timeout) as r:
        return int(r.status),r.read().decode("utf-8")

def assignment(text,name):
    m=re.search(rf"window\.{re.escape(name)}\s*=\s*(.*?);(?:\r?\n|$)",text,re.S)
    if not m: raise AssertionError(name)
    return json.loads(m.group(1))

def classify(rank):
    v=str(rank or '').lower().replace('º','').strip()
    if 'ten cel' in v or 'ten-cel' in v or v=='cel': return 'Ten-Cel'
    if v.startswith('maj'): return 'Maj'
    if v.startswith('cap'): return 'Cap'
    if 'sub ten' in v or 'subten' in v or 'sgt' in v: return 'Sgt/SubTen'
    if 'ten' in v: return 'Ten'
    if v.startswith('cb') or v.startswith('sd'): return 'Sd/Cb'
    return None

def main():
    last=None
    for _ in range(30):
        try:
            s,index=fetch("")
            if s==200 and 'assets/js/app.js?v=2.2.0' in index and 'data/contacts.js?v=2026.09.05' in index and 'data/emails.js?v=2026.09.06' in index and 'assets/js/email-actions.js?v=1.0.0' in index and 'class="banner"' in index:
                break
        except Exception as e: last=e
        time.sleep(5)
    else:
        print(f"FAIL: Pages não convergiu para frontend com e-mail: {last}"); return 1

    is_,index=fetch("")
    ds,data=fetch("data/data.js?v=2.0.0")
    cts,contact_text=fetch("data/contacts.js?v=2026.09.05")
    es,email_text=fetch("data/emails.js?v=2026.09.06")
    ts,tpbt=fetch("data/tpb.js?v=2026.09.03")
    aps,app=fetch("assets/js/app.js?v=2.2.0")
    eas,email_actions=fetch("assets/js/email-actions.js?v=1.0.0")
    cs,css=fetch("assets/css/main.css?v=2.1.0")
    meta=assignment(data,"DAI2_META"); ddqod=assignment(data,"DAI2_DDQOD"); personnel=assignment(data,"DAI2_PERSONNEL")
    contacts=assignment(contact_text,"DAI2_CONTACTS"); birthdays=assignment(contact_text,"DAI2_BIRTHDAYS"); emails=assignment(email_text,"DAI2_EMAILS")
    tm=assignment(tpbt,"DAI_TPB_META"); rows=assignment(tpbt,"DAI_TPB_ROWS")
    tpb=[{"status":r[3],"dispensa":bool(r[4]),"dateToConfirm":bool(r[7])} for r in rows]
    planned=sum(sum(int(g.get(r,0) or 0) for r in RANKS) for g in ddqod.values())
    by=Counter(p["org"] for p in personnel); claro=0; excess=0
    for org,g in ddqod.items():
        ex=Counter(classify(p["rank"]) for p in personnel if p["org"]==org)
        for rank in RANKS:
            p=int(g.get(rank,0) or 0); e=int(ex.get(rank,0) or 0)
            claro+=max(p-e,0)
            if org!="SEMAD": excess+=max(e-p,0)
    done=sum(1 for r in tpb if r["status"]=="feito"); notdone=len(tpb)-done
    disp=sum(1 for r in tpb if r["dispensa"]); action=sum(1 for r in tpb if r["status"]!="feito" and not r["dispensa"])
    check=sum(1 for r in tpb if r["status"]=="feito" and r["dateToConfirm"])
    frontend=index+"\n"+app+"\n"+email_actions
    names={p['name'] for p in personnel}
    valid_emails=all(re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+",str(v).strip()) for v in emails.values())
    tests=[
      ("01 URL pública responde HTTP 200",is_==200),
      ("02 layout original: splash presente",'id="splash"' in index),
      ("03 layout original: onboarding presente",'id="onboarding"' in index),
      ("04 layout original: banner presente",'class="banner"' in index),
      ("05 layout original: container presente",'class="container"' in index),
      ("06 layout original: dados gerais presente",'class="general-data"' in index),
      ("07 layout original: legenda presente",'class="color-legend"' in index),
      ("08 layout original: 18 blocos",index.count('class="block"')==18),
      ("09 redesign estrutural removido",'mobile-nav' not in index and 'section-card' not in index and 'org-grid' not in index),
      ("10 CSS 2.1 carregado",cs==200 and 'assets/css/main.css?v=2.1.0' in index),
      ("11 app 2.2 carregado",aps==200 and 'assets/js/app.js?v=2.2.0' in index),
      ("12 runtime-updates removido",'runtime-updates.js' not in index),
      ("13 Chart.js removido",'chart.js' not in index.lower() and 'chart.js' not in app.lower()),
      ("14 Nº BM não publicado",'\"number\":' not in data and 'Nr BM' not in index),
      ("15 contatos WhatsApp completos",cts==200 and set(contacts)==names and len(contacts)==84 and 'https://wa.me/' in app and 'Enviar WhatsApp' in app),
      ("16 e-mails validados + ação direta",es==200 and eas==200 and len(emails)==72 and set(emails).issubset(names) and valid_emails and 'mailto:' in email_actions and 'Enviar e-mail' in email_actions),
      ("17 aniversários carregados",len(birthdays)>=60 and set(birthdays).issubset(names)),
      ("18 previsto DDQOD = 101",planned==101),
      ("19 efetivo = 84",len(personnel)==84),
      ("20 SEMAD previsto 0 e extra-DDQOD 1",sum(int(ddqod["SEMAD"].get(r,0) or 0) for r in RANKS)==0 and by.get("SEMAD",0)==1),
      ("21 Silvana está na AFAS",any(p["name"]=="Silvana Tiengo" and p["org"]=="AFAS" for p in personnel)),
      ("22 Claro P/G = 23",claro==23),
      ("23 excedente P/G DDQOD = 5",excess==5),
      ("24 TPB carregado",ts==200 and 'id="tpbToggleBtn"' in index and 'id="tpbModal"' in index),
      ("25 corte TPB = 03/09/2026",tm.get("cutoff")=="03/09/2026"),
      ("26 escopo TPB = 85",len(tpb)==85),
      ("27 TPB feito = 69",done==69),
      ("28 TPB não feito = 16 / dispensa = 9",notdone==16 and disp==9),
      ("29 exigem ação = 7 / sem data consolidada = 15",action==7 and check==15),
      ("30 WhatsApp + e-mail + frontend limpo + a11y",not any(x in frontend for x in BANNED) and 'renderBirthdaysPrivacy' not in app and '.innerHTML' not in app and '.innerHTML' not in email_actions and 'prefers-reduced-motion' in css and 'viewport-fit=cover' in index and 'role="dialog"' in index),
    ]
    fail=[n for n,ok in tests if not ok]
    for n,ok in tests: print(f"{'PASS' if ok else 'FAIL'} | {n}")
    print(f"RESULTADO: {30-len(fail)}/30")
    if fail:
        print("FALHAS:"); [print("-",x) for x in fail]; return 1
    print("SMOKE PÚBLICO: APROVADO 30/30 — layout original, WhatsApp/e-mail e frontend limpo")
    return 0

if __name__=="__main__": sys.exit(main())
