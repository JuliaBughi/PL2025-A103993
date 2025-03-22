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

# Exp -> Termo Exp2
def rec_Exp():
    print("Derivando por: Exp -> Termo Exp2")
    value = rec_Termo()
    value = rec_Exp2(value)
    print("Reconheci: Exp -> Termo Exp2, valor:", value)
    return value

# Exp2 -> '+' Exp
# Exp2 -> '-' Exp
# Exp2 -> epslon
def rec_Exp2(current_value):
    global prox_simb
    if prox_simb is not None and prox_simb.type == 'ADD':
        print("Derivando por: Exp2 -> '+' Exp")
        rec_term('ADD')
        right_value = rec_Exp()
        result = current_value + right_value
        print("Reconheci: Exp2 -> '+' Exp, resultado parcial:", result)
        return result
    elif prox_simb is not None and prox_simb.type == 'SUB':
        print("Derivando por: Exp2 -> '-' Exp")
        rec_term('SUB')
        right_value = rec_Exp()
        result = current_value - right_value
        print("Reconheci: Exp2 -> '-' Exp, resultado parcial:", result)
        return result
    else:
        print("Derivando por: Exp2 -> epslon")
        print("Reconheci: Exp2 -> epslon, valor atual:", current_value)
        return current_value

# Termo -> Fator Termo2
def rec_Termo():
    print("Derivando por: Termo -> Fator Termo2")
    value = rec_Fator()
    value = rec_Termo2(value)
    print("Reconheci: Termo -> Fator Termo2, valor:", value)
    return value

# Termo2 -> '*' Termo
# Termo2 -> epslon
def rec_Termo2(current_value):
    global prox_simb
    if prox_simb is not None and prox_simb.type == 'MUL':
        print("Derivando por: Termo2 -> '*' Termo")
        rec_term('MUL')
        right_value = rec_Termo()
        result = current_value * right_value
        print("Reconheci: Termo2 -> '*' Termo, resultado parcial:", result)
        return result
    else:
        print("Derivando por: Termo2 -> epslon")
        print("Reconheci: Termo2 -> epslon, valor atual:", current_value)
        return current_value

# Fator -> '(' Exp ')'
# Fator -> num
def rec_Fator():
    global prox_simb
    if prox_simb is not None and prox_simb.type == 'AP':
        print("Derivando por: Fator -> '(' Exp ')'")
        rec_term('AP')
        value = rec_Exp()
        rec_term('FP')
        print("Reconheci: Fator -> '(' Exp ')', valor:", value)
        return value
    elif prox_simb is not None and prox_simb.type == 'NUM':
        print("Derivando por: Fator -> num")
        value = rec_term('NUM')
        print("Reconheci: Fator -> num, valor:", value)
        return value
    else:
        parseError(prox_simb)
        return None

def rec_Parser(data):
    global prox_simb
    lexer.input(data)
    prox_simb = lexer.token()
    result = rec_Exp()
    print("Resultado final: ", result)
    return result

