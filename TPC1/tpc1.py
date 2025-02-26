import sys

def somador_onoff(line):
    on = True
    acc = 0
    reading_value = 0
    i = 0

    while i < len(line):
        if line[i] in '0123456789' and on:
            reading_value = reading_value * 10 + int(line[i])
        else:
            if reading_value > 0:
                acc += reading_value
                reading_value = 0
            if line[i] == '=':
                print(str(acc))
            elif line[i:(i + 2)].lower() == 'on':
                on = True
                i += 1
            elif line[i:(i + 3)].lower() == 'off':
                on = False
                i += 2
        i += 1

    if reading_value > 0:
        acc += reading_value
        reading_value = 0

    print(f"Valor final do acumulador: {acc}")       

for linha in sys.stdin:
    somador_onoff(linha)
