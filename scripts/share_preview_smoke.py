#!/usr/bin/env python3
"""Smoke específico da pré-visualização social/WhatsApp do Portal DAI/2."""
from __future__ import annotations

import re
import sys
import time
import urllib.request

PAGE = "https://ricmurtapsicologia.github.io/efetivoDAI2/"
IMAGE = "https://ricmurtapsicologia.github.io/efetivoDAI2/assets/img/cidade-administrativa-preview.jpg"
IMAGE_MARKER = "cidade-administrativa-preview.jpg"
UAS = [
    "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)",
    "WhatsApp/2.0",
]


def request(url: str, ua: str, timeout: int = 30):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,image/avif,image/webp,image/*,*/*;q=0.8",
        },
    )
    return urllib.request.urlopen(req, timeout=timeout)


def meta(html: str, key: str, attr: str = "property") -> str:
    pattern = rf'<meta\s+[^>]*{attr}=["\']{re.escape(key)}["\'][^>]*content=["\']([^"\']+)["\'][^>]*>'
    match = re.search(pattern, html, flags=re.I)
    if match:
        return match.group(1).strip()
    pattern_rev = rf'<meta\s+[^>]*content=["\']([^"\']+)["\'][^>]*{attr}=["\']{re.escape(key)}["\'][^>]*>'
    match = re.search(pattern_rev, html, flags=re.I)
    return match.group(1).strip() if match else ""


def link(html: str, rel: str) -> str:
    pattern = rf'<link\s+[^>]*rel=["\']{re.escape(rel)}["\'][^>]*href=["\']([^"\']+)["\'][^>]*>'
    match = re.search(pattern, html, flags=re.I)
    if match:
        return match.group(1).strip()
    pattern_rev = rf'<link\s+[^>]*href=["\']([^"\']+)["\'][^>]*rel=["\']{re.escape(rel)}["\'][^>]*>'
    match = re.search(pattern_rev, html, flags=re.I)
    return match.group(1).strip() if match else ""


def check(name: str, ok: bool, detail: str = "") -> bool:
    print(f"{'PASS' if ok else 'FAIL'} | {name}" + (f" | {detail}" if detail else ""))
    return bool(ok)


def main() -> int:
    html = ""
    last_error = ""
    for _ in range(30):
        try:
            with request(PAGE + f"?preview_probe={int(time.time())}", UAS[0]) as response:
                html = response.read().decode("utf-8", errors="replace")
            if IMAGE in html:
                break
        except Exception as exc:
            last_error = str(exc)
        time.sleep(5)
    else:
        print(f"FAIL | deploy não convergiu para OG local da Cidade Administrativa | {last_error or 'imagem OG esperada ausente'}")
        return 1

    results = []
    canonical = link(html, "canonical")
    image_src = link(html, "image_src")
    og_url = meta(html, "og:url")
    og_image = meta(html, "og:image")
    og_image_url = meta(html, "og:image:url")
    og_secure = meta(html, "og:image:secure_url")
    og_type = meta(html, "og:image:type")
    og_width = meta(html, "og:image:width")
    og_height = meta(html, "og:image:height")
    og_title = meta(html, "og:title")
    og_desc = meta(html, "og:description")
    twitter_image = meta(html, "twitter:image", attr="name")

    results.append(check("01 canonical limpa", canonical == PAGE, canonical))
    results.append(check("02 og:url limpa", og_url == PAGE, og_url))
    results.append(check("03 sem rastreador ChatGPT", "chatgpt" not in (canonical + og_url + og_image + twitter_image).lower()))
    results.append(check("04 título OG presente", og_title == "DAI/2 — Efetivo em Órgãos Externos", og_title))
    results.append(check("05 descrição OG presente", bool(og_desc), og_desc))
    results.append(check("06 og:image = preview Cidade Administrativa", og_image == IMAGE and IMAGE_MARKER in og_image, og_image))
    results.append(check("07 og:image:url alinhada", og_image_url == IMAGE, og_image_url))
    results.append(check("08 og:image:secure_url alinhada", og_secure == IMAGE, og_secure))
    results.append(check("09 image_src alinhada", image_src == IMAGE, image_src))
    results.append(check("10 og:image MIME declarado", og_type == "image/jpeg", og_type))
    results.append(check("11 dimensões sociais 1200x630", og_width == "1200" and og_height == "630", f"{og_width}x{og_height}"))
    results.append(check("12 twitter:image alinhada", twitter_image == IMAGE, twitter_image))
    results.append(check("13 preview não aponta para banner local antigo", "assets/img/banner-cbmmg.jpg" not in html))

    for ua in UAS:
        try:
            with request(PAGE + f"?ua_probe={int(time.time())}", ua) as response:
                crawler_html = response.read().decode("utf-8", errors="replace")
                page_ok = int(response.status) == 200 and IMAGE in crawler_html and IMAGE_MARKER in crawler_html
            results.append(check(f"14 página entregue ao crawler {ua.split('/')[0]}", page_ok))
        except Exception as exc:
            results.append(check(f"14 página entregue ao crawler {ua.split('/')[0]}", False, str(exc)))

    try:
        with request(IMAGE + f"?asset_probe={int(time.time())}", UAS[0]) as response:
            content_type = (response.headers.get("Content-Type") or "").split(";", 1)[0].strip().lower()
            data = response.read()
            status = int(response.status)
        results.append(check("15 imagem pública HTTP 200", status == 200, str(status)))
        results.append(check("16 imagem servida como JPEG", content_type in {"image/jpeg", "image/jpg"}, content_type))
        results.append(check("17 imagem possui assinatura JPEG", data[:2] == b"\xff\xd8" and data[-2:] == b"\xff\xd9", f"{len(data)} bytes"))
        results.append(check("18 imagem em faixa segura de tamanho", 10_000 <= len(data) <= 1_500_000, f"{len(data)} bytes"))
    except Exception as exc:
        results.append(check("15-18 imagem pública acessível", False, str(exc)))

    passed = sum(1 for value in results if value)
    total = len(results)
    print(f"RESULTADO SHARE PREVIEW: {passed}/{total}")
    if passed != total:
        return 1
    print("SHARE PREVIEW: APROVADO — Cidade Administrativa local, 1200x630, acessível a crawlers sociais")
    return 0


if __name__ == "__main__":
    sys.exit(main())
