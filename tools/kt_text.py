#!/usr/bin/env python3
"""Tabela de textos do LINKDATA do Pokopia.

u32 n, u32 ?, ... (cabeçalho 0x40); n registros de 8 bytes (u32 deslocamento relativo ao próprio registro,
u32 flag); textos UTF-8 terminados em zero.
"""
import struct


def parse(d):
    n = struct.unpack_from('<I', d)[0]
    if n == 0 or 0x40 + n * 8 > len(d):
        raise ValueError('nao parece tabela de texto')
    out = []
    for i in range(n):
        pos = 0x40 + i * 8
        off, fl = struct.unpack_from('<II', d, pos)
        s = pos + off
        if off == 0:
            out.append([fl, None]); continue  # registro vazio
        if s >= len(d):
            raise ValueError(f'ponteiro invalido {i}')
        e = d.index(b'\0', s)
        out.append([fl, d[s:e].decode('utf8')])
    return out


def build(head, rows):
    """head: os 0x40 bytes do cabeçalho original; rows: [(flag, texto)]."""
    n = len(rows)
    tbl = bytearray(head[:0x40]); struct.pack_into('<I', tbl, 0, n)
    tbl += b'\0' * (n * 8)
    data = bytearray(); cache = {}
    base = 0x40 + n * 8
    for i, (fl, txt) in enumerate(rows):
        pos = 0x40 + i * 8
        if txt is None:
            struct.pack_into('<II', tbl, pos, 0, fl); continue
        if txt not in cache:
            cache[txt] = base + len(data)
            data += txt.encode('utf8') + b'\0'
        struct.pack_into('<II', tbl, pos, cache[txt] - pos, fl)
    out = tbl + data
    out += b'\0' * ((-len(out)) % 0x10)
    return bytes(out)
