"""Gera o SVG do README (arte ASCII da foto + ficha estilo neofetch).

Edite o dicionário PERFIL e rode:  python gerar.py
"""
import os
from html import escape

from PIL import Image, ImageFilter, ImageOps

USUARIO = "TheSugZiuL"

# Cada item: (chave, valor). None = linha em branco. ("-", "Título") = seção.
PERFIL = [
    ("OS", "Windows 11, Linux"),
    ("Uptime", "22 anos"),
    ("Host", "Ciência da Computação"),
    ("Kernel", "IA de Fronteira, DevOps, Segurança"),
    ("Shell", "Agentes de IA (o código é com a máquina)"),
    None,
    ("Mind.Product", "Produto, Inovação"),
    ("Mind.Build", "Prototipagem rápida"),
    ("Mind.Core", "Liberdade"),
    None,
    ("Stack", "A que resolve o problema"),
    ("Stack.Focus", "Robustez, Ciência, Segurança"),
    ("Paradigm", "Funcional e matemático"),
    ("Paradigm.Why", "Determinístico, tolerante a falhas"),
    ("Now", "Elixir/BEAM, Phoenix"),
    ("Learning", "Lean"),
    None,
    ("-", "Contact"),
    ("Email", "sugziul@gmail.com"),
    ("Site", "luizssz.github.io"),
    ("LinkedIn", "luizgustavosilvasouza"),
    ("Instagram", "sugziul"),
    ("GitHub", "TheSugZiuL"),
]

FOTO = "foto.png"
RECORTE = "foto_sem_fundo.png"
CORTE = 0.62                                 # fração da altura mantida (cabeça e ombros)
ROWS = 44                                    # linhas da arte (a largura sai da proporção)
RAMPA = " .:-=+*#%@"

FONTE = 14
CW, LH = FONTE * 0.6, FONTE * 1.25          # largura do caractere / altura da linha
FONTE_ARTE = 9                               # arte com fonte menor = mais detalhe
ACW, ALH = FONTE_ARTE * 0.6, FONTE_ARTE * 1.15
PAD = 32
CHAVE_W = 13                                 # colunas reservadas para as chaves
LARG_INFO = 52                               # largura da régua do cabeçalho
GRAD = ["#7aa2f7", "#9d7cd8", "#bb9af7", "#c678dd", "#f7768e"]


def recorte():
    """Foto sem fundo (gerada uma vez com rembg e salva ao lado)."""
    if not os.path.exists(RECORTE):
        from rembg import remove
        remove(Image.open(FOTO)).save(RECORTE)
    im = Image.open(RECORTE).convert("RGBA")
    x0, y0, x1, y1 = im.getchannel("A").point(lambda a: 255 if a > 40 else 0).getbbox()
    return im.crop((x0, y0, x1, y0 + int((y1 - y0) * CORTE)))


def arte_ascii():
    im = recorte()
    # mantém a proporção da foto (caractere é ~2x mais alto que largo)
    rows = ROWS
    cols = round(rows * im.width / im.height * ALH / ACW)
    im = im.resize((cols, rows), Image.LANCZOS)
    alfa = im.getchannel("A")
    lum = ImageOps.autocontrast(im.convert("L").filter(ImageFilter.SHARPEN), cutoff=2)
    linhas = []
    for y in range(rows):
        s = ""
        for x in range(cols):
            if alfa.getpixel((x, y)) < 110:
                s += " "
                continue
            v = lum.getpixel((x, y)) / 255
            s += RAMPA[1 + min(len(RAMPA) - 2, int(v * (len(RAMPA) - 1)))]
        linhas.append(s.rstrip())
    return linhas


def svg(tema):
    escuro = tema == "dark"
    bg = "#0d1117" if escuro else "#ffffff"
    txt = "#c9d1d9" if escuro else "#24292f"
    chave = "#58a6ff" if escuro else "#0550ae"
    sep = "#6e7681" if escuro else "#8c959f"
    titulo = "#ffa657" if escuro else "#953800"

    arte = arte_ascii()
    INFO_X = round(PAD + max(map(len, arte)) * ACW + 40)
    alt_arte = len(arte) * ALH
    alt_info = (len(PERFIL) + 4) * LH
    altura = int(PAD * 2 + max(alt_arte, alt_info))
    largura = int(INFO_X + LARG_INFO * CW + PAD)

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{largura}" height="{altura}" '
        f'font-family="ConsolasFallback,Consolas,\'Courier New\',monospace" font-size="{FONTE}px">',
        '<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">'
        + "".join(f'<stop offset="{i / (len(GRAD) - 1)}" stop-color="{c}"/>' for i, c in enumerate(GRAD))
        + "</linearGradient></defs>",
        f'<rect width="100%" height="100%" fill="{bg}" rx="15"/>',
        f'<text x="{PAD}" y="{PAD + FONTE_ARTE}" fill="url(#g)" font-size="{FONTE_ARTE}px" xml:space="preserve">',
    ]
    for i, l in enumerate(arte):
        out.append(f'<tspan x="{PAD}" y="{PAD + FONTE_ARTE + i * ALH:.1f}">{escape(l)}</tspan>')
    out.append("</text>")

    y0 = PAD + FONTE + max(0, alt_arte - alt_info) / 2
    out.append(f'<text x="{INFO_X}" y="{y0}" fill="{txt}" xml:space="preserve">')
    cab = f"{USUARIO}@github"
    out.append(f'<tspan x="{INFO_X}" y="{y0:.1f}" fill="{titulo}" font-weight="bold">{cab}</tspan>'
               f'<tspan fill="{sep}"> {"─" * (LARG_INFO - len(cab) - 1)}</tspan>')
    y = y0
    for item in PERFIL:
        y += LH
        if item is None:
            continue
        k, v = item
        if k == "-":
            out.append(f'<tspan x="{INFO_X}" y="{y:.1f}" fill="{titulo}" font-weight="bold">- {escape(v)}</tspan>'
                       f'<tspan fill="{sep}"> {"─" * (LARG_INFO - len(v) - 3)}</tspan>')
            continue
        out.append(f'<tspan x="{INFO_X}" y="{y:.1f}" fill="{chave}" font-weight="bold">{escape(k)}</tspan>'
                   f'<tspan x="{INFO_X + CHAVE_W * CW:.1f}" fill="{sep}">: </tspan>'
                   f'<tspan>{escape(v)}</tspan>')
    y += LH * 2
    out.append("</text>")
    cores = ["#ff7b72", "#ffa657", "#e3b341", "#7ee787", "#79c0ff", "#58a6ff", "#bc8cff", "#ff7eb6"]
    for i, c in enumerate(cores):
        out.append(f'<rect x="{INFO_X + i * 24}" y="{y:.1f}" width="20" height="14" rx="3" fill="{c}"/>')
    out.append("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    for tema in ("dark", "light"):
        with open(f"{tema}_mode.svg", "w", encoding="utf-8") as f:
            f.write(svg(tema))
    print("\n".join(arte_ascii()))
