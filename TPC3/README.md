# TPC3

## Dados

Júlia Bughi Corrêa da Costa, a103993

## Sobre o TPC3

O TPC3 consiste em criar em Python um pequeno conversor de MarkDown para HTML para os elementos descritos na "Basic Syntax" da Cheat Sheet:
1. Cabeçalhos 
2. Textos em **bold**
3. Textos em *itálico*
4. Listas numeradas
5. Links
6. Imagens

Para a realização deste TPC, usou-se, principalmente, a função "*sub*" da biblioteca "*re*". Esta função encontra padrões descritos através de expressões regulares e substitui essas ocorrências por um outro padrão à escolha. Todos os casos exigidos pelo TPC (com exceção às listas numeradas) são exemplos muito diretos da utilização dessa função.

No caso das listas numeradas, há uma complexidade maior envolvida, pois para além das tags que delimitam a lista, também existem tags individuais para cada elemento. Para isso, inicialmente chama-se um "*sub*", que procura por um padrão do tipo "dígito, ponto, espaço, conjunto de caracteres e um caracteres de mudança de linha opcional". Quando encontra esse padrão, passa como argumento para a função *replace_list*, que irá formatar a lista de acordo com as normas do html. Para isso, essa função seleciona o grupo **1** (o primeiro grupo de captura - que neste caso é o bloco todo) e nele opera de item em item, formatando em **<ol\>** e **<li\>**.