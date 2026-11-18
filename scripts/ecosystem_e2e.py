#!/usr/bin/env python3
"""Inventário público e E2E não destrutivo: 41+ repos, desktop e celular."""
import asyncio,json,os,re,time
from pathlib import Path
from collections import Counter
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from urllib.parse import quote,urlsplit
from playwright.async_api import async_playwright

OWNER="ricmurtapsicologia"
ART=Path("artifacts/ecosystem-e2e")
ART.mkdir(parents=True,exist_ok=True)
HEADERS={"Accept":"application/vnd.github+json","User-Agent":"Ecossistema-E2E/1.0"}
if os.getenv("GITHUB_TOKEN"): HEADERS["Authorization"]="Bearer "+os.environ["GITHUB_TOKEN"]

def api(path):
    try:
        with urlopen(Request("https://api.github.com"+path,headers=HEADERS),timeout=25) as r: return json.load(r)
    except HTTPError as e:
        if e.code in (403,404,422): return None
        raise

def inventory():
    repos=[]
    for page in range(1,10):
        batch=api("/users/"+OWNER+"/repos?per_page=100&page="+str(page))
        if not isinstance(batch,list): raise RuntimeError("Falha na consulta dos repositórios GitHub")
        repos.extend(x for x in batch if x.get("owner",{}).get("login","").lower()==OWNER.lower())
        if len(batch)<100:break
    pages=[];unpublished=[];internal=[]
    for repo in repos:
        name=repo["name"]
        if not repo.get("has_pages"):
            unpublished.append(name)
            continue
        info=api("/repos/"+OWNER+"/"+quote(name)+"/pages") or {}
        base=(info.get("html_url") or "https://"+OWNER+".github.io/"+name+"/").rstrip("/")+"/"
        source=info.get("source") or {}
        source_branch=source.get("branch") or repo.get("default_branch") or "main"
        source_prefix=(source.get("path") or "/").strip("/")
        tree=api("/repos/"+OWNER+"/"+quote(name)+"/git/trees/"+quote(source_branch,safe="")+"?recursive=1") or {}
        found=[]
        for item in tree.get("tree",[]):
            path=item.get("path","")
            if item.get("type")!="blob" or not path.lower().endswith(".html") or path.lower()=="404.html":continue
            if source_prefix:
                if not path.startswith(source_prefix+"/"):continue
                path=path[len(source_prefix)+1:]
            if path.startswith(("tests/","test/","__tests__/")):
                internal.append(name+"/"+path);continue
            kind=("principal" if path=="index.html" else ("histórico" if re.search(r"(legacy|before|final|old|backup|archive|v0\d+)",path,re.I) else "subpágina"))
            relative=("" if path=="index.html" else (path[:-10] if path.endswith("/index.html") else path))
            found.append({"repo":name,"path":path,"url":base+relative,"kind":kind,"hosting":"GitHub Pages"})
        if not any(x["url"]==base for x in found):
            found.insert(0,{"repo":name,"path":"(build publicado)","url":base,"kind":"principal","hosting":"GitHub Pages"})
        pages.extend(found)
    for name in ("secretaria-digital-core","manual-participante-cats-digital"):
        pages.append({"repo":name,"path":"/","url":"https://"+name+".vercel.app/","kind":"principal","hosting":"Vercel"})
    return list({x["url"]:x for x in pages}.values()),unpublished,internal,len(repos)

