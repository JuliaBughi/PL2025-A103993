import ply.lex as lex

tokens = ('NUM', 'ADD', 'SUB', 'MUL', 'AP', 'FP')

def t_NUM(p):
    r'\d+'
    p.value = int(p.value)
    return p

t_ADD = r'\+'
t_SUB = r'-'
t_MUL = r'\*'
t_AP = r'\('
t_FP = r'\)'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore = '\t '

def t_error(t):
    print('Carácter desconhecido: ', t.value[0], 'Linha: ', t.lexer.lineno)
    t.lexer.skip(1)

lexer = lex.lex()