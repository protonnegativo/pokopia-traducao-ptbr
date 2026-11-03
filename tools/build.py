#!/usr/bin/env python3
"""Monta o mod de tradução revisado a partir da base PT-BR.

uso: build.py <romfs_base> <textos.tsv> <titulo.png> <pasta_saida>
- textos.tsv: id (arquivo:índice), en, pt  — a coluna pt é a revisada
- titulo.png: tela de título (textura 79c6dd0e) já com o crédito novo
"""
import os, shutil, struct, sys, zlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
import g1t_decode as g, kt_rdb, kt_scan, kt_text

KIDS = 'motor_asset_re/KIDS_PLATFORM_OUNCE'
TITLE = 0x79c6dd0e
FDATA_BY_INDEX = {0x10: '0x4b13d561.fdata'}
al = lambda x, a: (x + a - 1) & ~(a - 1)


def ld_read(f, off, size, csize, comp):
    f.seek(off)
    if not comp:
        return f.read(size)
    ch, cnt, tot = struct.unpack('<III', f.read(12)); sizes = struct.unpack(f'<{cnt}I', f.read(4 * cnt))
    pos, out = al(12 + 4 * cnt, 0x80), bytearray()
    for s in sizes:
        f.seek(off + pos); blk = f.read(s); n = struct.unpack_from('<I', blk)[0]
        out += zlib.decompress(blk[4:4 + n]); pos = al(pos + s, 0x80)
    return bytes(out[:tot])


def ld_pack(data, ch=0x10000):
    blocks = [zlib.compress(data[i:i + ch], 9) for i in range(0, len(data), ch)]
    head = struct.pack('<III', ch, len(blocks), len(data)) + b''.join(struct.pack('<I', len(b) + 4) for b in blocks)
    out = bytearray(head); out += b'\0' * (al(len(out), 0x80) - len(out))
    for b in blocks:
        out += struct.pack('<I', len(b)) + b; out += b'\0' * (al(len(out), 0x80) - len(out))
    return bytes(out)


def unesc(s):
    out, i = [], 0
    while i < len(s):
        if s[i] == '\\' and i + 1 < len(s):
            out.append({'n': '\n', 't': '\t', '\\': '\\'}[s[i + 1]]); i += 2
        else:
            out.append(s[i]); i += 1
    return ''.join(out)


def patch_texts(romfs, tsv):
    want = {}
    for line in open(tsv, encoding='utf8').read().splitlines()[1:]:
        id_, en, pt = line.split('\t')
        fn, i = id_.split(':'); want.setdefault(int(fn), {})[int(i)] = unesc(pt)
    ld, li = os.path.join(romfs, 'LD_C0_R.BIN'), os.path.join(romfs, 'LI_C0_R.IDX')
    idx = bytearray(open(li, 'rb').read()); changed = 0; lines = 0
    with open(ld, 'r+b') as f:
        for fn, rows_new in sorted(want.items()):
            ent = struct.unpack_from('<QQQQ', idx, fn * 32)
            old = ld_read(f, *ent); rows = kt_text.parse(old)
            diff = [i for i, t in rows_new.items() if rows[i][1] != t]
            if not diff:
                continue
            for i in diff:
                rows[i][1] = rows_new[i]
            new = kt_text.build(old, rows); assert kt_text.parse(new) == rows
            packed = ld_pack(new)
            f.seek(0, 2); end = al(f.tell(), 0x100); f.truncate(end); f.seek(end); f.write(packed)
            struct.pack_into('<QQQQ', idx, fn * 32, end, len(new), len(packed), 1)
            assert ld_read(f, end, len(new), len(packed), 1) == new
            changed += 1; lines += len(diff)
    open(li, 'wb').write(idx)
    print(f'textos: {lines} linhas alteradas em {changed} arquivos')


def patch_title(kids, png):
    _, ents, _ = kt_rdb.read(os.path.join(kids, 'root.rdb'))
    off, size, fidx = struct.unpack_from('<IIH', ents[TITLE]['loc'], 2)
    path = os.path.join(kids, FDATA_BY_INDEX[fidx])
    e = next(x for x in kt_scan.entries(path) if x['offset'] == off)
    assert e['comp_size'] == e['file_size'], 'título deveria estar sem compressão (vindo da base PT-BR)'
    data = bytearray(kt_scan.read_data(path, e)); t = g.parse(bytes(data))[0]
    img = Image.open(png).convert('RGBA'); assert img.size == (t['width'], t['height'])
    sw = g.swizzle(g.encode_bc3(img), t['width'] // 4, t['height'] // 4, 16)
    assert len(sw) <= t['data_end'] - t['data_off']
    data[t['data_off']:t['data_off'] + len(sw)] = sw; data[t['header'] + 1] = 0x62
    back = g.decode(bytes(data), g.parse(bytes(data))[0]).convert('RGBA')
    err = np.abs(np.asarray(back, np.int16) - np.asarray(img, np.int16)).mean(); assert err < 6, err
    with open(path, 'r+b') as f:
        f.seek(e['data_off']); f.write(data)
        f.seek(e['offset'] + 0x30); f.write(struct.pack('<I', zlib.crc32(bytes(data))))
    assert kt_scan.read_data(path, next(x for x in kt_scan.entries(path) if x['offset'] == off)) == bytes(data)
    print(f'título regravado (erro médio {err:.2f})')


def main():
    base, tsv, png, out = sys.argv[1:5]
    if os.path.exists(out):
        shutil.rmtree(out)
    shutil.copytree(base, os.path.join(out, 'romfs'))
    romfs = os.path.join(out, 'romfs')
    patch_texts(romfs, tsv)
    patch_title(os.path.join(romfs, KIDS), png)
    print('ok:', out)


if __name__ == '__main__':
    main()
