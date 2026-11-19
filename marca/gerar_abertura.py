"""Gera a imagem da tela de abertura do Brew (Android) a partir da logo da Original Coffee Roaster.

No Android, a abertura de um app instalado é montada pelo Chrome: cor de fundo do manifesto
(background_color #104a53) + um ícone de propósito "any". O ícone da tela de início usa o "maskable".
Por isso o manifesto separa os dois: "any" = esta logo; "maskable" = a gota (icon-192/512.png).

Fonte: 01.png da pasta da marca (assinatura completa sobre petróleo #104a53, 1080 px).
O desenho ocupa x 242–836 (594 px); o recorte é um quadrado centrado em que a assinatura ocupa 85 % da largura.
Uso (na pasta do app): python marca/gerar_abertura.py "<pasta Logo_Original>" .
"""
import sys, pathlib
from PIL import Image

SRC = pathlib.Path(sys.argv[1]) / '01.png'
OUT = pathlib.Path(sys.argv[2])
im = Image.open(SRC).convert('RGB')
assert im.getpixel((5, 5)) == (16, 74, 83), 'fundo esperado: petróleo #104a53'
x0, x1, cx, cy = 242, 836, 539, 539
lado = round((x1 - x0) / 0.85)
caixa = (cx - lado // 2, cy - lado // 2, cx - lado // 2 + lado, cy - lado // 2 + lado)
quad = im.crop(caixa)
for px in (192, 512):
    nome = f'icon-original-{px}.png'
    quad.resize((px, px), Image.LANCZOS).save(OUT / nome, optimize=True)
    print(nome, px, (OUT / nome).stat().st_size, 'bytes | recorte', caixa)
