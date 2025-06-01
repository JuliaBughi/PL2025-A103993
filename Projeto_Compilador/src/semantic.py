predefined_functions = {
    # Write and Read
    'write': {
        'is_procedure': True,
        'args': {
            'value': ['integer', 'real', 'string', 'char', 'boolean']
        },
        'arbitrary_args': True,  # permite múltiplos argumentos
        'return_type': 'void'
    },
    'writeln': {
        'is_procedure': True,
        'args': {
            'value': ['integer', 'real', 'string', 'char', 'boolean']
        },
        'arbitrary_args': True,  # permite múltiplos argumentos
        'return_type': 'void'
    },
    'read': {
        'is_procedure': True,
        'args': {
            'variable': ['integer', 'real', 'string', 'char']
        },
        'arbitrary_args': True,  # permite múltiplos argumentos
        'return_type': 'void'
    },
    'readln': {
        'is_procedure': True,
        'args': {
            'variable': ['integer', 'real', 'string', 'char']
        },
        'arbitrary_args': True,  # permite múltiplos argumentos
        'return_type': 'void'
    },

    'length': {
        'is_procedure': False,
        'args': {
            'string': ['string']
        },
        'return_type': 'integer'
    },

    # Conversão caracteres
    'ord': {
        'is_procedure': False,
        'args': {
            'char': ['char']
        },
        'return_type': 'integer'
    },
    'chr': {
        'is_procedure': False,
        'args': {
            'integer': ['integer']
        },
        'return_type': 'char'
    },

    # Funções numéricas
    'sin': {
        'is_procedure': False,
        'args': {
            'angle': ['real', 'integer']
        },
        'return_type': 'real'
    },
    'cos': {
        'is_procedure': False,
        'args': {
            'angle': ['real', 'integer']
        },
        'return_type': 'real'
    },
    'abs': { # com ifs
        'is_procedure': False,
        'args': {
            'number': ['integer', 'real']
        },
        'return_type': 'real'
    },
    'trunc': { #FTOI
        'is_procedure': False,
        'args': {
            'number': ['integer', 'real']
        },
        'return_type': 'integer'
    },
    'round': { #talvez dê para fazer com ifs
        'is_procedure': False,
        'args': {
            'number': ['real']
        },
        'return_type': 'integer'
    },
}

#Exceção para erros semânticos
class SemanticError(Exception):
    def __init__(self, message, line=None):
        self.message = message
        self.line = line # TODO: noção de número de linha
        super().__init__(f"Linha {line}: {message}" if line else message)

# Classe para representar uma variável
class Variable:
    def __init__(self, name, var_type, is_const=False, array_index_type=None):
        self.name = name
        self.type = var_type
        self.is_const = is_const
        self.n_uses = 0
        self.array_index_type = array_index_type  # se for um array, guardar o tipo do índice
    
    def use(self):
        """Marca um uso desta variável, incrementando o contador de usos"""
        self.n_uses += 1

    def is_array(self):
        """Verifica se a variável é um array"""
        return self.type.startswith('array_of_') if isinstance(self.type, str) else False
    
    def get_type(self) -> str:
        """Retorna o tipo da variável, considerando arrays"""
        if self.is_array():
            return self.type.replace('array_of_', '')
        return self.type

# Classe para representar uma função ou procedimento
class Function:
    def __init__(self, name: str, args, return_type: str, is_procedure=False):
        self.name = name
        self.is_procedure = is_procedure
        self.return_type = return_type
        self.args = args # mapa dos argumentos -> {} ou {nome -> tipo}
        self.n_uses = 0
        self.has_return = False
    
    def use(self):
        """Marca um uso desta função, incrementando o contador de usos"""
        self.n_uses += 1


