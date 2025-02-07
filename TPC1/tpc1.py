import sys

def somador_onoff(texto):
    isOn = True
    acc = 0
    i = 0

    while i < len(texto):
        valor = 0

        if texto[i] in "0123456789" and isOn:
            while texto[i] in "0123456789":
                valor = valor * 10 + int(texto[i])
                i += 1

            acc += valor
        
        elif texto[i] in "Oo":
            if i + 1 < len(texto) and texto[i+1] in "Nn":
                isOn = True
                i += 2
            
            elif i + 2 < len(texto) and texto[i+1] in "Ff" and texto[i+2] in "Ff":
                isOn = False
                i += 3
            
            else:
                i += 1
        
        elif texto[i] == "=":
            print(acc)
            i += 1
        
        else:
            i += 1

for linha in sys.stdin:
    somador_onoff(linha)
