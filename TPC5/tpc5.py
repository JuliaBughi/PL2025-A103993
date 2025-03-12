import ply.lex as lex
import json
import datetime 

tokens = (
    'LISTAR',
    'MOEDA',
    'SELECIONAR',
    'SAIR',
)

t_LISTAR = r'LISTAR'
t_MOEDA = r'MOEDA'
t_SELECIONAR = r'SELECIONAR'
t_SAIR = r'SAIR'

def t_error(t):
    print(f"Comando inválido: {t.value}")
    t.lexer.skip(len(t.value))

lexer = lex.lex()

def carregar_stock():
    with open('stock.json', 'r') as file:
        return json.load(file)

def salvar_stock(stock):
    with open('stock.json', 'w') as file:
        json.dump(stock, file, indent=4)

def listar_stock(stock):
    print("maq:")
    print("cod | nome | quantidade | preço")
    print("---------------------------------")
    for item in stock:
        print(f'{item["cod"]} | {item["nome"]} | {item["quant"]} | {item["preco"]}')

def formatar_saldo(saldo):
    euros = int(saldo)
    centavos = int((saldo - euros) * 100)
    return f"{euros}e{centavos}c"

def adicionar_moeda(moedas, saldo):
    valor_moeda = {'2e': 2.0, '1e': 1.0, '50c': 0.5, '20c': 0.2, '10c': 0.1, '5c': 0.05, '2c': 0.02, '1c': 0.01}
    moedas = moedas.split(', ')
    for moeda in moedas:
        moeda = moeda.strip().replace(' .', '.').strip('.')
        if moeda in valor_moeda:
            saldo += valor_moeda[moeda]
        else:
            print(f"Valor de moeda inválido: {moeda}")
    
    print(f"maq: Saldo = {formatar_saldo(saldo)}")
    return saldo

def selecionar_produto(stock, codigo, saldo):
    produto = next((item for item in stock if item["cod"] == codigo), None)
    if produto:
        if saldo >= produto["preco"]:
            if produto["quant"] > 0:
                produto["quant"] -= 1
                saldo -= produto["preco"]
                print(f'maq: Pode retirar o produto dispensado "{produto["nome"]}"')
                print(f"maq: Saldo = {formatar_saldo(saldo)}")
            else:
                print("maq: Produto indisponível.")
        else:
            print(f"maq: Saldo insuficiente para satisfazer o seu pedido\nmaq: Saldo = {formatar_saldo(saldo)}; Pedido = {formatar_saldo(produto['preco'])}")
    else:
        print("maq: Produto inexistente.")
    return saldo

def calcular_troco(saldo):
    moedas = {1.0: '1e', 0.5: '50c', 0.2: '20c', 0.1: '10c', 0.05: '5c', 0.02: '2c', 0.01: '1c'}
    troco = []
    for valor, nome in moedas.items():
        quantidade = int(saldo // valor)
        if quantidade > 0:
            troco.append(f"{quantidade}x {nome}")
            saldo -= quantidade * valor
    return troco
 
def main():
    stock = carregar_stock()
    saldo = 0
    print(f"maq: {datetime.datetime.now().date()}, Stock carregado, Estado atualizado.")
    print("maq: Bom dia. Estou disponível para atender o seu pedido.")

    while True:
        comando = input(">> ").strip().split(maxsplit=1)
        lexer.input(comando[0])
        token = lexer.token()

        if not token:
            continue

        if token.type == 'LISTAR':
            listar_stock(stock)

        elif token.type == 'MOEDA':
            if len(comando) > 1:
                saldo = adicionar_moeda(comando[1], saldo)
            else:
                print("Comando inválido: falta o valor da moeda")
            
        elif token.type == 'SELECIONAR':
            if len(comando) > 1:
                saldo = selecionar_produto(stock, comando[1], saldo)
            else:
                print("Comando inválido: falta o código do produto")
            
        elif token.type == 'SAIR':
            salvar_stock(stock)
            troco = calcular_troco(saldo)
            if troco:
                print("maq: Pode retirar o troco: " + ", ".join(troco) + ".")
            print("maq: Até à próxima")
            break

if __name__ == "__main__": 
    main()