# Classe para representar um contexto (global, dentro de uma função ou for_loop)
class Context:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.variables = {}  # nome -> Variable
        self.functions = {}  # nome -> Function
        self.children = []
        
        if parent:
            parent.children.append(self)
    
    def declare_var(self, name: str, var_type: str, is_const=False, array_index_type=None):
        """Declara uma variável no contexto atual"""
        if name in self.variables:
            raise SemanticError(f"Variável '{name}' já declarada neste contexto")
        
        self.variables[name] = Variable(name, var_type, is_const)
    
    def declare_function(self, name: str, return_type: str, param_types=None, is_procedure=False):
        """
        Declara uma função ou procedimento no contexto atual.
        Se já existir uma função com o mesmo nome, lança um erro.
        """
        if name in self.functions:
            raise SemanticError(f"Função/Procedimento '{name}' já declarado neste contexto")
        
        if param_types is None:
            param_types = {}
        
        self.functions[name] = Function(name, param_types, return_type, is_procedure)
    
    def use_var(self, name):
        """
        Aumenta os usos de uma variável.
        Se a variável não estiver declarada, lança um erro.
        """
        if name not in self.variables:
            if self.parent:
                self.parent.use_var(name)
            else:
                raise SemanticError(f"Variável '{name}' não declarada neste contexto")
        else:
            self.variables[name].use()

    def use_function(self, name):
        """
        Aumenta os usos de uma função.
        Se a função não estiver declarada, lança um erro.
        """
        if name.lower() in predefined_functions:
            # Se for uma função pré-definida, não lança erro
            return

        if name not in self.functions:
            if self.parent:
                self.parent.use_function(name)
            else:
                raise SemanticError(f"Função/Procedimento '{name}' não declarado neste contexto")
        else:
            self.functions[name].use()
    
    def mark_func_return(self, name: str):
        """
        Marca que uma função tem um retorno.
        Se a função não estiver declarada, lança um erro.
        """
        if name not in self.functions:
            if self.parent:
                self.parent.mark_func_return(name)
            else:
                raise SemanticError(f"Função '{name}' não declarada neste contexto")
        
        self.functions[name].has_return = True

    
    def find_var(self, name: str) -> Variable | None: 
        """
        Procura uma variável no contexto atual e nos contextos pais.
        Retorna a variável? se encontrada, None caso contrário.
        """
        if name in self.variables:
            return self.variables[name]
        
        if self.parent:
            return self.parent.find_var(name)
        
        return None

    def find_function(self, name: str):
        """
        Procura uma função no contexto atual e nos contextos pais.
        Retorna a função se encontrada, None caso contrário.
        """
        if name.lower() in predefined_functions:
            # Se for uma função pré-definida, retorna uma função com os detalhes
            func_details = predefined_functions[name.lower()]
            return Function(name, func_details['args'], func_details['return_type'], is_procedure=func_details['is_procedure'])

        if name in self.functions:
            return self.functions[name]
        
        if self.parent:
            return self.parent.find_function(name)
        
        return None
    
    def is_local_var(self, name: str) -> Variable:
        """
        Verifica se uma variável é local a este contexto.
        """
        return name in self.variables
    

current_context = Context("global")
contexts = []

#Início
def semantic_analyse(ast):
    """Início da análise semântica
    Guarda o contexto global e inicia a análise.
    Devolve 2 listas de variáveis e funções não usadas, respetivamente.
    """
    global current_context, contexts
    if ast[0] != 'program':
        raise SemanticError("AST root must be 'program'")
    _, name, content = ast
    
    current_context = Context(name)
    contexts.append(current_context)

    analyse_content(content)
    unused_vars, unused_functions = check_unused_vars_functions()
    return unused_vars, unused_functions

