# Relatório Projeto PL 2024/2025

## Compilador para Pascal Standard

### Grupo 27

#### A104171 - Gabriel Pereira Ribeiro

#### A103993 - Júlia Bughi Corrêa da Costa

#### 08-05-2025

## Introdução

O objetivo deste projeto é desenvolver um compilador para a linguagem Pascal standard utilizando [PLY](https://ply.readthedocs.io/en/latest/ply.html) e gerando código funcional para a [EWVM](https://ewvm.epl.di.uminho.pt/).

## Índice

1. Analisador Léxico
2. Analisador Sintático
3. Análise Semântica
4. Geração de código EWVM
5. Testes
6. Conclusão

## Analisador Léxico

A primeira etapa da construção de um compilador é definir os tokens da linguagem. A linguagem Pascal possui diversas funcionalidades e estes são os tokens necessários para as que decidimos suportar:

1. Operadores aritméticos:

   ```python
    'PLUS',             # +
    'MINUS',            # -
    'ASTERISK',         # *
    'DIVIDE',           # /
    'BECOMES',          # := 
    ```

2. Operadores lógicos:

   ```python
    'EQ',               # =
    'NEQ',              # <>
    'LT',               # <
    'GT',               # >
    'LE',               # <=
    'GE',               # >= 
    ```  

3. Pontuação:

    ```python
    'LPAREN',           # (
    'RPAREN',           # )
    'LBRAC',            # [ ou (.
    'RBRAC',            # ] ou .)
    'SEMICOLON',        # ;
    'COLON',            # :
    'COMMA',            # ,
    'DOT',              # .
    'DOTDOT',           # ..
    ```

4. Tipos primitivos:

   ```python
    'INTEGER_TYPE',
    'REAL_TYPE',
    'STRING_TYPE',
    'BOOLEAN_TYPE',
    'CHAR_TYPE'
   ```

5. Palavras reservadas:

    ```python
    'AND',
    'ARRAY',
    'BEGIN',
    'CASE',
    'CONST',
    'DIV',
    'DO',
    'DOWNTO',
    'ELSE',
    'END',
    'FOR',
    'FUNCTION',
    'IF',
    'MOD',
    'NIL',
    'NOT',
    'OF',
    'OR',
    'PROCEDURE',
    'PROGRAM',
    'REPEAT',
    'SET',
    'THEN',
    'TO',
    'UNTIL',
    'VAR',
    'WHILE',
    ```

6. Valores:

   ```python
    'ID',               # Identificadores
    'INTEGER',          # Números inteiros
    'REAL',             # Números reais
    'STRING',           # Strings
    'TRUE',
    'FALSE',
   ```

Após identificar as unidades mais básicas da linguagem, foi utilizado o lex da biblioteca ply para definir cada uma delas como um token.
Definimos as expressões regulares para cada um deles, tendo em consideração a ordem das declarações,
de modo a que uma expressão regular mais geral não se sobreponha a uma mais específica.

As palavras reservadas também são reconhecidas com base em expressões regulares e não pela abordagem com um dicionário. Nesta abordagem, suportamos várias combinações de minúsculas e maiúsculas `(?i:...)` e também foi necessário utilizar as *word boundaries* `\b` para não apanhar palavras que não fossem exatamente as palavras reservadas (ex: não detetar *for* em *forget*).

## Analisador Sintático

A segunda etapa consiste na definição das regras sintáticas de linguagem. Depois de uma extensiva análise da estrutura da linguagem Pascal, fomos capazes de produzir uma gramática que podem descrevê-la e reconhecer frases válidas.

Quando aplicável, tivemos o cuidado de definir regras recursivas à esquerda, pois o yacc é um parser LALR(1) e utiliza uma estratégia bottom-up, logo este detalhe torna o processo mais eficiente.

Definimos a tabela das precedências com base no que vimos nas aulas para fazer a associação entre operadores corretamente e garantir que os valores das expressões são bem calculados:

```python
precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'),
    ('nonassoc', 'LT', 'LE', 'GT', 'GE', 'EQ', 'NEQ'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'ASTERISK', 'DIVIDE', 'MOD', 'DIV'),
)
```

O resultado deste parser é uma AST representada em tuplos do python. A árvore começa com o nodo do programa `('program', id_program, content)` e estende-se pelos elementos do content.

```python
# Início do programa
def p_program_start(p):
    '''ProgramStart : PROGRAM ID SEMICOLON Content DOT'''
    p[0] = ('program', p[2], p[4])

# Conteúdo do programa    
def p_content(p):
    '''Content : DeclarationsAndProcedures BeginBlock'''
    p[0] = ('content', p[1], p[2])
```

A estrutura das regras tenta ser bastante intuitiva, nem sempre sendo necessário o primeiro elemento ser o identificador do tipo do nodo da árvore. Isto acontece principalmente nos elementos mais básicos como 'Fator' ou quando não é necessário a identificação como nas listas, por exemplo 'Params' a representar uma lista de parâmetros não tem uma identificação e só toma o valor de uma lista de 'expr_bool' ou 'expr'.

Um caso particular das nossas regras gramaticais é a forma que encontramos para
resolver o problema clássico do dangling else, ou seja, a ambiguidade de associar corretamente um else ao seu if correspondente. Ao separar Statement em duas categorias — MatchedStatement (sem ambiguidade, com if já completo ou outro tipo de statement) e
UnmatchedStatement (potencialmente incompleto, esperando um else) — garantimos que o else é sempre associado ao if mais próximo que ainda não tem else, seguindo a semântica correta e esperada da linguagem Pascal. Esta abordagem permite uma análise sintática clara e desambígua com o PLY.

```python
# Bloco de início
def p_begin_block(p):
    '''BeginBlock : BEGIN Statements END'''
    if len(p) == 4:
        p[0] = ('begin_block', p[2])

# Lista de statements
def p_statements(p):
    '''Statements : Statements SEMICOLON Statement
                 | Statement'''
    if len(p) == 4:
        if p[3] is None:
            p[0] = p[1]
        else:
            p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

# Declaração de statement -> para resolver problema de dangling else
def p_statement(p): 
    '''Statement : MatchedStatement
                 | UnmatchedStatement
                 |'''    
    if len(p) > 1:
        p[0] = p[1]

# Declaração de statement correspondido (não pode apanhar else)
def p_matched_statement(p):
    '''MatchedStatement : Assignment
                | IF ExprBool THEN MatchedStatement ELSE MatchedStatement
                | While
                | Repeat
                | For
                | Case
                | BeginBlock
                | Procedure_or_function_call'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ('if', p[2], p[4], p[6])

# Declaração de statement não correspondido (pode apanhar else)
def p_unmatched_statement(p):
    '''UnmatchedStatement : IF ExprBool THEN Statement
                          | IF ExprBool THEN MatchedStatement ELSE UnmatchedStatement'''
    if len(p) == 5:
        p[0] = ('if', p[2], p[4])
    else:
        p[0] = ('if', p[2], p[4], p[6])
```

Como referido anteriormente, a estrutura tenta ser intuitiva, colocando os elementos dos nodos a ordem que eles aparecem na gramática para permitir um reconhecimento mais rápido. Verifica-se, por exemplo nos nodos 'if' ou 'for' onde cada elemento, desde condições a instruções aparecem na ordem da gramática. Também podemos observar, através do exemplo,
a recursividade à esquerda, usada em todas as nossas regras.

A utilização de uma estrutura de representação intermédia, uma ast, irá permitir realizar análises mais robustas ao código e uma exploração mais fácil e eficiente, ao contrário da estratégia de tradução imediata, o que facilitará os processos seguintes.

Exemplo AST do teste #3 (Fatorial):

```python
program
  Fatorial
  content
    [
      var_list
        [
          var
            [
              n
              i
              fat
            ]
            integer
        ]
    ]
    begin_block
      [
        func_call
          writeln
          [
            Introduza um número inteiro positivo:
          ]
        func_call
          readln
          [
            var
              n
          ]
        assignment
          fat
          1
        for
          assignment
            i
            1
          to
          var
            n
          assignment
            fat
            termo
              var
                fat
              *
              var
                i
        func_call
          writeln
          [
            Fatorial de
            var
              n
            :
            var
              fat
          ]
      ]
```

## Semântica

Após a construção de uma estrutura intermédia pelo parser, antes de continuar para a geração do código, decidimos introduzir uma etapa que consiste na análise semântica do código para assegurar que as frases reconhecidas fazem sentido.

Nesta análise focamo-nos em essencialmente 3 pontos:

- Coerência de tipos
- Imutabilidade de constantes
- Identificação de funções, procedimentos e variáveis inutilizados

A coerência dos tipos que são atribuídos aos dados é algo fundamental para a coerência global do código. Nesta análise o objetivo foi garantir que todos os tipos estavam a ser respeitados.

Verificámos a atribuição de valores às variáveis e comparamos o tipo da expressão ao tipo com que a variável tinha sido declarada e asseguramos que estes coincidiam. Nesta estapa também tivemos em atenção o segundo ponto, se o identificador da variável a que estivesse a ser atribuído o valor fosse, na verdade, uma constante, este seria considerado como erro semântico também.

Aqui utilizamos a noção de Contexto para indicar se estávamos no *scope* global do código, dentro da execução de uma função ou dentro de um loop FOR. Os Contextos servem para percber que variáveis e funções são visíveis naquele ponto do programa.

Verificámos a atribuição de valores às variáveis e comparamos o tipo da expressão ao tipo com que a variável tinha sido declarada e asseguramos que estes coincidiam. Aqui também tivemos em atenção o segundo ponto, se o identificador da variável a que estivesse a ser atribuído o valor fosse, na verdade, uma constante, este seria considerado como erro semântico também.

Também asseguramos que as condições booleanas nos IF, FOR, WHILE, REPEAT e CASE são de facto booleanas. O caso do FOR é especial, pois é necessário restringir o tipo da sua variável de controlo para Integer, Char ou Boolean. Esta variável de controlo também não pode ser alterada no corpo do ciclo, por isso é necessário criar um novo Contexo a analisar as intruções do corpo do ciclo dentro dele.

Outro aspeto importante a ter em consideração é as chamadas de funções e procedimentos nas quais precisamos de ver se os seus argumentos estão certos tanto em número como em tipos. Nas funções, diferenciando dos procedimentos, precisamos de ver se o valor de retorno é compativel com o tipo da função e se depois este está a ser atribuído num sitío também compatível. Aqui tivemos em consideração a existência de algumas funções predefinidas do pascal, assim como o seu número e tipo de argumentos.

Para calcular o tipo de uma expressão é usada a função `evaluate_expr` que se baseia nos operadores presentes na expressão, no caso de ser um tipo primitivo e se é uma utilização de uma função ou variável, obtendo o seu tipo que foi declarado.

Tem em consideração na passagem de Integer para Real nas multiplicações, subtrações e somas, neste último caso também aceitando a concatenação de Strings. Dada a natureza do python, um valor Char será reconhecido como String, mas o analisador tem isso e consideração e aceita se o tipo esperado for Char e o fornecido for String mas com comprimento 1. Se estiver presente um operadoe booleano, o tipo da expressão é imediatamente booleano, sendo necessário apenas grantir a coerência dos 2 lados da expressão.

O último cuidado essencial a ter foi em relação às variáveis que são arrays. O tipo do *range* na definição deve ser ordinal (Integer, Char ou Booleano) e os tipos dos elementos a colocar no array devem ser compatíveis com o seu tipo. Verificamos também que a sintaxe no estilo `var[i]` é exclusiva para arrays e Strings.

Depois de os 2 primeiros pontos serem analisados, verifica-se cada contexto para identificar as variáveis e funções que têm a contagem de usos abaixo de 1.
As que forem identificadas são colocadas na respetiva lista para variáveis ou funções e estas são retornadas para depois a próxima etapa de geração de código poder utilizar.

## EWVM

A parte de geração do código foi a mais desafiadora principalmente por a linguagem se basear numa stack e as suas instruções. Tentamos separar a lógica de cada tipo de nodo e encontrar as traduções adequadas para replicar o comportamento na EWVM.

O `codegen.py` possui uma **SymbolTable**, para memorizar os scopes, as variáveis, funções e seus valores em cada ponto do programa, parecido ao que acontecia na etapa anterior. Também possui conhecimento sobre algumas funções predefinidas para as ter em conta.

A classe principal é o **CodeGenerator** que contém várias funções *visit*, responsáveis por navegar pela AST e produzir código base para cada tipo de nodo. Aqui são tidas em conta as funções e variávis não utilizadas identificadas anteriormente que vão ser ignoradas. Também tem funções emit, responsáveis por adicionar as instruções produzidas ao código gerado.

Para os exemplos mais básicos a geração funcionou, mas houve problemas nos testes mais à frente.

Exemplos de código gerado para os testes 1 a 4.

START
PUSHS "Ola, Mundo!"
WRITES
WRITELN
STOP

PUSHN 4
START
PUSHS "Introduza o primeiro número: "
WRITES
READ
ATOI
STOREG 0
PUSHS "Introduza o segundo número: "
WRITES
READ
ATOI
STOREG 1
PUSHS "Introduza o terceiro número: "
WRITES
READ
ATOI
STOREG 2
PUSHG 0
PUSHG 1
SUP
JZ ELSE0
PUSHG 0
PUSHG 2
SUP
JZ ELSE2
PUSHG 0
STOREG 3
JUMP ENDIF3
ELSE2:
PUSHG 2
STOREG 3
ENDIF3:
JUMP ENDIF1
ELSE0:
PUSHG 1
PUSHG 2
SUP
JZ ELSE4
PUSHG 1
STOREG 3
JUMP ENDIF5
ELSE4:
PUSHG 2
STOREG 3
ENDIF5:
ENDIF1:
PUSHS "O maior é: "
WRITES
PUSHG 3
WRITEI
WRITELN
STOP

PUSHN 3
START
PUSHS "Introduza um número inteiro positivo:"
WRITES
WRITELN
READ
ATOI
STOREG 0
PUSHI 1
STOREG 2
PUSHI 1
STOREG 1
JUMP FORCOND0
FORBODY1:
PUSHG 2
PUSHG 1
MUL
STOREG 2
PUSHG 1
PUSHI 1
ADD
STOREG 1
FORCOND0:
PUSHG 1
PUSHG 0
INFEQ
JZ FOREND2
JUMP FORBODY1
FOREND2:
PUSHS "Fatorial de "
WRITES
PUSHG 0
WRITEI
PUSHS ": "
WRITES
PUSHG 2
WRITEI
WRITELN
STOP

PUSHN 3
START
PUSHS "Introduza um número inteiro positivo:"
WRITES
WRITELN
READ
ATOI
STOREG 0
PUSHI 1
STOREG 2
PUSHI 2
STOREG 1
LOOPSTART0:
PUSHG 1
PUSHG 0
PUSHI 2
DIV
INFEQ
PUSHG 2
AND
JZ LOOPEND1
PUSHG 0
PUSHG 1
MOD
PUSHI 0
EQUAL
JZ ENDIF2
PUSHI 0
STOREG 2
ENDIF2:
PUSHG 1
PUSHI 1
ADD
STOREG 1
JUMP LOOPSTART0
LOOPEND1:
PUSHG 2
JZ ELSE3
PUSHG 0
WRITEI
PUSHS " é um número primo"
WRITES
WRITELN
JUMP ENDIF4
ELSE3:
PUSHG 0
WRITEI
PUSHS " não é um número primo"
WRITES
WRITELN
ENDIF4:
STOP

## Testes

Desde as etapas iniciais que fizemos testes para verificar o bom funcionamento do programa.
Estes estão na pasta `/test`.

Para uma melhor organização, o ficheiro `tests_db.py` contém uma lista com diversos programas em Pascal de teste para usar a seguir.

Para o lexer, construímos o programa `lexer_test.py` que tem uma lista de tokens esperados para os primeiros testes.
O programa corre o lexer no programa em Pascal e obtém uma lista de tokens que depois compara com a esperada, se encontrar algum desconhecido ou fora de ordem, indica o erro.

A organização destes testes depende da ordem que os programas de testes e os tokens esperados estão organizados e apenas corre alguns iniciais devido à complexidade de definir os tokens esperados à mão.

No `parser_test.py` testamos as outras etapas do compilador. Este programa pode levar aceitar como primeiro argumento o índice do teste que se deseja usar, se não for fornecido, corre os programas de teste todos.

No caso de correr apenas 1 teste, o programa apresenta a AST construída pelo parser.

Também há a opção de fornecer a flag `-s` para realizar a análise semântica do código que indica se há inconsistências no código. Vários testes foram desenhados para falhar nesta etapa e perceber se esta análise estava a ser feita corretamente (9 a 17).

Por fim se a flag `-g` for fornecida, o programa também faz a geração do código para a EWVM e apresenta-o no terminal.

Resumindo, o `parser_test.py` testa as 3 etapas finais do compilador aceitando como argumento:

- O índice do programa de teste a utilizar, como primeiro argumento opcional
- flag `-s` para executar a análise semântica
- flag `-g` para executar a geração do código (e anteriormente a análise semântica também)

## Conclusão

A construção de um compilador mostrou ser um grande desafio dada à complexidade de todo o processo, especialmente para uma linguagem como Pascal. Um passo essencial para o desenvolvimento foi a identificação das várias etapas que teríamos de realizar. Foi possível perceber rapidamente que cada etapa estava muito ligada e dependente da anterior e que o desenvolvimento do compilador teria de ser algo bem estruturado.

A parte da análise léxica foi bastante imediata, sendo apenas necessário identificar que funcionalidade de Pascal queríamos suportar e que símbolos seriam necessários identificar.

O parser já foi mais desafiador, mas à medida que íamos avançando na matéria, a sua construção tornou-se mais imediata. Um aspeto que poderia ser melhorado é arranjar uma estrutura de dados mais robusta para representar a AST resultante.

O conceito da análise semântica, apesar de ter responsabilidades muito simples, mostrou ser uma tarefa muito exaustiva onde existiam muitos pequenos detalhes a ter em consideração.

A etapa mais difícil talvez tenha sido a de geração de código, já que tivemos de nos familiarizar também com a linguagem da EWVM, perceber como funcionava e depois perceber como traduzir a nossa árvore de sintaxe abstrata para código funcional.

Consideramos que, apesar de não suportar todas as funcionalidades de Pascal Standard nem gerar o melhor código possível e com melhor otimização, o nosso trabalho está num bom nível pois trata-se de um compilador que consegue traduzir uma linguagem noutra enquando tem em atenção alguns aspetos de eficiência de compilação e a coerência do código.

Assim sendo, este compilador tem muito espaço para melhorias em vários aspetos e é algo que seria necessário fazer para atingir o melhor desempenho e produzir os melhores resultados.

## Referências

[1] [standardpascal.org](https://www.standardpascal.org/)

[2] [freepascal.org](https://wiki.freepascal.org/Standard_Pascal)

[3] [tutorialspoint.com](https://wiki.freepascal.org/Standard_Pascal)

[4] [Docs PLY](https://ply.readthedocs.io/en/latest/)

[5] [Docs EWVM](https://ewvm.epl.di.uminho.pt/manual)
