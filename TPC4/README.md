# TPC4

## Dados

Júlia Bughi Corrêa da Costa, a103993

## Sobre o TPC4

O TPC 4 consistia em criar um *lexer* para linguagens de query as quais se podem escrever frases do tipo:

```
# DBPedia: obras de Chuck Berry

select ?nome ?desc where {
    ?s a dbo:MusicalArtist.
    ?s foaf:name "Chuck Berry"@en .
    ?w dbo:artist ?s.
    ?w foaf:name ?nome.
    ?w dbo:abstract ?desc
} LIMIT 1000
```

Para realizar a tarefa, utilizou-se a biblioteca *ply*. Definiram-se os *tokens* da linguagem exemplo através de expressões regulares. 