def analyse_content(content):
    """Análise de um conteúdo do programa ou de uma função
    Primeiro processa as declarações de variáveis e constantes, depois as declarações de funções.
    Verifica os tipos das contantes e das expressões, os ranges dos arrays e regista no contexto atual.
    Por fim analisa as expressões do bloco begin.
    """
    global current_context
    _, declarations, begin_block = content

    # Processar as declarações de variáveis e constantes
    for decl in declarations:
        if decl[0] == 'const_list':
            for const in decl[1]:
                name, value = const
                typ = evaluate_expr(value)
                current_context.declare_var(name, typ, is_const=True)
        elif decl[0] == 'var_list':
            for var in decl[1]:
                _, ids, var_type = var
                array_index_type = None
                if isinstance(var_type, tuple) and var_type[0] == 'array':
                    # ('array', range, type)
                    _, range_lower, range_upper = var_type[1]
                    lower_type = evaluate_expr(range_lower)
                    upper_type = evaluate_expr(range_upper)

                    if lower_type != upper_type:
                        raise SemanticError(f"Tipo incompatível para o intervalo do array: {lower_type} vs {upper_type}")
                    if lower_type not in ['integer', 'char', 'boolean']:
                        raise SemanticError(f"Tipo do índice do array deve ser INTEGER, CHAR ou BOOLEAN, mas encontrado {lower_type}")
                    if range_lower > range_upper and lower_type in ['integer', 'char']:
                        raise SemanticError(f"Limite inferior do array ({range_lower}) é maior que o limite superior ({range_upper})")
                    
                    var_type = f"array_of_{var_type[2]}"
                    array_index_type = lower_type
                for id in ids:
                    current_context.declare_var(id, var_type, array_index_type=array_index_type)
        else:
            # Processar as declarações de funções e procedimentos
            process_procedures_and_functions(decl)

    # Analisar o bloco inicial
    analyse_statements(begin_block[1])

def process_procedures_and_functions(proc_or_func):
    global current_context, contexts
    """
    Processa declarações de procedimentos e funções.
    Verifica se já existe uma declaração anterior e guarda no contexto atual as características da função ou procedimento.
    """
    if proc_or_func[0] == 'procedure':
        # ('procedure', name, args, do_block)
        _, name, args, do_block = proc_or_func
        if current_context.find_function(name):
            raise SemanticError(f"Procedimento '{name}' já declarado")
        if args == []:
            args_list = []
        else:
            args_list = args[1]

        args_types = {}
        for arg in args_list:
            args_types[arg[1]] = arg[2]

        current_context.declare_function(name, 'void', args_types, is_procedure=True)
        current_context = Context(name, current_context)
        contexts.append(current_context)
        analyse_content(do_block)
        current_context = current_context.parent
    elif proc_or_func[0] == 'function':
        # ('function', name, args, return_type, do_block)
        _, name, args, return_type, do_block = proc_or_func
        if current_context.find_function(name):
            raise SemanticError(f"Função '{name}' já declarada")
        if args == []:
            args_list = []
        else:
            args_list = args[1]
        
        args_types = {}
        for arg in args_list:
            args_types[arg[1]] = arg[2]

        current_context.declare_function(name, return_type, args_types)
        current_context = Context(name, current_context)
        
        for arg in args_list:
            current_context.declare_var(arg[1], arg[2])

        contexts.append(current_context)
        analyse_content(do_block)
        current_context = current_context.parent
        if not current_context.find_function(name).has_return:
            raise SemanticError(f"Função '{name}' deve ter um valor de return do tipo, mas não foi encontrado")
    else:
        raise SemanticError(f"Tipo de declaração desconhecido: {proc_or_func[0]}")

