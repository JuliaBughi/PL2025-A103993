import sys

def somador_onoff(texto):
    isOn = True
    acc = 0
    i=0

    while i<len(texto):
        valor = 0

        if texto[i] in "0123456789":
            while texto[i] in "0123456789":
                valor = valor * 10 + int(texto[i])
                i = i+1
            if isOn:
                acc += valor

        elif texto[i] in "Oo":
            if texto[i+1] in "Nn":
                isOn = True

            elif texto[i+1] in "Ff":
                if texto[i+2] in "Ff":
                    isOn = False

            i = i+1

        elif texto[i] in "=":
            print(acc)
            i = i+1

        else:
            i = i+1

for linha in sys.stdin:
    somador_onoff(linha)


