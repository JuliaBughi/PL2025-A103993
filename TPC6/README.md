# TPC6

## Dados

Júlia Bughi Corrêa da Costa, a103993

## Sobre o TPC6

O TPC6 consistia em construir um analisador sintático recursivo descendente, que aceitasse as seguintes frases exemplo:
1. "5 + 3 * 2"
2. "2 * 7 - 5 * 3"
3. "2+3"
4. "67-(2+3*4)"
5. "(9-2)*(13-4)"
 
Adicionalmente, deve retornar o resultado do cálculo.

Para isso, foi necessário construir as regras de produção a seguir:
- Exp --> Termo Exp2
- Exp2 --> '+' Exp
- Exp2 --> '-' Exp
- Exp2 --> epslon
- Termo --> Fator Mul2
- Termo2 --> '*' Mul
- Termo2 --> epslon
- Fator --> '(' Exp ')' 
- Fator --> num

O *calc_sin* traduz essas regras para código, enquanto o *calc_lex* define os símbolos (tokens).

Através dos prints definidos nas funções que definem as regras, ao executar o programa, podemos ver a árvore construída