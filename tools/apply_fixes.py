#!/usr/bin/env python3
"""Valida e aplica correções. uso: apply_fixes.py textos-revisado.tsv saida.tsv fix1.tsv [fix2.tsv ...]

Cada correção (id, texto, motivo) é aceita só se:
- tiver as mesmas tags da tradução atual (o texto de dentro do <qty;...(a,b)> pode mudar);
- nenhuma linha (trecho entre <br>) passar de 115% (+3) da maior linha atual/inglês; sem <br>, 125% (+4).
A correção vale para todas as linhas com o mesmo par (en, pt).
"""
import collections, re, sys
TAG = re.compile(r'<[^<>]*>')
def norm(t): return re.sub(r'^(<qty;\d+)\(.*\)>$', r'\1()>', t)
def tags(s): return collections.Counter(norm(t) for t in TAG.findall(s))
def longest(s): return max(len(TAG.sub('', p)) for p in re.split(r'<br>', s))
src, dst, *fixes = sys.argv[1:]
lines = open(src, encoding='utf8').read().splitlines()
rows = [l.split('\t') for l in lines[1:]]
by_id = {r[0]: r for r in rows}
fix = {}; rej = collections.Counter(); bad = []
for fp in fixes:
    for l in open(fp, encoding='utf8').read().splitlines():
        p = l.split('\t')
        if len(p) < 2 or p[0] not in by_id:
            rej['formato/id'] += 1; continue
        id_, new = p[0], p[1]; why = p[2] if len(p) > 2 else ''
        _, en, pt = by_id[id_]
        if new == pt: continue
        if tags(new) != tags(pt): rej['tags'] += 1; bad.append(('tags', id_, pt, new)); continue
        lim = max(longest(pt), longest(en)); lim = lim * 1.15 + 3 if '<br>' in new else lim * 1.25 + 4
        if longest(new) > lim: rej['linha longa'] += 1; bad.append(('longa', id_, pt, new)); continue
        fix[(en, pt)] = (new, why, id_)
n = 0; log = []
for r in rows:
    k = (r[1], r[2])
    if k in fix:
        new, why, id0 = fix[k]
        if r[0] == id0: log.append(f'{r[0]}\t{why}\t{r[2]}\t{new}')
        r[2] = new; n += 1
open(dst, 'w', encoding='utf8').write(lines[0] + '\n' + ''.join('\t'.join(r) + '\n' for r in rows))
open(dst + '.mudancas.tsv', 'w', encoding='utf8').write('id\tmotivo\tantes\tdepois\n' + '\n'.join(log) + '\n')
open(dst + '.rejeitadas.tsv', 'w', encoding='utf8').write('\n'.join('\t'.join(b) for b in bad) + '\n')
print(f'aplicadas {len(fix)} correções ({n} linhas); rejeitadas {dict(rej)}')
