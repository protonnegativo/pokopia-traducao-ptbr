# Ferramentas

Scripts usados para montar o mod (rodam com Python 3 + Pillow + numpy). Nenhum arquivo do jogo fica no repositório.

| Script | O que faz |
|---|---|
| `kt_text.py` | lê/grava as tabelas de texto do LINKDATA (`LD_C0_R.BIN` / `LI_C0_R.IDX`) |
| `export.py` | exporta inglês × PT-BR para `textos.tsv` (id `arquivo:índice`, en, pt) |
| `check.py` | procura erros (tags, espaços, pontuação, trechos sem tradução) → `relatorio.tsv` |
| `apply_fixes.py` | valida (tags e tamanho das linhas) e aplica correções de revisão (`id`, texto, motivo) |
| `fix_auto.py` | aplica correções mecânicas seguras (espaço/pontuação em volta das quebras de linha) |
| `title_credit.py` | redesenha o crédito na tela de título (textura `79c6dd0e`) |
| `build.py` | monta o mod: grava os textos revisados e a tela de título sobre a base PT-BR |
| `kt_scan.py`, `kt_rdb.py`, `g1t_decode.py` | leitura dos pacotes `.fdata`, do `root.rdb` e das texturas G1T |

Fluxo:

```sh
python3 tools/kt_linkdata.py LD_C0_R.BIN LI_C0_R.IDX --extract <pasta>   # original e base
python3 tools/export.py <orig> <base> textos.tsv
python3 tools/fix_auto.py textos.tsv textos-revisado.tsv
python3 tools/apply_fixes.py textos-revisado.tsv textos-final.tsv correcoes/*.tsv   # regras em INSTRUCOES-REVISAO.md
STYLE=pokemon SIZE=26 Y=469 TRK=1.5 NICK=52 NB=582 \
  python3 tools/title_credit.py titulo_base.png titulo.png "Tradução PT-BR por" "protonnegativo" Fredoka.ttf LuckiestGuy.ttf
python3 tools/build.py <romfs_base> textos-final.tsv titulo.png "build/Traducao PT-BR protonnegativo"
```

Fontes: [Fredoka](https://fonts.google.com/specimen/Fredoka) (OFL) e [Luckiest Guy](https://fonts.google.com/specimen/Luckiest+Guy) (Apache 2.0).
