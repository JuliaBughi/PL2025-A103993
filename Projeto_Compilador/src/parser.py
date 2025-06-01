import ply.yacc as yacc
from lexer import tokens
from semantic import semantic_analyse, SemanticError
from codegen import CodeGenerator

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'),
    ('nonassoc', 'LT', 'LE', 'GT', 'GE', 'EQ', 'NEQ'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'ASTERISK', 'DIVIDE', 'MOD', 'DIV'),
)

# Início do programa
def p_program_start(p):
    '''ProgramStart : PROGRAM ID SEMICOLON Content DOT'''
    p[0] = ('program', p[2], p[4])

# Conteúdo do programa    
def p_content(p):
    '''Content : DeclarationsAndProcedures BeginBlock'''
    p[0] = ('content', p[1], p[2])

# Blocos de declarações e procedimentos
def p_declarations_and_procedures(p):
    '''DeclarationsAndProcedures : DeclarationsAndProcedures DeclarationOrProcedure
                                 | '''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []

# Declarações ou procedimentos
def p_declaration_or_procedure(p):
    '''DeclarationOrProcedure : Declaration
                              | Proc_or_func SEMICOLON'''
    p[0] = p[1]

# Declaração de variáveis e constantes
def p_declaration(p):
    '''Declaration : ConstBlock
                    | VarBlock'''
    p[0] = p[1]

# Blocos de constantes
def p_const_block(p):
    '''ConstBlock : CONST ConstDeclarations'''
    if len(p) > 1:
        p[0] = ('const_list', p[2])

# Declarações de constantes
def p_const_declarations(p):
    '''ConstDeclarations : ConstDeclarations ConstDeclaration
                        | ConstDeclaration'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

# Declaração de constante
def p_const_declaration(p):
    '''ConstDeclaration : ID EQ Value SEMICOLON'''
    p[0] = (p[1], p[3])

# Blocos de variáveis
def p_var_block(p):
    '''VarBlock : VAR VarDeclarations'''
    p[0] = ('var_list', p[2])

# Declarações de variáveis
def p_var_declarations(p):
    '''VarDeclarations : VarDeclarations VarDeclaration
                      | VarDeclaration'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

# Declaração de variável
def p_var_declaration(p):
    '''VarDeclaration : IDs COLON VarType SEMICOLON'''
    p[0] = ('var', p[1], p[3])

# Tipo de variável
def p_var_type(p):
    '''VarType : Type
                | ARRAY LBRAC Range RBRAC OF Type'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ('array', p[3], p[6])

# Intervalo de valores na definição de array
def p_range(p):
    '''Range : Value DOTDOT Value'''
    p[0] = ('range', p[1], p[3])

# Lista de identificadores
def p_ids(p):
    '''IDs : IDs COMMA ID
           | ID'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

# Procedimento ou função
def p_proc_or_func(p):
    '''Proc_or_func : Procedure
                    | Function'''
    p[0] = p[1]

# Definição de procedimento
def p_procedure(p):
    '''Procedure : PROCEDURE ID ArgsList SEMICOLON Content'''
    p[0] = ('procedure', p[2], p[3], p[5])

# Definição de função
def p_function(p):
    '''Function : FUNCTION ID ArgsList COLON Type SEMICOLON Content'''
    p[0] = ('function', p[2], p[3], p[5], p[7])

# Lista de argumentos
def p_args_list(p):
    '''ArgsList : LPAREN Args RPAREN
                | '''
    if len(p) == 4:
        p[0] = ('args_list', p[2])
    else:
        p[0] = []

# Argumentos (lista recursiva)
def p_args(p):
    '''Args : Args COMMA Arg
            | Arg'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

# Definição de argumento
def p_arg(p):
    '''Arg : ID COLON Type'''
    if len(p) == 4:
        p[0] = ('arg', p[1], p[3])


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

# Chamada de procedimento ou função (com ou sem parâmetros)
def p_procedure_or_function_call(p):
    '''Procedure_or_function_call : ID LPAREN Params RPAREN
                                  | ID'''
    if len(p) == 5:
        p[0] = ('func_call', p[1], p[3])
    else:
        p[0] = ('func_call', p[1])

# Lista de parâmetros
def p_params(p):
    '''Params : Params COMMA ExprBool
              | ExprBool'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

# Atribuição
def p_assignment(p):
    '''Assignment : ID BECOMES Expr'''
    p[0] = ('assignment', p[1], p[3])

# While
def p_while(p):
    '''While : WHILE ExprBool DO Statement'''
    p[0] = ('while', p[2], p[4])

# Repeat
def p_repeat(p):
    '''Repeat : REPEAT Statements UNTIL ExprBool'''
    p[0] = ('repeat', p[2], p[4])

