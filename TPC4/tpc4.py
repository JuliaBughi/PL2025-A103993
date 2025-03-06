import ply.lex as lex

frase = ''' 
        # DBPedia: obras de Chuck Berry
 
        select ?nome ?desc where {
            ?s a dbo:MusicalArtist.
            ?s foaf:name "Chuck Berry"@en .
            ?w dbo:artist ?s.
            ?w foaf:name ?nome.
            ?w dbo:abstract ?desc
        } LIMIT 1000'''

tokens = (
    'COMMENT',        # #
    'SELECT',         # SELECT
    'WHERE',          # WHERE
    'LIMIT',          # LIMIT
    'VAR',            # ?
    'PREFIX',         # prefixos
    'LANGSTRING',     # "texto"@en
    'NUMBER',         # Números
    'LBRACE',         # {
    'RBRACE',         # }
    'DOT',            # .
    'A'               # 'a' keyword (rdf:type)
)

t_COMMENT = r"\#.*"
t_SELECT = r"select"
t_WHERE = r"where"
t_LIMIT = r"LIMIT"
t_VAR = r"\?[a-z]+"
t_PREFIX = r"[a-zA-Z]+:[a-zA-Z]+"
t_LANGSTRING = r'"[^"]*"@[a-z]{2}'
def t_NUMBER(t):
    r"\d+"
    t.value = int(t.value)
    return t
t_LBRACE = r"\{"
t_RBRACE = r"\}"
t_DOT = r"\."
t_A = r"a"
t_ignore = ' \t'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Caractere ilegal '{t.value[0]}' na linha {t.lexer.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()

lexer.input(frase)

for l in lexer:
    print(l)
