def analisar_dataset_musical(file_path):

    compositores = set()  # evita repetidos
    obras_por_periodo = {}
    
    entre_aspas = False  # verifica se está entre aspas
    linha_atual = []
    campo_atual = []
    header_processed = False
    indices = {}
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        
        for char in content:
            if char == '"':  # sempre que encontra aspas inverte o boolean
                entre_aspas = not entre_aspas
            elif char == ';' and not entre_aspas:  # se encontrar um ';' fora de aspas, troca de campo
                linha_atual.append(''.join(campo_atual))
                campo_atual = []
            elif char == '\n' and not entre_aspas:  # se encontrar um '\n' fora de aspas, troca de linha
                linha_atual.append(''.join(campo_atual))
                
                if not header_processed:  # processa a primeira linha do csv
                    headers = [col.strip() for col in linha_atual]
                    indices = {
                        'nome': headers.index('nome'),
                        'periodo': headers.index('periodo'),
                        'compositor': headers.index('compositor')
                    }
                    header_processed = True
                else:  # se não estivermos na primeira linha, vai buscar o campo correto com os índices indicados
                    nome = linha_atual[indices['nome']].strip()
                    periodo = linha_atual[indices['periodo']].strip()
                    compositor = linha_atual[indices['compositor']].strip()
                    
                    compositores.add(compositor)  # adiciona o compositor ao set
                    if periodo not in obras_por_periodo:
                        obras_por_periodo[periodo] = []
                    obras_por_periodo[periodo].append(nome)  # adiciona o nome da obra ao período indicado
                
                linha_atual = []  # reset a linha
                campo_atual = []  # reset ao campo
            else:  # adiciona char ao campo
                campo_atual.append(char)
        
        if campo_atual and header_processed:  # caso de última linha não terminar com '\n'
            linha_atual.append(''.join(campo_atual))
            nome = linha_atual[indices['nome']].strip()
            periodo = linha_atual[indices['periodo']].strip()
            compositor = linha_atual[indices['compositor']].strip()
            
            compositores.add(compositor)
            if periodo not in obras_por_periodo:
                obras_por_periodo[periodo] = []
            obras_por_periodo[periodo].append(nome)
    
    lista_compositores = sorted(list(compositores))

    obras_ordenadas_por_periodo = {
        periodo: sorted(obras)
        for periodo, obras in obras_por_periodo.items()
    }
    
    return lista_compositores, obras_ordenadas_por_periodo

def imprimir_resultados(lista_compositores, obras_por_periodo):
    print("1. Lista de Compositores:")
    for compositor in lista_compositores:
        print(f"   - {compositor}")
    
    print("\n2. Distribuição de Obras por Período:")
    for periodo, obras in obras_por_periodo.items():
        print(f"   - {periodo}: {len(obras)} obras")
    
    print("\n3. Obras por Período:")
    for periodo, obras in obras_por_periodo.items():
        print(f"\n   {periodo}:")
        for obra in obras:
            print(f"   - {obra}")

arquivo_csv = "obras.csv"
compositores, obras = analisar_dataset_musical(arquivo_csv)
imprimir_resultados(compositores, obras)
