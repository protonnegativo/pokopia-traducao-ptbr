# Revisão da tradução PT-BR do Pokémon Pokopia

Você revisa um trecho da tradução do jogo. O arquivo de entrada é um TSV com as colunas `id`, `en` (original em
inglês) e `pt` (tradução atual). A tradução atual foi feita com IA e tem erros. Seu trabalho é corrigir **só o que
está errado**. Não reescreva por gosto pessoal.

## O que corrigir
- **Sentido errado** ou tradução literal que não faz sentido. Exemplos: "drawing" (sorteio) virou "desenho";
  "Enter photo mode" virou "Digite o modo de foto" (deveria ser "Entre no modo de foto"); "Packing Tips" virou
  "Dicas de embalagem" (deveria ser "Dicas de arrumação").
- **Frase embaralhada**, truncada, sem pedaço do original ou com trecho repetido.
- **Português errado**: concordância, regência, crase, acentuação, ortografia, pontuação.
- **Trecho que ficou em inglês** sem motivo.
- **Tags na ordem errada**, quando isso quebra a frase (por exemplo, a cor `<$cdef(27)>…</color>` envolvendo a
  palavra errada, ou uma pontuação que ficou fora do lugar por causa de uma tag).

## O que NÃO mexer
- Nomes de Pokémon, de golpes (ficam em inglês, por escolha do projeto) e nomes próprios.
- Frases que já estão corretas e naturais. Na dúvida, deixe como está.
- O tom do personagem. Gírias e jeito de falar devem ser preservados em português ("Eiii!", "tipo", "né").
  Use "você".

## Regras técnicas (obrigatórias)
1. **Tags `<...>`**: o texto corrigido deve ter **exatamente as mesmas tags** da tradução atual, com a mesma
   quantidade de cada uma. Você pode mudar a posição de uma tag dentro da frase quando o português pedir, mas
   não pode criar, apagar nem alterar tags. Exemplos: `<$voicel(1,7)>`, `<pname;1>`, `<$cdef(27)>`, `</color>`,
   `<qty;0(tipo,tipos)>` (no `qty`, o conteúdo entre parênteses é singular,plural em português e PODE ser
   corrigido), `<br>`, `<clear>`, `<slide>`, `<wait(0.8)>`. A única exceção é o `<qty;…(…)>`, que pode ter o
   texto de dentro corrigido.
2. **`<br>` é quebra de linha na caixa de texto.** Nenhuma linha (o trecho entre dois `<br>`, sem contar as
   tags) pode ficar **mais longa** que a linha mais longa da tradução atual do mesmo texto. Se precisar,
   redistribua as palavras entre as linhas, mantendo o número de `<br>`.
3. Não use tab nem quebra de linha de verdade dentro do texto. Use as mesmas aspas e reticências do texto atual.
4. Texto que começa sem letra (só números ou símbolos) normalmente não precisa de correção.

## Saída
Escreva um TSV, sem cabeçalho, com **apenas as linhas que você corrigiu**, no formato:

```
id<TAB>texto corrigido completo<TAB>motivo curto
```

O texto corrigido deve ser a linha `pt` inteira, já corrigida, com todas as tags. O motivo tem poucas palavras,
por exemplo: "sentido: drawing = sorteio", "concordância", "frase embaralhada", "ficou em inglês".
Se uma linha estiver boa, não a inclua.
