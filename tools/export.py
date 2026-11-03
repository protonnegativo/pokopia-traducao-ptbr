#!/usr/bin/env python3
"""Exporta EN x PT-BR para textos.tsv (id, en, pt). uso: export.py <dir_original> <dir_ptbr> <saida.tsv>"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kt_text as k
a, b, out = sys.argv[1:4]
esc = lambda s: s.replace('\\', '\\\\').replace('\n', '\\n').replace('\t', '\\t')
n = 0
with open(out, 'w', newline='', encoding='utf8') as f:
    w = lambda r: f.write('\t'.join(r) + '\n')
    w(['id', 'en', 'pt'])
    for fn in sorted(os.listdir(b)):
        db = open(f'{b}/{fn}', 'rb').read(); da = open(f'{a}/{fn}', 'rb').read()
        if da == db: continue
        try: t = k.parse(db); o = k.parse(da)
        except ValueError: continue
        for i, ((_, en), (_, pt)) in enumerate(zip(o, t)):
            if pt is None or not (en or pt): continue
            w([f'{fn[:5]}:{i}', esc(en or ''), esc(pt)]); n += 1
print(n, 'linhas')