# For
def p_for(p):
    '''For : FOR Assignment TO ExprBool DO Statement
           | FOR Assignment DOWNTO ExprBool DO Statement'''
    p[0] = ('for', p[2], p[3], p[4], p[6])

# Case
def p_case(p):
    '''Case : CASE Expr OF CaseLabels END'''
    p[0] = ('case', p[2], p[4])

# Case labels
def p_case_labels(p):
    '''CaseLabels : CaseLabels CaseLabel
                  | CaseLabel'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

# Case label
def p_case_label(p):
    '''CaseLabel : Values COLON Statement SEMICOLON'''
    p[0] = ('case_label', p[1], p[3])

# Lista de valores
def p_values(p):
    '''Values : Values COMMA Value
              | Value'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

# Valor que pode ser atribuído a uma constante ou variável
def p_value(p):
    '''Value : INTEGER
                | REAL
                | STRING
                | TRUE
                | FALSE
                | ID'''
    p[0] = p[1]

# Definição de tipos
def p_type(p):
    '''Type : INTEGER_TYPE
            | REAL_TYPE
            | STRING_TYPE
            | BOOLEAN_TYPE
            | CHAR_TYPE'''
    p[0] = p[1]


def p_expr_bool(p):
    '''ExprBool : NOT ExprBool
                | Expr 
                | Expr OpRel Expr'''
    if len(p) == 3: 
        p[0] = ('not', p[2])
    elif len(p) == 2: 
        p[0] = p[1]
    else:  
        p[0] = ('expr_bool', p[1], p[2], p[3])


def p_expr(p):
    '''Expr : Termo
            | Expr OpAdd Termo'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ('expr', p[1], p[2], p[3])

def p_termo(p):
    '''Termo : Fator
            | Termo OpMul Fator'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ('termo', p[1], p[2], p[3])

def p_fator(p):
    '''Fator : Const
            | VarOrFuncCall 
            | LPAREN ExprBool RPAREN'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]
    
def p_op_rel(p):
    '''OpRel : EQ
            | NEQ
            | LT
            | GT
            | LE
            | GE'''
    p[0] = p[1]

def p_op_add(p):
    '''OpAdd : PLUS
            | MINUS
            | OR'''
    p[0] = p[1]
    
def p_op_mul(p):
    '''OpMul : ASTERISK
            | DIVIDE
            | AND
            | MOD
            | DIV'''
    p[0] = p[1]
    
def p_const(p):
    '''Const : INTEGER
            | REAL
            | STRING
            | TRUE
            | FALSE'''
    p[0] = p[1]
    
def p_var_or_func_call(p):
    '''VarOrFuncCall : ID
                    | ID LBRAC Expr RBRAC
                    | ID LPAREN Params RPAREN'''
    if len(p) == 2:
        p[0] = ('var', p[1])
    elif p[2] == '[':
        p[0] = ('var', p[1], p[3])
    else:
        p[0] = ('func_call', p[1], p[3])

# Erro
def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}'")
    else:
        print("Syntax error at EOF")

parser = yacc.yacc()

#ver também aquilo de apareceer numa imagem
def print_ast(node, indent=0):
    spacer = '  ' * indent
    if isinstance(node, tuple):
        print(f"{spacer}{node[0]}")
        for child in node[1:]:
            print_ast(child, indent + 1)
    elif isinstance(node, list):
        print(f"{spacer}[")
        for item in node:
            print_ast(item, indent + 1)
        print(f"{spacer}]")
    else:
        print(f"{spacer}{node}")

# Função principal
def parse(input, debug=False):
    return parser.parse(input, debug=debug)

# Teste para debug
if __name__ == '__main__':
    data ="""
    program BinarioParaInteiro;
    var
        bin: string;
        i, valor, potencia: integer;
    begin
        writeln('Introduza uma string binária:');
        readln(bin);
             
        valor := 0;
        potencia := 1;
        for i := length(bin) downto 1 do
        begin
            if bin[i] = '1' then
                valor := valor + potencia;
            potencia := potencia * 2;
        end;
             
        writeln('O valor inteiro correspondente é: ', valor);
    end.
"""
    result = parser.parse(data, debug=True)
    print(result)
    print_ast(result)
    
    try: 
        unused_vars, unused_functions = semantic_analyse(result)
        print("Semantic analysis passed.")
        if unused_vars:
            print("Unused variables:", unused_vars)
        if unused_functions:
            print("Unused functions:", unused_functions)
        generator = CodeGenerator(unused_vars, unused_functions)
        code = generator.generate_code(result)
        print(code)
    except SemanticError as e:
        print(f"Erro semântico: {e}")