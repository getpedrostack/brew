"""Gera o ícone mestre (SVG) e os PNGs do WBrC Timer (Brew) na paleta Original Coffee Roaster.

A marca do Brew é a gota do escudo da torrefação, reconstruída com a mesma geometria medida no logo (01.png):
- gota = círculo de raio r + duas tangentes saindo da ponta, a 70/39 r do centro (lados a ~34° da vertical);
- "olho" concêntrico ao círculo: anel cobre de raio 22/39 r e miolo café de 13/39 r;
- mesma família do Triângulo OCR: fundo petróleo com luz no alto, desenho pêssego, olho cobre/café.
Ícone (192/512/180, também maskable): r = 134, ponta arredondada (traço de 10), caixa da gota centrada em y = 250 (centro óptico, a massa fica no círculo),
tudo dentro da zona segura do Android (raio 204,8). Favicon (32 px): r = 148, sem zona segura.
Uso (na pasta do app): python marca/gerar_icones.py .
"""
import math, sys, pathlib
from playwright.sync_api import sync_playwright

OUT = pathlib.Path(sys.argv[1])
PETROLEO, CAFE, COBRE, PESSEGO = '#104a53', '#5d3007', '#ba744d', '#fad9b8'
FUNDO = ('#17606b', PETROLEO, '#0b363d')
K_PONTA, K_ANEL, K_MIOLO = 70 / 39, 22 / 39, 13 / 39
ARREDONDA = 10.0  # largura do traço que arredonda a ponta (acrescenta 5 px em volta)


def geo(r, centro_caixa=256.0):
    altura = r * (1 + K_PONTA)
    cy = centro_caixa + altura / 2 - r          # centro do círculo
    cx = 256.0
    cosf = 1 / K_PONTA                          # r / distância da ponta
    sinf = math.sqrt(1 - cosf ** 2)
    ponta = (cx, cy - r * K_PONTA)
    tang = (r * sinf, -r * cosf)
    return dict(r=r, cx=cx, cy=cy, ponta=ponta, tang=tang)


def n(x):
    return f'{x:.2f}'.rstrip('0').rstrip('.')


def glyph(G):
    r, cx, cy = G['r'], G['cx'], G['cy']
    tx, ty = G['tang']
    d = (f'M{n(cx)} {n(G["ponta"][1])} L{n(cx + tx)} {n(cy + ty)} '
         f'A{n(r)} {n(r)} 0 1 1 {n(cx - tx)} {n(cy + ty)} Z')
    # traço da mesma cor, cantos redondos: arredonda a ponta como os cantos do triângulo do Triângulo OCR
    return (f'<path d="{d}" fill="{PESSEGO}" stroke="{PESSEGO}" stroke-width="{n(ARREDONDA)}" stroke-linejoin="round"/>'
            f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r * K_ANEL)}" fill="{COBRE}"/>'
            f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r * K_MIOLO)}" fill="{CAFE}"/>')


def icon_svg(G):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">'
            '<defs><radialGradient id="g" cx="50%" cy="36%" r="78%">'
            f'<stop offset="0" stop-color="{FUNDO[0]}"/><stop offset=".62" stop-color="{FUNDO[1]}"/>'
            f'<stop offset="1" stop-color="{FUNDO[2]}"/></radialGradient></defs>'
            '<rect width="512" height="512" fill="url(#g)"/>' + glyph(G) + '</svg>\n')


def mais_longe(G):
    """Ponto da gota mais distante do centro do ícone (ponta, base e lados)."""
    r, cx, cy = G['r'], G['cx'], G['cy']
    pts = [G['ponta']] + [(cx + r * math.cos(a), cy + r * math.sin(a)) for a in [i * math.pi / 90 for i in range(-18, 109)]]
    return max(math.dist(p, (256, 256)) for p in pts) + ARREDONDA / 2


G = geo(134.0, centro_caixa=250.0)
far = mais_longe(G)
print('icone r', G['r'], '| centro do circulo y', round(G['cy'], 2), '| ponta y', round(G['ponta'][1], 2),
      '| ponto mais distante', round(far, 1), '(limite 204,8)')
assert far <= 204.8
svg = icon_svg(G)
F = geo(148.0, centro_caixa=252.0)
svg_fav = icon_svg(F)
(OUT / 'icon.svg').write_text(svg, encoding='utf-8', newline='\n')

alvos = [('icon-32.png', 32, svg_fav), ('icon-180.png', 180, svg), ('icon-192.png', 192, svg), ('icon-512.png', 512, svg)]
with sync_playwright() as pw:
    br = pw.chromium.launch(channel='msedge')
    for nome, px, sv in alvos:
        pg = br.new_page(viewport={'width': px, 'height': px}, device_scale_factor=1)
        pg.set_content(f'<html><body style="margin:0;background:#000">'
                       f'<div style="width:{px}px;height:{px}px">{sv.replace("<svg ", f"<svg width={px} height={px} ")}</div></body></html>')
        pg.screenshot(path=str(OUT / nome), clip={'x': 0, 'y': 0, 'width': px, 'height': px}, omit_background=False)
        pg.close()
    br.close()

from PIL import Image
for nome, px, _ in alvos:
    im = Image.open(OUT / nome).convert('RGB')
    assert im.size == (px, px), (nome, im.size)
    im.save(OUT / nome, optimize=True)
    print(nome, im.size, (OUT / nome).stat().st_size, 'bytes')
