from calc_lex import lexer

prox_simb = ('Erro', '', 0, 0)

def parseError(simb):
    print("Erro sintático, token inesperado: ", simb)

def rec_term(simb):
    global prox_simb
    if prox_simb is not None and prox_simb.type == simb:
        value = int(prox_simb.value) if simb == 'NUM' else None
        prox_simb = lexer.token()
        return value
    else:
        parseError(prox_simb)
        return None

# Exp -> Mul Exp2
def rec_Exp():
    print("Derivando por: Exp -> Mul Exp2")
    value = rec_Mul()
    value += rec_Exp2(value)
    print("Reconheci: Exp -> Mul Exp2")
    return value

# Exp2 -> '+' Exp
# Exp2 -> '-' Exp
# Exp2 -> epslon
def rec_Exp2(current_value):
    global prox_simb
    if prox_simb is not None and prox_simb.type == 'ADD':
        print("Derivando por: Exp2 -> '+' Exp")
        rec_term('ADD')
        value = rec_Exp()
        print("Reconheci: Exp2 -> '+' Exp")
        return value
    elif prox_simb is not None and prox_simb.type == 'SUB':
        print("Derivando por: Exp2 -> '-' Exp")
        rec_term('SUB')
        value = rec_Exp()
        print("Reconheci: Exp2 -> '-' Exp")
        return -value
    else:
        print("Derivando por: Exp2 -> epslon")
        print("Reconheci: Exp2 -> epslon")
        return 0

# Mul -> num Mul2
def rec_Mul():
    print("Derivando por: Mul -> num Mul2")
    value = rec_term('NUM')
    value *= rec_Mul2(value)
    print("Reconheci: Mul -> num Mul2")
    return value

# Mul2 -> '*' Mul
# Mul2 -> epslon
def rec_Mul2(current_value):
    global prox_simb
    if prox_simb is not None and prox_simb.type == 'MUL':
        print("Derivando por: Mul2 -> '*' Mul")
        rec_term('MUL')
        value = rec_Mul()
        print("Reconheci: Mul2 -> '*' Mul")
        return value
    else:
        print("Derivando por: Mul2 -> epslon")
        print("Reconheci: Mul2 -> epslon")
        return 1

def rec_Parser(data):
    global prox_simb
    lexer.input(data)
    prox_simb = lexer.token()
    result = rec_Exp()
    print("Resultado final: ", result)
