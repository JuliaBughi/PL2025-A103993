# TPC2

## Dados

Júlia Bughi Corrêa da Costa, a103993

## Sobre o TPC2

Enunciado:
Neste TPC, é proibido usar o módulo CSV do Python;
Deverás ler o dataset, processá-lo e criar os seguintes resultados:
1. Lista ordenada alfabeticamente dos compositores musicais;
2. Distribuição das obras por período: quantas obras catalogadas em cada período;
3. Dicionário em que a cada período está a associada uma lista alfabética dos títulos das obras
desse período.

Para a realização deste TPC, precisava ser feito um parse do csv fornecido. A dificuldade estava na identificação dos delimitadores, pois o '\n' de mudança de linha também estava presente dentro do campo "desc", assim como o delimitador ';' de mudança de campo.
Para contornar esse problema, precisou-se de um boolean "entre_aspas" que identificasse se o caracter especial estava entre aspas ou não, podendo assim atribuir o seu significado correto.
Depois de solucionada esta dificuldade, o processo foi o habitual: guardar dados em dicionários/sets e fazer print dos mesmos, após a sua ordenação.