def analyse_statements(statements):
    """Análise de uma lista de instruções
    Verifica os tipos das expressões, atribuições, condições e loops.
    """
    global current_context, contexts
    for stmt in statements:
        if stmt is None:
            continue
        match stmt[0]:
            case 'assignment':
                _, var_name, expr = stmt
                
                var = current_context.find_var(var_name)
                if var_name == current_context.name:
                    function = current_context.find_function(var_name)
                    expr_type = evaluate_expr(expr)
                    if function and not function.is_procedure:
                        if expr_type != function.return_type:
                            raise SemanticError(f"Tipo de retorno da função '{var_name}' deve ser {function.return_type}, mas encontrado {expr_type}")
                    current_context.parent.functions[var_name].has_return = True
                    continue
                if var is None:
                    raise SemanticError(f"Variável '{var_name}' não foi declarada antes do uso")
                elif var.is_const:
                    raise SemanticError(f"Não é possível atribuir valor a constante '{var_name}'")
                elif current_context.name == f"FOR_LOOP_{var_name}" and current_context.is_local_var(var_name):
                    raise SemanticError(f"Não é possível atribuir valor à variável de controlo '{var_name}' dentro do loop FOR")
                else:
                    current_context.use_var(var_name)
                
                expr_type = evaluate_expr(expr)
                if var.get_type() == 'char' and expr_type == 'string' and len(expr) == 1:
                    continue
                elif var.get_type() != expr_type:
                    raise SemanticError(f"Atribuição de tipo inválido à variável '{var_name}': esperado {var.get_type()}, fornecido {expr_type}")
            case 'if':
                # ('if', condition_expr, then_stmt, else_stmt?)
                cond_type = evaluate_expr(stmt[1])
                if cond_type != 'boolean':
                    raise SemanticError(f"Condição do IF deve ser booleana, mas encontrado {cond_type}")
                analyse_statements([stmt[2]])
                if len(stmt) > 3:
                    analyse_statements([stmt[3]])
            
            case 'while':
                # ('while', condition_expr, do_stmt)
                _, cond_expr, do_stmt = stmt

                cond_type = evaluate_expr(cond_expr)
                if cond_type != 'boolean':
                    raise SemanticError(f"Condição WHILE deve ser booleana, mas encontrado {cond_type}.")
                
                analyse_statements([do_stmt])

            case 'repeat':
                # ('repeat', do_stmt, condition_expr)
                _, do_stmt, cond_expr = stmt

                analyse_statements([do_stmt])

                cond_type = evaluate_expr(cond_expr)
                if cond_type != 'boolean':
                    raise SemanticError(f"Condição REPEAT deve ser booleana, mas encontrado {cond_type}.")
                
            case 'for':
                # ('for', assignment_node, direction, final_expr, do_stmt)
                _, assignment_node, direction, final_expr, do_stmt = stmt

                if assignment_node[0] != 'assignment':
                    raise SemanticError(f"A inicialização do loop FOR deve ser uma atribuição, mas encontrado: {assignment_node[0]}.")

                _, control_var_name, initial_expr = assignment_node
                current_context.use_var(control_var_name)
                current_context = Context(f"FOR_LOOP_{control_var_name}", current_context)
                contexts.append(current_context)
                
                control_var = current_context.find_var(control_var_name)
                
                if control_var is None:
                    raise SemanticError(f"Variável de controle '{control_var_name}' do FOR não declarada.")
                
                if control_var.get_type() not in ['integer', 'char', 'boolean']:
                     raise SemanticError(f"Variável de controle '{control_var_name}' deve ser tipo INTEGER, CHAR ou BOOLEAN, mas encontrado {control_var.type}.")

                initial_val_type = evaluate_expr(initial_expr)
                if not (initial_val_type == control_var.get_type()):
                    if control_var.get_type() == 'char' and initial_val_type == 'string' and len(initial_expr) == 1:
                        pass
                    else:
                        raise SemanticError(f"Tipo da expressão inicial ({initial_val_type}) incompatível com a variável de controle '{control_var_name}' ({control_var.type}).")

                final_val_type = evaluate_expr(final_expr)
                if not (final_val_type == control_var.get_type()):
                    if control_var.get_type() == 'char' and final_val_type == 'string' and len(initial_expr) == 1:
                        pass
                    else:
                        raise SemanticError(f"Tipo da expressão final ({final_val_type}) incompatível com a variável de controle '{control_var_name}' ({control_var.type}).")

                current_context.declare_var(control_var_name, control_var.get_type())
                current_context.use_var(control_var_name)

                analyse_statements([do_stmt])
                current_context = current_context.parent
            case 'case':
                # ('case', expr, case_labels)
                _, case_expr, case_labels = stmt
                
                # Avaliar o tipo da expressão do case
                case_expr_type = evaluate_expr(case_expr)
                
                # Verificar se o tipo da expressão é compatível com case (deve ser ordinal)
                if case_expr_type not in ['integer', 'char', 'boolean']:
                    raise SemanticError(f"Expressão CASE deve ser de tipo ordinal (INTEGER, CHAR ou BOOLEAN), mas encontrado {case_expr_type}")
                
                # Verificar cada case_label
                used_values = set()
                for case_label in case_labels:
                    if case_label[0] == 'case_label':
                        # ('case_label', values, statement)
                        _, values, case_stmt = case_label
                        
                        # Verificar cada valor no case_label
                        for value in values:
                            value_type = evaluate_expr(value)
                            
                            # Verificar compatibilidade de tipos
                            if value_type != case_expr_type:
                                if case_expr_type == 'char' and value_type == 'string' and len(str(value)) == 1:
                                    pass
                                else:
                                    raise SemanticError(f"Valor '{value}' no CASE deve ser do mesmo tipo da expressão ({case_expr_type}), mas encontrado {value_type}")
                            
                            # Verificar valores duplicados
                            if value in used_values:
                                raise SemanticError(f"Valor '{value}' duplicado no statement CASE")
                            used_values.add(value)
                        
                        # Analisar o statement do case_label
                        if case_stmt is not None:
                            analyse_statements([case_stmt])
            case 'begin_block':
                analyse_statements(stmt[1])
            case 'func_call':
                # ('func_call', func_name, params?)
                func_name = stmt[1]
                params = stmt[2] if len(stmt) > 2 else []
                func = current_context.find_function(func_name)
                if not func:
                    raise SemanticError(f"Função '{func_name}' não declarada")
                
                current_context.use_function(func_name)
                expected_params = list(func.args.items()) if func.args else []
                check_args(func_name, params, expected_params)
            #TODO : ver se falta algum tipo de statement (acho que falta o case)


