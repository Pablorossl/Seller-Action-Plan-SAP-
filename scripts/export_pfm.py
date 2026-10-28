"""Exporta la memoria Markdown a PDF A4 con Chromium, sin servicios externos.

Requiere Python con Playwright y Chromium (herramientas de documentación/QA).
Soporta los bloques usados en la memoria: títulos, párrafos, tablas, listas,
código, enlaces e imágenes locales. No pretende ser un parser Markdown general.
"""
from html import escape
from pathlib import Path
import re

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SOURCE = DOCS / "memoria-pfm.md"
BUILD = DOCS / "_build"


def inline(value):
    tokens = []

    def token(markup):
        tokens.append(markup)
        return f"SAPINLINE{len(tokens)-1}END"

    value = re.sub(r"`([^`]+)`", lambda m: token(f"<code>{escape(m[1])}</code>"), value)
    value = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: token(f'<a href="{escape(m[2], quote=True)}">{escape(m[1])}</a>'), value)
    value = escape(value)
    value = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", value)
    for i, markup in enumerate(tokens):
        value = value.replace(f"SAPINLINE{i}END", markup)
    return value


def render(markdown):
    lines = markdown.splitlines()
    headings = [line[3:] for line in lines if line.startswith("## ")]
    toc = '<nav class="toc"><h2>Índice</h2><ol>' + ''.join(
        f'<li><a href="#section-{i}">{escape(title)}</a></li>' for i, title in enumerate(headings)) + '</ol></nav>'
    out, i, section = ['<div class="cover">'], 0, 0
    cover = True
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        heading = re.match(r"^(#{1,3}) (.+)$", line)
        if heading:
            level, title = len(heading[1]), heading[2]
            if level == 2:
                if cover:
                    out.extend(['</div>', toc])
                    cover = False
                out.append(f'<h2 id="section-{section}">{inline(title)}</h2>')
                section += 1
            else:
                out.append(f'<h{level}>{inline(title)}</h{level}>')
            i += 1
            continue
        figure = re.fullmatch(r"!\[([^\]]*)\]\(([^)]+)\)", line)
        if figure:
            path = (DOCS / figure[2]).resolve()
            if not path.is_file() or not path.is_relative_to(DOCS):
                raise ValueError(f"Imagen local no válida: {figure[2]}")
            out.append(f'<figure><img src="{path.as_uri()}" alt="{escape(figure[1])}"/><figcaption>{escape(figure[1])}</figcaption></figure>')
            i += 1
            continue
        if line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                cells = [cell.strip() for cell in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r":?-+:?", cell) for cell in cells):
                    rows.append(cells)
                i += 1
            out.append('<table><thead><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in rows[0]) + '</tr></thead><tbody>')
            for row in rows[1:]:
                out.append('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in row) + '</tr>')
            out.append('</tbody></table>')
            continue
        if line.startswith('```'):
            code = []
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                code.append(lines[i])
                i += 1
            out.append('<pre>' + escape('\n'.join(code)) + '</pre>')
            i += 1
            continue
        if line.startswith('- '):
            out.append('<ul>')
            while i < len(lines) and lines[i].startswith('- '):
                out.append('<li>' + inline(lines[i][2:]) + '</li>')
                i += 1
            out.append('</ul>')
            continue
        paragraph = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r'^(#|\||!\[|```|- )', lines[i]):
            paragraph.append(lines[i].strip())
            i += 1
        out.append('<p>' + inline(' '.join(paragraph)) + '</p>')
    if cover:
        out.append('</div>')
    return '\n'.join(out)


CSS = '''
@page { size: A4; margin: 18mm 18mm 20mm; }
* { box-sizing: border-box; }
body { font: 10.5pt/1.48 Arial, sans-serif; color: #253630; margin: 0; }
p { orphans: 3; widows: 3; margin: 0 0 3.5mm; }
h1 { color:#123c32; font-size: 34pt; line-height:1.12; margin: 0 0 15mm; }
h2 { color:#123c32; font-size: 20pt; line-height:1.2; margin:8mm 0 5mm; }
h2#section-0, h2#section-16, h2#section-17 { break-before:page; margin-top:0; }
h3 { font-size:12pt; color:#176b50; margin:6mm 0 3mm; }
h2,h3 { break-after:avoid; }
.cover { padding-top:40mm; break-after:page; }
.cover p { margin-bottom:8mm; }
.cover p:nth-of-type(1) { font-size:16pt; }
.toc { break-after:page; }
.toc h2 { margin-top:0; }
.toc ol { list-style:none; padding:0; }
.toc li { padding:2.4mm 0; border-bottom:1px solid #e2e8e4; }
a { color:#176b50; text-decoration:none; overflow-wrap:anywhere; }
code { font:9pt/1.4 monospace; background:#f1f4f2; overflow-wrap:anywhere; }
pre { white-space:pre-wrap; background:#f1f4f2; padding:4mm; font-size:9pt; }
table { width:100%; border-collapse:collapse; table-layout:fixed; margin:4mm 0 6mm; font-size:9pt; }
th { background:#e7f0e9; text-align:left; font-weight:bold; }
th,td { padding:2.5mm; border:1px solid #cbd8d0; vertical-align:top; overflow-wrap:anywhere; }
tr { break-inside:avoid; }
thead { display:table-header-group; }
figure { margin:6mm 0; break-inside:avoid; text-align:center; }
figure img { display:block; max-width:100%; max-height:205mm; width:auto; height:auto; margin:0 auto; }
figcaption { font-size:9pt; line-height:1.4; margin-top:3mm; color:#52665b; }
'''


def main():
    BUILD.mkdir(parents=True, exist_ok=True)
    html = '<!doctype html><html lang="es"><meta charset="utf-8"><title>Seller Action Plan — Memoria PFM</title><style>' + CSS + '</style><body>' + render(SOURCE.read_text()) + '</body></html>'
    path = BUILD / "memoria-pfm.html"
    path.write_text(html)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()
        page.route(re.compile(r"^https?://"), lambda route: route.abort())
        page.goto(path.as_uri())
        page.evaluate("async () => { await document.fonts.ready; await Promise.all([...document.images].map(i => i.decode())); }")
        assert page.locator('img').count() == len(re.findall(r'^!\[', SOURCE.read_text(), re.M))
        page.pdf(path=str(DOCS / "memoria-pfm.pdf"), format="A4", print_background=True,
            prefer_css_page_size=True, display_header_footer=True, header_template='<span></span>',
            footer_template='<div style="font:8px Arial;width:100%;margin:0 18mm;color:#52665b;display:flex;justify-content:space-between"><span>SAP · Pablo Rosales · Memoria para revisión</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>')
        browser.close()
    print(f"PDF generado: {DOCS / 'memoria-pfm.pdf'}")


if __name__ == '__main__':
    main()
