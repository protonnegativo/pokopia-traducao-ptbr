#!/usr/bin/env python3
"""Procura erros na tradução. uso: check.py textos.tsv > relatorio.tsv"""
import re, sys, collections
TAG = re.compile(r'<[^<>]*>')
LAYOUT = {'<br>', '<clear>', '<slide>', '<oneline>'}
def tags(s): return collections.Counter(t for t in TAG.findall(s) if t not in LAYOUT and not t.startswith('<wait'))
def plain(s): return TAG.sub(' ', s)
rows = [l.rstrip('\n').split('\t') for l in open(sys.argv[1], encoding='utf8')][1:]
out = collections.defaultdict(list)
for id_, en, pt in rows:
    if tags(en) != tags(pt):
        miss = tags(en) - tags(pt); extra = tags(pt) - tags(en)
        out['tag'].append((id_, f'falta {dict(miss)} sobra {dict(extra)}', en, pt))
    p = plain(pt)
    if '  ' in pt.replace('<br>', ' ') and '  ' not in en: out['espaço duplo'].append((id_, '', en, pt))
    if re.search(r'<br> \S', pt) and not re.search(r'<br> ', en): out['espaço após quebra'].append((id_, '', en, pt))
    if re.search(r' [,.!?;:](?!\.)', p) and not re.search(r' [,.!?;:]', plain(en)): out['espaço antes de pontuação'].append((id_, '', en, pt))
    if re.search(r'[a-zà-ú][.!?][A-ZÀ-Ú]', p): out['falta espaço depois da pontuação'].append((id_, '', en, pt))
    if en == pt and re.search(r'[a-z]{3,} [a-z]{3,}', plain(en)): out['não traduzido'].append((id_, '', en, pt))
    if pt.count('“') != pt.count('”') or pt.count('(') != pt.count(')'): out['aspas/parênteses'].append((id_, '', en, pt))
    if re.search(r'\b(\w{3,}) \1\b', p, re.I): out['palavra repetida'].append((id_, re.search(r'\b(\w{3,}) \1\b', p, re.I).group(0), en, pt))
    if re.search(r'[一-鿿぀-ヿ]', p): out['caractere asiático'].append((id_, '', en, pt))
    if re.search(r'\b(the|and|you|your|with)\b', p) : out['inglês no meio'].append((id_, '', en, pt))
    if pt.endswith(' ') != en.endswith(' '): out['espaço no fim'].append((id_, '', en, pt))
    le = plain(en).rstrip()[-1:]; lp = plain(pt).rstrip()[-1:]
    if le in '.!?' and lp and lp not in '.!?…' and le: out['pontuação final'].append((id_, f'{le}->{lp}', en, pt))
print('tipo\tid\tnota\ten\tpt')
for k, v in out.items():
    for r in v: print(k, *r, sep='\t')
for k, v in sorted(out.items(), key=lambda x: -len(x[1])): print(f'{len(v):6}  {k}', file=sys.stderr)