def evaluate_expr(expr):
    global current_context
    """Percebe qual o tipo de uma expressão
    Se for um tipo imediato, devolve o tipo.
    Se for uma expressão, verifica os tipos dos operadores presentes e devolve o tipo resultante.
    Se for uma variável, devolve o tipo da variável.
    Se for uma chamada de função, verifica os tipos dos argumentos e devolve o tipo de retorno.
    """
    if isinstance(expr, bool):
        return 'boolean'
    elif isinstance(expr, int):
        return 'integer'
    elif isinstance(expr, float):
        return 'real'
    elif isinstance(expr, str):
        return 'string'
    elif isinstance(expr, tuple):
        expr_type = expr[0]

        if expr_type == 'expr_bool':
            # ('expr_bool', left_expr_ast, op_rel, right_expr_ast)
            _, left_ast, op_rel, right_ast = expr
            left_type = evaluate_expr(left_ast)
            right_type = evaluate_expr(right_ast)

            if (left_type == 'integer' and right_type == 'real') or \
               (left_type == 'real' and right_type == 'integer'):
                pass
            elif left_type == right_type:
                pass
            else:
                raise SemanticError(f"Tipo incompatível para operador relacional '{op_rel}': {left_type} vs {right_type}")
            return 'boolean'
        elif expr_type == 'not':
            # ('not', expr_ast)
            _, expr_ast = expr
            expr_type = evaluate_expr(expr_ast)
            if expr_type != 'boolean':
                raise SemanticError(f"Operador NOT deve ser aplicado a uma expressão booleana, mas encontrado {expr_type}")
            return 'boolean'
        elif expr_type == 'expr' or expr_type == 'termo':
            # (expr_type, left_expr_ast, op, right_expr_ast)
            _, left_ast, op, right_ast = expr
            left_type = evaluate_expr(left_ast)
            right_type = evaluate_expr(right_ast)

            if op in ['and', 'or']:
                if left_type == 'boolean' and right_type == 'boolean':
                    return 'boolean'
                else:
                    raise SemanticError(f"Tipo incompatível para operador lógico '{op}': {left_type} e {right_type} devem ser booleanos")

            elif op in ['+', '-', '*']:
                if left_type == 'integer' and right_type == 'integer':
                    return 'integer'
                elif (left_type == 'integer' and right_type == 'real') or \
                     (left_type == 'real' and right_type == 'integer') or \
                     (left_type == 'real' and right_type == 'real'):
                    return 'real' # Se algum for real, o resultado é real
                elif op == '+' and left_type == 'string' and right_type == 'string':
                    return 'string' # Concatenação de strings
                else:
                    raise SemanticError(f"Tipo incompatível para operador aritmético '{op}': {left_type} vs {right_type}")

            # Divisão é real
            elif op == '/':
                if (left_type in ['integer', 'real']) and (right_type in ['integer', 'real']):
                    return 'real'
                else:
                    raise SemanticError(f"Tipo incompatível para operador de divisão '/': {left_type} vs {right_type}")

            elif op == 'mod':
                if left_type == 'integer' and right_type == 'integer':
                    return 'integer'
                else:
                    raise SemanticError(f"Tipo incompatível para operador MOD: {left_type} e {right_type} devem ser inteiros")
            elif op == 'div':
                if left_type == 'integer' and right_type == 'integer':
                    return 'integer'
                else:
                    raise SemanticError(f"Tipo incompatível para operador DIV: {left_type} e {right_type} devem ser inteiros")
            else:
                raise SemanticError(f"Operador desconhecido: {op}")
       
        elif expr_type == 'var':
            # ('var', var_name, [index_expr])
            var_name = expr[1]
            variable = current_context.find_var(var_name)
            if not variable:
                raise SemanticError(f"Variável '{var_name}' não declarada")
            
            current_context.use_var(var_name)

            if len(expr) == 2:
                return variable.get_type()
            else: # Array
                if not variable.is_array() and variable.get_type() != 'string':
                    raise SemanticError(f"Variável '{var_name}' não é um array")
                
                var_type = variable.get_type()
                index_expr_ast = expr[2]
                index_type = evaluate_expr(index_expr_ast)

                if variable.array_index_type is not None and index_type != variable.array_index_type:
                    raise SemanticError(f"Índice de array deve ser {variable.array_index_type}, mas encontrado {index_type}")
                
                return var_type

        elif expr_type == 'func_call':
            # ('func_call', func_id, params)
            func_name = expr[1]
            func = current_context.find_function(func_name)
            if not func:
                raise SemanticError(f"Função '{func_name}' não declarada")
            if func.is_procedure:
                raise SemanticError(f"'{func_name}' é um procedimento, não uma função, não pode ser usado em uma expressão")
            
            current_context.use_function(func_name)
            func_params = expr[2] if len(expr) > 2 else []
            expected_params = list(func.args.items()) if func.args else []
            check_args(func_name, func_params, expected_params)
            return func.return_type
        else:
            raise SemanticError(f"Tipo de nó AST não suportado: {expr_type} na expressão {expr}")
    else:
        raise SemanticError(f"Estrutura de expressão não reconhecida: {expr}")


