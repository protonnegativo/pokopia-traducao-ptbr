#!/usr/bin/env python3
"""Lê o LINKDATA da Koei Tecmo (LD_*.BIN + LI_*.IDX).

Índice: registros de 32 bytes (u64 offset, u64 tamanho real, u64 tamanho comprimido, u64 comprimido).
Dados comprimidos: u32 tamanho do bloco, u32 nº de blocos, u32 tamanho real, u32[nº] tamanhos dos blocos,
alinhado a 0x80; cada bloco começa com u32 tamanho e o zlib em seguida.
uso: kt_linkdata.py <LD.BIN> <LI.IDX> [--list] [--extract DIR] [--find BYTES]
"""
import argparse, os, struct, zlib


def index(idx_path):
    data = open(idx_path, 'rb').read()
    for i in range(len(data) // 32):
        off, size, csize, comp = struct.unpack_from('<QQQQ', data, i * 32)
        yield i, off, size, csize, comp


def read_entry(f, off, size, csize, comp):
    f.seek(off)
    if not comp:
        return f.read(size)
    chunk, count, total = struct.unpack('<III', f.read(12))
    sizes = struct.unpack(f'<{count}I', f.read(4 * count))
    pos = off + 12 + 4 * count
    pos = (pos + 0x7f) & ~0x7f
    out = bytearray()
    for s in sizes:
        f.seek(pos)
        blk = f.read(s)
        n = struct.unpack_from('<I', blk)[0]
        try:
            out += zlib.decompress(blk[4:4 + n])
        except zlib.error:
            out += blk  # bloco guardado sem compressão
        pos += s
        pos = (pos + 0x7f) & ~0x7f
    return bytes(out[:total])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('ld'); ap.add_argument('idx')
    ap.add_argument('--list', action='store_true'); ap.add_argument('--extract')
    a = ap.parse_args()
    with open(a.ld, 'rb') as f:
        for i, off, size, csize, comp in index(a.idx):
            if size == 0:
                continue
            if a.list or a.extract:
                try:
                    d = read_entry(f, off, size, csize, comp)
                except Exception as e:
                    print(f'{i:5} erro {e}'); continue
                if a.list:
                    print(f'{i:5} off=0x{off:x} size={size} comp={comp} head={d[:8]!r}')
                if a.extract:
                    os.makedirs(a.extract, exist_ok=True)
                    open(os.path.join(a.extract, f'{i:05d}.bin'), 'wb').write(d)


if __name__ == '__main__':
    main()
