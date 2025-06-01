import ply.lex as lex

tokens = [
    'ID',               # Identificadores
    'INTEGER',          # Números inteiros
    'REAL',             # Números reais
    'STRING',           # Strings
    
    # Operators
    'PLUS',             # +
    'MINUS',            # -
    'ASTERISK',         # *
    'DIVIDE',           # /
    'BECOMES',          # :=
    
    # Logical operators
    'EQ',               # =
    'NEQ',              # <>
    'LT',               # <
    'GT',               # >
    'LE',               # <=
    'GE',               # >=

    # Parentheses and brackets
    'LPAREN',           # (
    'RPAREN',           # )
    'LBRAC',            # [ ou (.
    'RBRAC',            # ] ou .)

    # Punctuation
    'SEMICOLON',        # ;
    'COLON',            # :
    'COMMA',            # ,
    'DOT',              # .
    'DOTDOT',           # ..

    #Palavras reservadas
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
    'NOT',
    'OF',
    'OR',
    'PROCEDURE',
    'PROGRAM',
    'REPEAT',
    'THEN',
    'TO',
    'UNTIL',
    'VAR',
    'WHILE',
    
    #Valores True e False
    'TRUE',
    'FALSE',
    
    # Tipos de dados
    'INTEGER_TYPE',
    'REAL_TYPE',
    'STRING_TYPE',
    'BOOLEAN_TYPE',
    'CHAR_TYPE',
]

# Operators
t_PLUS = r'\+'
t_MINUS = r'-'
t_ASTERISK = r'\*'
t_DIVIDE = r'/'
t_BECOMES = r':='

# Logical operators
t_LE = r'<='
t_GE = r'>='
t_EQ = r'='
t_NEQ = r'<>'
t_LT = r'<'
t_GT = r'>'

# Parentheses and brackets
t_LBRAC = r'\(\.|\['
t_RBRAC = r'\.\)|\]'

t_LPAREN = r'\('
t_RPAREN = r'\)'

# Punctuation
t_SEMICOLON = r';'
t_COLON = r':'
t_COMMA = r','
t_DOT = r'\.'
t_DOTDOT = r'\.\.'

t_ignore = ' \t'

#Palavras reservadas
def t_AND(t):
    r'\b(?i:and)\b'
    t.value = t.value.lower()
    return t

def t_ARRAY(t):
    r'\b(?i:array)\b'
    t.value = t.value.lower()
    return t

def t_BEGIN(t):
    r'\b(?i:begin)\b'
    t.value = t.value.lower()
    return t

def t_CASE(t):
    r'\b(?i:case)\b'
    t.value = t.value.lower()
    return t

def t_CONST(t):
    r'\b(?i:const)\b'
    t.value = t.value.lower()
    return t

def t_DIV(t):
    r'\b(?i:div)\b'
    t.value = t.value.lower()
    return t

def t_DO(t):
    r'\b(?i:do)\b'
    t.value = t.value.lower()
    return t

def t_DOWNTO(t):
    r'\b(?i:downto)\b'
    t.value = t.value.lower()
    return t

def t_ELSE(t):
    r'\b(?i:else)\b'
    t.value = t.value.lower()
    return t

def t_END(t):
    r'\b(?i:end)\b'
    t.value = t.value.lower()
    return t

def t_FOR(t):
    r'\b(?i:for)\b'
    t.value = t.value.lower()
    return t

def t_FUNCTION(t):
    r'\b(?i:function)\b'
    t.value = t.value.lower()
    return t

def t_GOTO(t):
    r'\b(?i:goto)\b'
    t.value = t.value.lower()
    return t

def t_IF(t):
    r'\b(?i:if)\b'
    t.value = t.value.lower()
    return t

def t_LABEL(t):
    r'\b(?i:label)\b'
    t.value = t.value.lower()
    return t

def t_MOD(t):
    r'\b(?i:mod)\b'
    t.value = t.value.lower()
    return t

def t_NOT(t):
    r'\b(?i:not)\b'
    t.value = t.value.lower()
    return t

def t_OF(t):
    r'\b(?i:of)\b'
    t.value = t.value.lower()
    return t

def t_OR(t):
    r'\b(?i:or)\b'
    t.value = t.value.lower()
    return t

def t_PROCEDURE(t):
    r'\b(?i:procedure)\b'
    t.value = t.value.lower()
    return t

def t_PROGRAM(t):
    r'\b(?i:program)\b'
    t.value = t.value.lower()
    return t

def t_REPEAT(t):
    r'\b(?i:repeat)\b'
    t.value = t.value.lower()
    return t

def t_THEN(t):
    r'\b(?i:then)\b'
    t.value = t.value.lower()
    return t

def t_TO(t):
    r'\b(?i:to)\b'
    t.value = t.value.lower()
    return t

def t_UNTIL(t):
    r'\b(?i:until)\b'
    t.value = t.value.lower()
    return t

def t_VAR(t):
    r'\b(?i:var)\b'
    t.value = t.value.lower()
    return t

def t_WHILE(t):
    r'\b(?i:while)\b'
    t.value = t.value.lower()
    return t

def t_TRUE(t):
    r'\b(?i:true)\b'
    t.value = True
    return t

def t_FALSE(t):
    r'\b(?i:false)\b'
    t.value = False
    return t

def t_INTEGER_TYPE(t):
    r'\b(?i:integer)\b'
    t.value = t.value.lower()
    return t

def t_REAL_TYPE(t):
    r'\b(?i:real)\b'
    t.value = t.value.lower()
    return t

def t_STRING_TYPE(t):
    r'\b(?i:string)\b'
    t.value = t.value.lower()
    return t

def t_BOOLEAN_TYPE(t):
    r'\b(?i:boolean)\b'
    t.value = t.value.lower()
    return t

def t_CHAR_TYPE(t):
    r'\b(?i:char)\b'
    t.value = t.value.lower()
    return t

def t_ID(t):
    r'[a-zA-Z][a-zA-Z0-9]*'
    return t

def t_REAL(t):
    r'-?\d+(\.\d+)?(\.|e-?)\d+'
    t.value = float(t.value)
    return t

def t_INTEGER(t):
    r'-?\d+'
    t.value = int(t.value)
    return t

def t_STRING(t):
    r"'((?:[^']+|'')*)'"
    t.value = t.value[1:-1]
    return t

# Ignored
t_ignore_COMMENT_LINE = r'\{.*?\}'
t_ignore_COMMENT_MULTILINE = r'\(\*(.|\n)*?\*\)'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Caracter ilegal '{t.value[0]}' na linha {t.lexer.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()