def check_args(func_name, func_params, expected_params):
    """
    Verifica os argumentos passados para uma função ou procedimento.
    Lança um erro se o número de argumentos ou os tipos não corresponderem."""
    mult_args = False
    if func_name.lower() in predefined_functions and 'arbitrary_args' in predefined_functions[func_name.lower()]:
        mult_args = True
        if len(func_params) < 1:
            raise SemanticError(f"Função '{func_name}' chamada com número insuficiente de argumentos: esperado pelo menos 1, encontrado 0")
    elif len(func_params) != len(expected_params):
        raise SemanticError(f"Função '{func_name}' chamada com número incorreto de argumentos: esperado {len(expected_params)}, encontrado {len(func_params)}")

    for i in range(len(func_params)):
        arg_type = evaluate_expr(func_params[i])
        
        if mult_args:
            expected_type = expected_params[0][1]  # Se for mult_args, só há um tipo esperado
        else:
            expected_type = expected_params[i][1]

        if isinstance(expected_type, list):
            if arg_type not in expected_type:
                raise SemanticError(f"Tipo do argumento {i+1} incompatível para função '{func_name}': esperado um dos {expected_type}, encontrado {arg_type}")
        elif arg_type != expected_type:
            raise SemanticError(f"Tipo do argumento {i+1} incompatível para função '{func_name}': esperado {expected_type}, encontrado {arg_type}")

        if isinstance(func_params[i], tuple) and func_params[i][0] == 'var':
            # Se for uma variável, marcar uso
            var_name = func_params[i][1]
            current_context.use_var(var_name)

def check_unused_vars_functions():
    """Verifica as variáveis e funções não usadas nos contextos
    Retorna duas listas: uma com os nomes das variáveis não usadas e outra com os nomes das funções não usadas.
    """
    global contexts
    unused_vars = []
    unused_funcs = []
    for context in contexts:
        for var in context.variables.values():
            if var.n_uses < 1:
                unused_vars.append(var.name)
        for func in context.functions.values():
            if func.n_uses < 1:
                unused_funcs.append(func.name)
    return unused_vars, unused_funcs