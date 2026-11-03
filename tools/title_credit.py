#!/usr/bin/env python3
"""Crédito da tela de título no estilo do logo POKOPIA.
uso: title_credit.py <in.png> <out.png> "<linha pequena>" "<nick>" <fonte_nick.ttf> <fonte_linha.ttf>"""
import math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
src, out, small, nick, fontp, fontp2 = sys.argv[1:7]
SS = 4
CX = 383.5
# (cor base, cor da listra) tiradas do logo
PAL = [((40, 192, 238), (95, 218, 248)), ((255, 150, 35), (255, 186, 80)), ((178, 98, 250), (212, 152, 255)),
       ((255, 78, 50), (255, 125, 100)), ((96, 202, 30), (150, 228, 60)), ((255, 118, 48), (255, 160, 95))]


def load(size, var='Bold'):
    f = ImageFont.truetype(fontp, size)
    try: f.set_variation_by_name(var)
    except Exception: pass
    return f


im = Image.open(src).convert('RGBA')
a = np.asarray(im).copy(); a[520:626, 100:668] = 0; im = Image.fromarray(a)   # apaga o crédito antigo

# linha pequena. ESTILO: pokemon (amarelo/azul) ou simples (branco com contorno escuro)
import os
STYLE = os.environ.get('STYLE', 'pokemon'); SIZE = float(os.environ.get('SIZE', '24')); TRK = float(os.environ.get('TRK', '1'))
var = os.environ.get('VAR', '')
f = ImageFont.truetype(fontp2, int(SIZE * SS))
if var:
    try: f.set_variation_by_name(var)
    except Exception: pass
W, H = 1024 * SS, 70 * SS
m = Image.new('L', (W, H)); d = ImageDraw.Draw(m)
widths = [d.textlength(c, font=f) + TRK * SS for c in small]
x = CX * SS - (sum(widths) - TRK * SS) / 2
t, b_ = d.textbbox((0, 0), 'TÃ', font=f)[1::2]
for c, w in zip(small, widths):
    d.text((x, H / 2 - (t + b_) / 2), c, font=f, fill=255); x += w
grow = lambda mk, n: mk.filter(ImageFilter.MaxFilter(2 * int(n) + 1))
solid = lambda c: Image.new('RGBA', (W, H), c)
lay = Image.new('RGBA', (W, H))
if STYLE == 'pokemon':
    blue = grow(m, 2.5 * SS)
    shadow = ImageChops.offset(blue, 1 * SS, 2 * SS)
    white = grow(ImageChops.lighter(blue, shadow), 2 * SS)
    layers = ((white, (255, 255, 255, 255)), (shadow, (20, 62, 150, 255)), (blue, (30, 112, 196, 255)), (m, (255, 212, 0, 255)))
elif STYLE == 'branco':
    sh = ImageChops.offset(m, 0, 2 * SS).filter(ImageFilter.GaussianBlur(2 * SS))
    layers = ((sh, (10, 30, 70, 150)), (m, (255, 255, 255, 255)))
else:
    layers = ((grow(m, 2.5 * SS), (6, 2, 10, 255)), (m, (255, 255, 255, 255)))
for mk, c in layers:
    lay = Image.alpha_composite(lay, Image.composite(solid(c), solid((0, 0, 0, 0)), mk))
im.alpha_composite(lay.resize((1024, 70), Image.LANCZOS), (0, int(os.environ.get('Y', '508'))))

# nick: letra por letra, cada uma de uma cor, listras diagonais, leve inclinação e "pulinho"
size = int(float(os.environ.get('NICK', '62')) * SS); f = load(size)
glyphs = []
for i, ch in enumerate(nick):
    base, stripe = PAL[i % len(PAL)]
    bb = f.getbbox(ch); w, h = bb[2] - bb[0], bb[3] - bb[1]
    pad = 40 * SS
    g = Image.new('L', (w + 2 * pad, size + 2 * pad)); ImageDraw.Draw(g).text((pad - bb[0], pad), ch, font=f, fill=255)
    col = Image.new('RGBA', g.size, base + (255,)); cd = ImageDraw.Draw(col)
    step = 22 * SS
    for k in range(-g.size[1], g.size[0] + g.size[1], step):       # listras a 60°
        cd.polygon([(k, g.size[1]), (k + step // 2, g.size[1]), (k + step // 2 + g.size[1] * 0.55, 0), (k + g.size[1] * 0.55, 0)], fill=stripe + (255,))
    col.putalpha(g)
    ang = (-6, 5, -3, 6, -5, 3, -4)[i % 7]
    glyphs.append((col.rotate(ang, Image.BICUBIC, expand=False), g.rotate(ang, Image.BICUBIC), w, (i % 2) * 3 * SS))
track = -1 * SS
total = sum(w for _, _, w, _ in glyphs) + track * (len(glyphs) - 1)
CW, CH = 1024 * SS, 140 * SS
canvas = Image.new('RGBA', (CW, CH)); mask = Image.new('L', (CW, CH))
x = CX * SS - total / 2; pos = []
for col, g, w, dy in glyphs:
    px, py = int(x - 40 * SS), int(10 * SS + dy)
    mask.paste(ImageChops.lighter(mask.crop((px, py, px + g.size[0], py + g.size[1])), g), (px, py))
    pos.append((col, px, py)); x += w + track
# contorno branco grosso + borda fina escura por fora (como o logo sobre o fundo)
white = mask.filter(ImageFilter.MaxFilter(1 + 2 * 7 * SS // 2 * 2 // 2 * 2 + 1)) if False else mask
for _ in range(7):
    white = white.filter(ImageFilter.MaxFilter(2 * SS + 1))
edge = white.filter(ImageFilter.MaxFilter(2 * SS + 1)).filter(ImageFilter.GaussianBlur(SS))
layer = Image.new('RGBA', (CW, CH))
layer.paste(Image.new('RGBA', (CW, CH), (40, 110, 30, 140)), (0, 0), edge)
layer.alpha_composite(Image.composite(Image.new('RGBA', (CW, CH), (255, 255, 255, 255)), Image.new('RGBA', (CW, CH)), white))
for col, px, py in pos:
    layer.alpha_composite(col, (px, py))
small_l = layer.resize((1024, 140), Image.LANCZOS)
bb = small_l.getbbox(); print('nick ocupa', bb)
im.alpha_composite(small_l, (0, int(os.environ.get('NB', '628')) - bb[3]))
im.save(out)
