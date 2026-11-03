#!/usr/bin/env python3
"""Correções mecânicas e seguras. uso: fix_auto.py entrada.tsv saida.tsv"""
import re, sys
src, dst = sys.argv[1:3]
lines = open(src, encoding='utf8').read().splitlines()
out = [lines[0]]; n = 0; log = []
for line in lines[1:]:
    id_, en, pt = line.split('\t'); o = pt
    # pontuação jogada para depois da quebra: "Por favor<br>, tente" -> "Por favor,<br>tente"
    pt = re.sub(r'\s*<br>\s*([,.;:!?])(?!\.)\s*', r'\1<br>', pt)
    # espaço logo depois da quebra de linha (vira recuo na tela), se o inglês não tem
    if not re.search(r'<br> ', en):
        pt = re.sub(r'<br> +', '<br>', pt)
    # espaço sobrando antes da quebra
    pt = re.sub(r' +<br>', '<br>', pt)
    # espaço antes de vírgula/ponto final (não mexe em reticências nem no começo de linha)
    pt = re.sub(r'(?<=[\wÀ-ú>]) +([,;:](?!\S*>)|\.(?!\.)|[!?](?![!?]))', r'\1', pt) if not re.search(r' [,.!?;:]', en) else pt
    # espaços duplos no meio do texto
    if '  ' not in en:
        pt = re.sub(r'(?<=\S)  +(?=\S)', ' ', pt)
    if pt != o:
        n += 1; log.append(f'{id_}\n  - {o}\n  + {pt}')
    out.append('\t'.join((id_, en, pt)))
open(dst, 'w', encoding='utf8').write('\n'.join(out) + '\n')
open(dst + '.log', 'w', encoding='utf8').write('\n'.join(log) + '\n')
print(n, 'linhas corrigidas')
