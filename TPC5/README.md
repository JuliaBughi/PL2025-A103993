# TPC5

## Dados

Júlia Bughi Corrêa da Costa, a103993

## Sobre o TPC5

O TPC5 consiste em simular uma *vending machine*, com as informações dos produtos persistidas num ficheiro json: *stock.json*.

Para isso, foi utilizada a biblioteca *ply.lex*, a qual ajuda a definir os comandos da máquina. Podemos:
1. Listar os produtos da máquina
2. Inserir moedas
3. Selecionar produtos
4. Sair

Cada um desses comandos tem uma função auxiliar associada, com o devido tratamento de erros. No caso das moedas, utiliza-se um dicionário para mapear o valor ao seu token e vice-versa. Também poderia ter sido usada a lógica de tokenização do *ply.lex*, porém, por motivos de simplificação, não foi preciso adicionar tal funcionalidade.