async def check(browser,gate,entry):
  async with gate:
    out=dict(entry,status="OK",http=None,title="",issues=[],notices=[],checks=[],time_seconds=0)
    start=time.monotonic();ctx=None
    try:
      ctx=await browser.new_context(viewport={"width":1366,"height":900},locale="pt-BR",service_workers="block")
      page=await ctx.new_page();errors=[];http_bad=[];host=urlsplit(entry["url"]).hostname
      page.on("pageerror",lambda e:errors.append(str(e).splitlines()[0][:200]))
      page.on("response",lambda r:http_bad.append(str(r.status)+" "+r.url[:150]) if r.status>=400 and urlsplit(r.url).hostname==host else None)
      try:res=await page.goto(entry["url"],wait_until="domcontentloaded",timeout=18000)
      except Exception as e:
        out["issues"].append("Navegação: "+str(e).splitlines()[0][:180]);out["status"]="FALHA";return out
      out["http"]=res.status if res else 0
      if out["http"] in (401,403):
        out["status"]="RESTRITO";out["notices"].append("Autenticação exigida");return out
      if out["http"]<200 or out["http"]>=400:
        out["status"]="FALHA";out["issues"].append("HTTP "+str(out["http"]));return out
      await page.wait_for_timeout(3500 if entry["kind"]=="principal" else 1400)
      snap=await page.evaluate("""() => ({
        title:document.title||'',lang:document.documentElement.lang||'',
        text:(document.body?.innerText||'').slice(0,600),
        length:(document.body?.innerText||'').trim().length,
        width:document.documentElement.scrollWidth,viewport:innerWidth,
        images:[...document.images].filter(x=>x.offsetParent!==null&&x.complete&&x.naturalWidth===0).length
      })""")
      out["title"]=snap["title"]
      if re.search(r"Authentication Required|Sign in to Vercel|Vercel Authentication|Deployment Protection",snap["text"],re.I):
        out["status"]="RESTRITO";out["notices"].append("Proteção de implantação/SSO");return out
      if snap["length"]<35:out["issues"].append("Conteúdo insuficiente após inicialização")
      if not snap["title"]:out["notices"].append("Sem título HTML")
      if not snap["lang"]:out["notices"].append("Sem idioma HTML")
      if snap["width"]>snap["viewport"]+8:out["notices"].append("Overflow horizontal desktop")
      if snap["images"]:out["notices"].append(str(snap["images"])+" imagem(ns) visível(is) indisponível(is)")
      out["checks"].append("renderização desktop")
      if entry["repo"]=="efetivoDAI2" and entry["kind"]=="principal":
        try:
          skip=page.locator(".btn-skip")
          if await skip.count() and await skip.first.is_visible():await skip.first.click(timeout=3500)
          await page.locator('.block[data-orgao="AFAS"]').click(timeout=3500)
          if not await page.locator("#modal").is_visible():out["issues"].append("Modal nominal não abriu")
          await page.keyboard.press("Escape")
          if await page.locator("#modal").is_visible():out["issues"].append("Modal não fechou com Escape")
          out["checks"].append("abrir/fechar modal do efetivo")
        except Exception as e:out["issues"].append("Interação do efetivo: "+str(e).splitlines()[0][:180])
      if entry["repo"]=="Curso-ATS" and entry["kind"]=="principal":
        try:
          anchor=page.get_by_text("Ver apresentações",exact=True)
          if await anchor.count():
            await anchor.first.click(timeout=3000)
            out["checks"].append("navegação das apresentações")
        except Exception as e:out["notices"].append("Navegação do curso: "+str(e).splitlines()[0][:120])
      await page.set_viewport_size({"width":390,"height":844})
      await page.wait_for_timeout(250)
      m=await page.evaluate("""() => ({
        width:document.documentElement.scrollWidth,viewport:innerWidth,
        meta:!!document.querySelector('meta[name="viewport"]')
      })""")
      if m["width"]>m["viewport"]+8:out["notices"].append("Overflow horizontal celular")
      if not m["meta"]:out["notices"].append("Meta viewport ausente")
      out["checks"].append("renderização móvel")
      if errors:out["issues"].append(str(len(errors))+" erro(s) JS: "+" | ".join(dict.fromkeys(errors))[:250])
      if http_bad:out["issues"].append("Recursos internos HTTP 4xx/5xx: "+" | ".join(dict.fromkeys(http_bad))[:250])
      if out["issues"]:out["status"]="FALHA"
      elif out["notices"]:out["status"]="AVISO"
    except Exception as e:
      out["status"]="FALHA";out["issues"].append("Erro da auditoria: "+str(e).splitlines()[0][:170])
    finally:
      out["time_seconds"]=round(time.monotonic()-start,2)
      if ctx:await ctx.close()
    return out

async def main():
  pages,unpublished,internal,count=await asyncio.to_thread(inventory)
  print("INVENTARIO",count,"repositorios;",len(pages),"URLs;",len(unpublished),"sem Pages; internos:",len(internal),flush=True)
  async with async_playwright() as pw:
    browser=await pw.chromium.launch(headless=True,args=["--no-sandbox"])
    sem=asyncio.Semaphore(6)
    results=await asyncio.gather(*(check(browser,sem,p) for p in pages))
    await browser.close()
  summary=dict(Counter(x["status"] for x in results))
  payload={"repository_count":count,"pages_tested":len(results),"summary":summary,
           "pages":results,"unpublished_repositories":unpublished,"internal_test_html":internal,
           "limits":["E2E não destrutivo: não envia dados nem formulários",
                     "Fluxos autenticados são restritos e requerem credenciais/ambiente próprios",
                     "Navegação/renderização/recursos em desktop e celular, não cobertura total dos fluxos por produto"]}
  (ART/"results.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
  md=["# Auditoria E2E do ecossistema","",f"Repositórios localizados: **{count}**",
      f"Endereços verificados: **{len(results)}**",f"Resultados: **{json.dumps(summary,ensure_ascii=False)}**","",
      "| Status | Site/página | HTTP | Evidência |","|---|---|---:|---|"]
  for x in sorted(results,key=lambda x:(x["status"],x["repo"],x["url"])):
    notes="; ".join((x["issues"]+x["notices"])[:3])[:240].replace("|","/")
    md.append(f'| {x["status"]} | [{x["repo"]} — {x["path"]}]({x["url"]}) | {x["http"] or "—"} | {notes} |')
    print(x["status"],x["repo"],x["url"],"HTTP",x["http"],notes[:140],flush=True)
  md+=["","## Repositórios sem GitHub Pages","",", ".join(unpublished) or "Nenhum","",
       "## HTMLs de teste (excluídos das páginas públicas)","",", ".join(internal) or "Nenhum","",
       "## Escopo","",*["- "+s for s in payload["limits"]]]
  (ART/"report.md").write_text("\n".join(md),encoding="utf-8")
  print("AUDITORIA_SUMARIO="+json.dumps({"repos":count,"urls":len(results),"status":summary},ensure_ascii=False),flush=True)
  return 1 if summary.get("FALHA",0) else 0

if __name__=="__main__":raise SystemExit(asyncio.run(main()))
