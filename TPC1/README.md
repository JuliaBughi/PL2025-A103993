# TPC1

## Dados

Júlia Bughi Corrêa da Costa, a103993

## Sobre o TPC1

Para o TP1 pretendia-se criar um somador on/off, com as seguintes características:
- Somar todas as sequências de dígitos que encontrar num texto;
- Sempre que encontrar a string "Off" em qualquer combinação de maíusculas e minúsculas, esse comportamento é desligado;
- Sempre que encontrar a string "On" em qualquer combinação de maíusculas e minúsculas, esse comportamento é ligado novamente;
- Sempre que encontrar o caráter "=", o resultado da soma é colocado na saída.

Para cumprir com este objetivo, foi realizada uma função simples em python.

Inicialmente, são definidas as variáveis:
- **"isOn"**: boolean que controla se o somador está ligado ou desligado (inicialmente com valor True);
- **"acc"**: acumulador da sequência de dígitos que encontra no texto;
- **"i"**: iterador dos caráteres do texto.

A seguir entra-se num ciclo "while" que itera cada caráter do texto passado como parâmetro. Neste ciclo estão definidas cláusulas condicionais que obedecem a cada critério.

**1.** A primeira cláusula identifica os caráteres numéricos e utiliza a variável auxiliar "valor" para determinar o valor correto de uma sequência de dígitos (ex: "dkjs23kw>", somar 23 e não 2 e 3); 

**2.** A segunda cláusula identifica o caráter "o" ou "O" e tem subcláusulas com para a identificação de "n" ou "N" e "f" ou "F" a seguir deste, uma forma de identificar as strings "on" e "off", em qualquer combinação de maiúsculas e minúsculas;

**3.** A terceira cláusula determina o comportamento da função quando encontra o caráter "=".
