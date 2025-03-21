# TPC6

## Dados

Júlia Bughi Corrêa da Costa, a103993

## Sobre o TPC6

O TPC6 consistia em construir um analisador sintático recursivo descendente, que aceitasse as seguintes frases exemplo:
1. "5 + 3 * 2"
2. "2 * 7 - 5 * 3"
Adicionalmente, deve retornar o resultado do cálculo.

Para isso, foi necessário construir as regras de produção a seguir:
- Exp --> Mul Exp2
- Exp2 --> '+' Exp
- Exp2 --> '-' Exp
- Exp2 --> epslon
- Mul --> num Mul2
- Mul2 --> '*' Mul
- Mul2 --> epslon