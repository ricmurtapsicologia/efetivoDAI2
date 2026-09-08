#!/usr/bin/env python3
"""Browser gate for E2E + QA + Accessibility + UX + UI on the DAI/2 portal."""
from __future__ import annotations

import json
import os
import re
import sys
from playwright.sync_api import sync_playwright

BASE = os.environ.get('DAI2_BASE_URL', 'http://127.0.0.1:8000')
EMAIL_RE = re.compile(r'\b[^\s@]+@[^\s@]+\.[^\s@]+\b')


def check(results, name, condition, detail=''):
    ok = bool(condition)
    results.append({'test': name, 'ok': ok, 'detail': detail})
    print(f"{'PASS' if ok else 'FAIL'} | {name}" + (f" | {detail}" if detail else ''))
    return ok


def main() -> int:
    results = []
    console_errors = []
    page_errors = []
    failed_requests = []
    bad_responses = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1366, 'height': 900}, locale='pt-BR')
        page = context.new_page()
        page.on('console', lambda msg: console_errors.append(msg.text) if msg.type == 'error' and not msg.text.startswith('Failed to load resource') else None)
        page.on('pageerror', lambda exc: page_errors.append(str(exc)))
        page.on('requestfailed', lambda req: failed_requests.append(req.url))
        page.on('response', lambda res: bad_responses.append((res.status, res.url)) if res.status >= 400 else None)

        response = page.goto(BASE, wait_until='networkidle')
        check(results, 'E2E 01 · página responde', response is not None and response.ok, str(response.status if response else 'sem resposta'))
        check(results, 'QA 01 · sem erro JavaScript de console inicial', not console_errors, '; '.join(console_errors[:3]))
        check(results, 'QA 02 · sem pageerror inicial', not page_errors, '; '.join(page_errors[:3]))

        page.wait_for_timeout(2900)
        check(results, 'UX 01 · onboarding aparece no primeiro acesso', page.locator('#onboarding').is_visible())
        for step in range(1, 5):
            active = page.locator('.onboarding-step:not(.hidden)')
            check(results, f'E2E 0{step+1} · onboarding etapa {step}', active.count() == 1 and active.is_visible())
            active.locator('.btn-continue').click()
        check(results, 'E2E 06 · conteúdo principal após onboarding', page.locator('#mainContent').is_visible())
        check(results, 'UI 01 · 18 blocos renderizados', page.locator('.block').count() == 18)

        hero_info = page.evaluate("""
          async () => {
            const bg = getComputedStyle(document.querySelector('header.banner')).backgroundImage;
            const m = bg.match(/url\(["']?(https?:[^"')]+)["']?\)/);
            if (!m) return {ok:false,url:'',width:0,height:0};
            return await new Promise(resolve => {
              const img = new Image();
              const timer = setTimeout(() => resolve({ok:false,url:m[1],width:0,height:0,timeout:true}), 8000);
              img.onload = () => { clearTimeout(timer); resolve({ok:img.naturalWidth >= 1600,url:m[1],width:img.naturalWidth,height:img.naturalHeight}); };
              img.onerror = () => { clearTimeout(timer); resolve({ok:false,url:m[1],width:0,height:0}); };
              img.src = m[1];
            });
          }
        """)
        check(results, 'UI 02 · hero corporativo realmente carrega em alta resolução', hero_info.get('ok'), json.dumps(hero_info, ensure_ascii=False))
        check(results, 'QA 03 · hero corresponde ao ativo governado', 'photo-1778876087506-47da0c3e6d98' in hero_info.get('url',''), hero_info.get('url',''))

        general = page.locator('.general-data').inner_text()
        check(results, 'QA 04 · totais canônicos renderizados', all(value in general for value in ['101','84','23']), general.replace('\n',' | '))
        check(results, 'UX 02 · texto técnico de claro removido', 'Claro calculado por posto/graduação' not in general)
        check(results, 'UX 03 · bloco visual de privacidade removido', page.locator('#birthdayPanel').count() == 0 and 'Proteção de dados' not in page.locator('body').inner_text())

        first_block = page.locator('.block[data-orgao="AFAS"]')
        first_block.focus()
        page.keyboard.press('Enter')
        check(results, 'E2E 07 · bloco abre modal por teclado', page.locator('#modal').is_visible())
        check(results, 'Accessibility 01 · modal possui título contextual', 'AFAS' in page.locator('#modalTitle').inner_text())
        page.keyboard.press('Shift+Tab')
        active_tag = page.evaluate("document.activeElement && (document.activeElement.id || document.activeElement.className || document.activeElement.tagName)")
        check(results, 'Accessibility 02 · foco permanece no modal', page.locator('#modal').evaluate("m => m.contains(document.activeElement)"), str(active_tag))
        card_count = page.locator('#militares-list .modal-military-item').count()
        check(results, 'E2E 08 · cada militar do modal tem número visível', card_count > 0 and page.locator('#militares-list .whatsapp-number').count() == card_count)
        check(results, 'E2E 09 · cada militar do modal tem botão WhatsApp', page.locator('#militares-list .whatsapp-action').count() == card_count)
        page.keyboard.press('Escape')
        check(results, 'E2E 10 · Escape fecha modal', not page.locator('#modal').is_visible())
        check(results, 'Accessibility 03 · foco retorna ao bloco acionador', page.evaluate("document.activeElement?.dataset?.orgao === 'AFAS'"))

        page.locator('#searchInput').fill('Silvana Tiengo')
        page.locator('#searchButton').click()
        search_text = page.locator('#searchResult').inner_text()
        check(results, 'E2E 11 · pesquisa nominal funciona', 'Silvana Tiengo' in search_text and 'AFAS' in search_text, search_text.replace('\n',' | ')[:260])
        check(results, 'E2E 12 · número WhatsApp de Silvana está visível', '+55 (31) 99174-3862' in search_text, search_text.replace('\n',' | ')[:260])
        check(results, 'E2E 13 · pesquisa traz ação WhatsApp', page.locator('#searchResult .whatsapp-action').count() == 1)
        page.evaluate("window.__opened=[]; window.open=(url)=>{window.__opened.push(url); return null;}")
        page.locator('#searchResult .whatsapp-action').click()
        opened = [url for url in page.evaluate('window.__opened') if isinstance(url, str) and url]
        whatsapp_url = opened[-1] if opened else ''
        check(results, 'E2E 14 · WhatsApp abre diretamente o destinatário correto', whatsapp_url.startswith('https://wa.me/5531991743862?text='), str(opened))

        page.locator('#searchInput').fill('Diego Natalino dos Santos')
        page.locator('#searchButton').click()
        diego_text = page.locator('#searchResult').inner_text()
        check(results, 'QA 05 · número legado de Diego é normalizado para 9 dígitos', '+55 (31) 98849-7210' in diego_text, diego_text.replace('\n',' | ')[:260])

        page.locator('#rankSelect').select_option('Sgt/SubTen')
        page.locator('#rankButton').click()
        claro_text = page.locator('#claroResult').inner_text()
        check(results, 'E2E 15 · pesquisa de claro por P/G funciona', bool(claro_text.strip()) and 'Claro' in claro_text, claro_text.replace('\n',' | ')[:220])

        page.locator('#showListBtn').click()
        check(results, 'E2E 16 · lista DDQOD expande', page.locator('#militaryList').is_visible())
        check(results, 'QA 06 · SEMAD aparece como extra-DDQOD', '0 previsto no DDQOD' in page.locator('#militaryList').inner_text())

        body_text = page.locator('body').inner_text()
        check(results, 'Data 01 · números WhatsApp são efetivamente visíveis', '+55 (' in body_text)
        check(results, 'Data 02 · nenhum e-mail visível', EMAIL_RE.search(body_text) is None)

        page.locator('#normasToggleBtn').click()
        check(results, 'E2E 17 · modal jurídico abre', page.locator('#normasModal').is_visible())
        check(results, 'QA 07 · modal jurídico contém fonte/ressalva', 'fonte primária prevalecem' in page.locator('#normasContent').inner_text().lower())
        page.keyboard.press('Escape')

        page.locator('#tpbToggleBtn').click()
        tpb_text = page.locator('#tpbContent').inner_text()
        check(results, 'E2E 18 · TPB abre', page.locator('#tpbModal').is_visible())
        check(results, 'UX 04 · TPB usa linguagem intuitiva', all(term in tpb_text for term in ['concluídos','Ação necessária','Sem data registrada']))
        check(results, 'QA 08 · KPIs TPB conferem', all(value in tpb_text for value in ['85','69','16','9','7','15']), tpb_text.replace('\n',' | ')[:260])
        check(results, 'Data 03 · TPB permanece sem lista nominal', page.locator('#tpbContent .tpb-item').count() == 0 and page.locator('#tpbContent input').count() == 0)
        page.keyboard.press('Escape')

        unlabeled_controls = page.evaluate("""
          () => [...document.querySelectorAll('input,select,textarea,button')]
            .filter(el => {
              if (el.offsetParent === null) return false;
              const txt = (el.innerText || el.value || '').trim();
              const aria = el.getAttribute('aria-label') || el.getAttribute('aria-labelledby');
              const id = el.id;
              const label = id ? document.querySelector(`label[for="${id}"]`) : null;
              return !txt && !aria && !label;
            }).map(el => el.id || el.outerHTML.slice(0,80))
        """)
        check(results, 'Accessibility 04 · controles visíveis possuem nome acessível', not unlabeled_controls, json.dumps(unlabeled_controls, ensure_ascii=False))

        small_targets = page.evaluate("""
          () => [...document.querySelectorAll('button')]
            .filter(el => el.offsetParent !== null && !el.disabled)
            .map(el => ({id:el.id || el.className, r:el.getBoundingClientRect()}))
            .filter(x => x.r.height < 44 || x.r.width < 44)
            .map(x => `${x.id}:${Math.round(x.r.width)}x${Math.round(x.r.height)}`)
        """)
        check(results, 'Accessibility 05 · alvos de toque ≥ 44 px', not small_targets, ', '.join(small_targets[:8]))

        page.set_viewport_size({'width': 375, 'height': 812})
        page.reload(wait_until='networkidle')
        page.wait_for_timeout(400)
        check(results, 'UI 03 · mobile sem overflow horizontal', page.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 4'), str(page.evaluate('[document.documentElement.scrollWidth, window.innerWidth]')))
        check(results, 'UI 04 · blocos mobile em coluna única', page.locator('.block').first.evaluate("el => el.getBoundingClientRect().width <= window.innerWidth - 20"))
        check(results, 'UX 05 · onboarding não reaparece após concluído', not page.locator('#onboarding').is_visible())
        check(results, 'UX 06 · conteúdo principal permanece acessível no mobile', page.locator('#mainContent').is_visible())

        title_size = page.locator('.title').evaluate("el => parseFloat(getComputedStyle(el).fontSize)")
        body_size = page.locator('body').evaluate("el => parseFloat(getComputedStyle(el).fontSize)")
        check(results, 'UI 05 · hierarquia tipográfica preservada', title_size >= 24 and body_size >= 14, f'title={title_size}px body={body_size}px')

        check(results, 'QA 09 · sem erros JavaScript ao final', not console_errors and not page_errors, f'console={console_errors[:3]} page={page_errors[:3]}')
        local_failures = [url for url in failed_requests if url.startswith(BASE)]
        local_bad = [f'{status} {url}' for status,url in bad_responses if url.startswith(BASE)]
        check(results, 'QA 10 · assets locais sem falha de rede/HTTP', not local_failures and not local_bad, '; '.join((local_failures + local_bad)[:5]))

        browser.close()

    failed = [item for item in results if not item['ok']]
    print(json.dumps({'ok':not failed,'base':BASE,'passed':len(results)-len(failed),'total':len(results),'failed':failed}, ensure_ascii=False, indent=2))
    return 0 if not failed else 1


if __name__ == '__main__':
    sys.exit(main())