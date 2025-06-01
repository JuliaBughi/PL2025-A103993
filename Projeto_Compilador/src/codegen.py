# EWVM Code Generator Skeleton

class SymbolTable:
    def __init__(self):
        self.scopes = [{}]  # Stack of scopes, global scope is the first
        self.fp_offsets = {} # {scope_id: current_fp_offset_for_locals}
        self.gp_offset = 0   # For global variables
        self.current_scope_id_counter = 0
        self.current_scope_id = 0 # Root scope (global)
        self.scopes[0]['__scope_id__'] = 0 # Mark global scope
        self.fp_offsets[self.current_scope_id] = 0

    def enter_scope(self):
        self.current_scope_id_counter += 1
        new_scope_id = self.current_scope_id_counter
        new_scope_dict = {'__scope_id__': new_scope_id, '__parent_scope_id__': self.current_scope_id}
        self.scopes.append(new_scope_dict)
        self.current_scope_id = new_scope_id
        self.fp_offsets[new_scope_id] = 0

    def exit_scope(self):
        if len(self.scopes) > 1: # Cannot exit global scope
            exiting_scope_info = self.scopes.pop()
            self.current_scope_id = exiting_scope_info.get('__parent_scope_id__', 0)
        else:
            print("Warning: Attempted to exit global scope.")


    def add_symbol(self, name, sym_type, kind, **kwargs):
        scope = self.scopes[-1]
        if name in scope and name not in ['__scope_id__', '__parent_scope_id__']:
            if not (kind == 'var' and kwargs.get('is_return_val_holder', False) and name == kwargs.get('func_name_for_return')):
                 raise Exception(f"Symbol '{name}' already declared in current scope {self.current_scope_id}.")

        symbol_entry = {'type': sym_type, 'kind': kind, 'scope_id': self.current_scope_id, **kwargs}
        scope[name] = symbol_entry
        
        if kind == 'var':
            if not kwargs.get('is_return_val_holder', False):
                if self.current_scope_id == 0: 
                    scope[name]['offset'] = self.gp_offset
                    self.gp_offset += 1 
                else: 
                    current_fp_offset = self.fp_offsets.get(self.current_scope_id, 0)
                    current_fp_offset -= 1 
                    scope[name]['offset'] = current_fp_offset
                    self.fp_offsets[self.current_scope_id] = current_fp_offset
        elif kind == 'param':
            pass


    def lookup_symbol(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def get_current_fp_offset(self): 
        return self.fp_offsets.get(self.current_scope_id, 0)

    def get_num_globals_allocated(self):
        return self.gp_offset


PREDEFINED_FUNCTIONS_INFO = {
    'write': {
        'is_procedure': True, 'args_meta': {'value': ['integer', 'real', 'string', 'char', 'boolean']},
        'arbitrary_args': True, 'return_type': 'void', 'ewvm_op': None
    },
    'writeln': {
        'is_procedure': True, 'args_meta': {'value': ['integer', 'real', 'string', 'char', 'boolean']},
        'arbitrary_args': True, 'return_type': 'void', 'ewvm_op': None
    },
    'read': {
        'is_procedure': True, 'args_meta': {'variable': ['integer', 'real', 'string', 'char']},
        'arbitrary_args': True, 'return_type': 'void', 'ewvm_op': "READ"
    },
    'readln': {
        'is_procedure': True, 'args_meta': {'variable': ['integer', 'real', 'string', 'char']},
        'arbitrary_args': True, 'return_type': 'void', 'ewvm_op': "READ" # plus line consumption logic
    },
    'length': {
        'is_procedure': False, 'args_meta': {'string': ['string']}, 'num_args': 1,
        'return_type': 'integer', 'ewvm_op': "STRLEN"
    },
    'ord': {
        'is_procedure': False, 'args_meta': {'char': ['char', 'string']}, 'num_args': 1, # char often passed as string
        'return_type': 'integer', 'ewvm_op': "CHRCODE" # Assumes char is 1-char string
    },
    'chr': {
        'is_procedure': False, 'args_meta': {'integer': ['integer']}, 'num_args': 1,
        'return_type': 'char', 'ewvm_op': None # No direct EWVM to create char string, usually for WRITECHR
    },
    'sin': {
        'is_procedure': False, 'args_meta': {'angle': ['real', 'integer']}, 'num_args': 1,
        'return_type': 'real', 'ewvm_op': "FSIN" # Needs ITOF if arg is int
    },
    'cos': {
        'is_procedure': False, 'args_meta': {'angle': ['real', 'integer']}, 'num_args': 1,
        'return_type': 'real', 'ewvm_op': "FCOS" # Needs ITOF if arg is int
    },
    'abs': {
        'is_procedure': False, 'args_meta': {'number': ['integer', 'real']}, 'num_args': 1,
        'return_type': 'input_dependent', 'ewvm_op': None # Custom logic
    },
    'trunc': {
        'is_procedure': False, 'args_meta': {'number': ['integer', 'real']}, 'num_args': 1,
        'return_type': 'integer', 'ewvm_op': "FTOI" # If input is int, effectively NOP
    },
    'round': {
        'is_procedure': False, 'args_meta': {'number': ['real']}, 'num_args': 1,
        'return_type': 'integer', 'ewvm_op': None # Custom logic
    }
}

class CodeGenerator:
    def __init__(self, unused_vars=None, unused_funcs=None):
        self.instructions = []
        self.label_count = 0
        self.symbol_table = SymbolTable()
        self.proc_func_code = [] 
        self.current_code_buffer = self.instructions 
        self.unused_vars = unused_vars or set()
        self.unused_funcs = unused_funcs or set()
        self.current_function_name = None
        self.predefined_functions_info = PREDEFINED_FUNCTIONS_INFO


    def new_label(self, prefix="L"):
        self.label_count += 1
        return f"{prefix}{self.label_count - 1}"

    def emit(self, instruction, *args):
        self.current_code_buffer.append(f"{instruction} {' '.join(map(str, args))}".strip())

    def emit_label(self, label):
        self.current_code_buffer.append(f"{label}:")

    def generate_code(self, node):
        self.visit(node)
        final_code = self.instructions 
        if self.proc_func_code: 
            final_code.extend(self.proc_func_code)
        return "\n".join(final_code)

    def visit(self, node, context=None):
        if node is None:
            return
        
        if isinstance(node, list) and not node:
            return

        if isinstance(node, (int, float)):
            self.visit_Const(node, context) 
            return
        if isinstance(node, str):
            if node == 'TRUE' or node == 'FALSE': 
                self.visit_Const(node, context)
                return
            
            if node.isidentifier(): 
                var_info = self.symbol_table.lookup_symbol(node)
                if not var_info:
                    # Could be a predefined function name used without lookup (handled in visit_func_call)
                    # For now, if it reaches here as a bare identifier string, it must be a var/const
                    raise Exception(f"Undefined identifier: {node}")
                
                if var_info['kind'] == 'const':
                    self.visit_Const(var_info['value'], context) 
                elif var_info['kind'] in ['var', 'param']:
                    self.emit_load_variable(node) 
                else:
                    raise Exception(f"Identifier '{node}' of kind '{var_info['kind']}' used directly as a value is unhandled here.")
                return
            else:
                self.visit_Const(node, context)
                return

        if not isinstance(node, tuple) or not node: 
            raise Exception(f"Invalid AST node structure encountered: {node}. Expected non-empty tuple.")

        method_name = f'visit_{node[0]}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node, context)

    def generic_visit(self, node, context=None):
        print(f"Warning: No specific visitor method for AST node type '{node[0]}'. Traversing children.")
        for child_node in node[1:]:
            if isinstance(child_node, (list, tuple, str, int, float)): 
                self.visit(child_node, context)


    def emit_load_variable(self, var_name):
        var_info = self.symbol_table.lookup_symbol(var_name)
        if not var_info:
            raise Exception(f"Undeclared variable {var_name}")
        offset = var_info['offset']
        if var_info['scope_id'] == 0: 
            self.emit("PUSHG", offset)
        else: 
            self.emit("PUSHL", offset)


    def emit_store_variable(self, var_name):
        var_info = self.symbol_table.lookup_symbol(var_name)
        if not var_info:
            raise Exception(f"Undeclared variable {var_name}")
        offset = var_info['offset']
        if var_info['scope_id'] == 0: 
            self.emit("STOREG", offset)
        else: 
            self.emit("STOREL", offset)

    def _get_expression_type(self, expr_node, context):
        # Placeholder for a real type-checking mechanism.
        # This is crucial for selecting correct EWVM opcodes (e.g., ADD vs FADD, WRITEI vs WRITEF)
        # and for type coercion (e.g., ITOF).
        if isinstance(expr_node, int): return 'integer'
        if isinstance(expr_node, float): return 'real'
        if isinstance(expr_node, str):
            if expr_node == 'TRUE' or expr_node == 'FALSE': return 'boolean'
            if expr_node.isidentifier():
                sym = self.symbol_table.lookup_symbol(expr_node)
                return sym['type'] if sym else 'unknown'
            return 'string' # Assumed string literal content
        if isinstance(expr_node, tuple):
            # For complex expressions, recursively determine type
            # Example: ('expr', left, op, right) -> type of op(left, right)
            # Example: ('func_call', name, params) -> return_type of function 'name'
            if expr_node[0] == 'func_call':
                func_name = expr_node[1].lower()
                if func_name in self.predefined_functions_info:
                    return self.predefined_functions_info[func_name]['return_type']
                user_func = self.symbol_table.lookup_symbol(expr_node[1])
                if user_func and user_func['kind'] == 'func':
                    return user_func['return_type']
            # Add more rules for other expression types
            return 'integer' # Default/placeholder for complex expressions
        return 'unknown'

    # --- Program Structure ---
    def visit_program(self, node, context=None): 
        _program_keyword, prog_name, content_node = node
        
        # Ensure proper AST structure for 'content'
        if content_node[0] == 'content':
            declarations_and_procedures_node = content_node[1] 
            self.visit_DeclarationsAndProcedures(declarations_and_procedures_node, {'scope': 'global_prepass'})
            # This is a pre-pass to register global variables and function/procedure labels first.
            # The actual code generation for functions/procedures happens in the main_content pass.
            # This separation helps in resolving forward references.

        num_globals = self.symbol_table.get_num_globals_allocated()
        if num_globals > 0:
            self.emit("PUSHN", num_globals) # Allocate space for global variables
        self.emit("START") # Entry point for the main program
        self.visit(content_node, context) # Visit the main content block
        self.emit("STOP")

    def visit_content(self, node, context=None): 
        _content_keyword, declarations_and_procedures_node, begin_block_node = node
        # This is the second pass for declarations and procedures, for actual code generation
        self.visit_DeclarationsAndProcedures(declarations_and_procedures_node, {'scope': 'main_content'})
        self.visit(begin_block_node, context) # Visit the main program's executable block

    def visit_DeclarationsAndProcedures(self, node, context=None): 
        if not node: 
            return
        current_scope_type = context.get('scope', 'unknown') if context else 'unknown'
        for decl_or_proc_node in node: 
            # The 'DeclarationOrProcedure' tuple is just a wrapper, unwrap it.
            # This is specific to how the parser outputs the AST for this rule.
            actual_node = decl_or_proc_node[0] if isinstance(decl_or_proc_node, tuple) and decl_or_proc_node[0] == 'DeclarationOrProcedure' else decl_or_proc_node

            node_type = actual_node[0]

            if node_type in ['const_list', 'var_list']:
                # Global declarations are processed in the 'global_prepass'
                if current_scope_type == 'global_prepass' and self.symbol_table.current_scope_id == 0:
                    self.visit(actual_node, context)
                # Local declarations are processed when visiting procedures/functions
                elif current_scope_type == 'local' and self.symbol_table.current_scope_id != 0:
                    self.visit(actual_node, context)
            elif node_type in ['procedure', 'function']:
                # Procedures and functions are generated in a separate buffer during 'main_content' pass
                if current_scope_type == 'main_content': 
                    original_buffer = self.current_code_buffer
                    self.current_code_buffer = self.proc_func_code # Switch to procedure/function code buffer
                    self.visit(actual_node, context)
                    self.current_code_buffer = original_buffer # Restore main code buffer
            else:
                 # Generic visit for any other nodes that might appear here
                 # (Though, based on grammar, it should only be the above types or wrapper)
                 self.visit(actual_node, context) 

    def visit_DeclarationOrProcedure(self, node, context=None): 
        # This method might not be explicitly called due to unwrapping in visit_DeclarationsAndProcedures
        self.visit(node[0], context)

    # --- Declarations ---
    def visit_const_list(self, node, context=None): 
        _const_list_keyword, const_declarations = node
        for const_decl in const_declarations: 
            self.visit_ConstDeclaration(const_decl, context)

    def visit_ConstDeclaration(self, node, context=None): 
        var_id, value_node = node 
        actual_value = None
        sym_type = 'unknown'
        if isinstance(value_node, int):
            sym_type = 'integer'; actual_value = value_node
        elif isinstance(value_node, float):
            sym_type = 'real'; actual_value = value_node
        elif value_node is True: # PLY's t_TRUE converts to Python True
            sym_type = 'boolean'; actual_value = 1
        elif value_node is False: # PLY's t_FALSE converts to Python False
            sym_type = 'boolean'; actual_value = 0
        elif isinstance(value_node, str): 
            # Check if it's an ID referring to another constant
            if self.symbol_table.lookup_symbol(value_node) and self.symbol_table.lookup_symbol(value_node)['kind'] == 'const':
                const_ref = self.symbol_table.lookup_symbol(value_node)
                sym_type = const_ref['type']
                actual_value = const_ref['value']
            else:
                sym_type = 'string'; actual_value = value_node 
        else: 
             raise Exception(f"Unhandled literal type in ConstDeclaration: {value_node}")
        self.symbol_table.add_symbol(var_id, sym_type, 'const', value=actual_value)

    def visit_var_list(self, node, context=None): 
        _var_list_keyword, var_declarations = node
        for var_decl in var_declarations: 
            self.visit_VarDeclaration(var_decl, context)

    def visit_VarDeclaration(self, node, context=None): 
        _var_keyword, ids_list, var_type_node = node
        pascal_type_info = self.visit_VarType(var_type_node, context)
        for var_id in ids_list:
            if var_id in self.unused_vars:
                print(f"Info: Variable '{var_id}' is unused. Not adding to symbol table / allocating.")
                continue
            self.symbol_table.add_symbol(var_id, pascal_type_info, 'var')
            if isinstance(pascal_type_info, dict) and pascal_type_info.get('base_type') == 'array':
                size = (pascal_type_info['range'][1] - pascal_type_info['range'][0] + 1)
                if self.symbol_table.current_scope_id == 0: 
                    self.symbol_table.gp_offset += (size -1) # gp_offset already incremented by 1 for the first element
                else: 
                    self.symbol_table.fp_offsets[self.symbol_table.current_scope_id] -= (size -1) # fp_offset already decremented by 1 for the first element

    def visit_VarType(self, node, context=None): 
        if isinstance(node, str): 
            # PLY tokens like INTEGER_TYPE might be directly returned as 'integer'
            return node.lower() # ensure it's lowercase for consistency
        elif isinstance(node, tuple) and node[0] == 'array':
            _array_keyword, range_node, element_type_node = node[0], node[1], node[2] # Corrected unpacking based on parser `('array', p[3], p[6])`
            array_range_tuple = self.visit_Range(range_node, context)
            element_type_str = self.visit_Type(element_type_node, context) 
            return {'base_type': 'array', 'range': array_range_tuple, 'element_type': element_type_str}
        raise Exception(f"Unknown VarType structure: {node}")

    def visit_Range(self, node, context=None): 
        _range_keyword, lower_bound_node, upper_bound_node = node # Corrected unpacking based on parser `('range', p[1], p[3])`
        lower_bound = self.resolve_value_to_int(lower_bound_node)
        upper_bound = self.resolve_value_to_int(upper_bound_node)
        return (lower_bound, upper_bound)

    def resolve_value_to_int(self, value_node):
        if isinstance(value_node, int): return value_node
        if isinstance(value_node, str): 
            sym = self.symbol_table.lookup_symbol(value_node)
            if sym and sym['kind'] == 'const' and isinstance(sym['value'], int):
                return sym['value']
        raise Exception(f"Cannot resolve range bound '{value_node}' to an integer constant.")

    def visit_Type(self, node, context=None): 
        if isinstance(node, str): return node.lower() # ensure it's lowercase
        raise Exception(f"Unknown Type structure: {node}")

    # --- Statements ---
    def visit_begin_block(self, node, context=None): 
        _begin_keyword, statements_node_list = node
        if statements_node_list: 
            self.visit_Statements(statements_node_list, context)

    def visit_Statements(self, node_list, context=None): 
        # The parser rule p_statements can produce a list where some elements are None
        # due to the '|' in `Statement : MatchedStatement | UnmatchedStatement |`
        # Filter out None statements.
        for stmt_node_tuple in node_list:
            if stmt_node_tuple is not None:
                self.visit(stmt_node_tuple, context)

    def visit_assignment(self, node, context=None): 
        _assignment_keyword, lhs_node, rhs_expr_node = node
        # lhs_node can be a simple ID string or a ('var', ID, index_expr) tuple for array access
        if isinstance(lhs_node, str): 
            var_id = lhs_node
            self.visit(rhs_expr_node, context) 
            self.emit_store_variable(var_id)
        elif isinstance(lhs_node, tuple) and lhs_node[0] == 'var' and len(lhs_node) == 3:
            # Array assignment: ('var', array_id, index_expr_node)
            array_id = lhs_node[1]; index_expr_node = lhs_node[2]
            array_info = self.symbol_table.lookup_symbol(array_id)
            if not array_info or not (isinstance(array_info.get('type'), dict) and array_info['type'].get('base_type') == 'array'):
                raise Exception(f"'{array_id}' is not a declared array or type info is missing for array assignment.")
            
            # Calculate address of the element
            if array_info['scope_id'] == 0: 
                self.emit("PUSHGP"); self.emit("PUSHI", array_info['offset']); self.emit("PADD") # Address of array base + offset
            else: 
                self.emit("PUSHFP"); self.emit("PUSHI", array_info['offset']); self.emit("PADD") # Address of array base + offset

            self.visit(index_expr_node, context) # Index value on stack
            
            lower_bound = array_info['type']['range'][0]
            if lower_bound != 0:
                self.emit("PUSHI", lower_bound); self.emit("SUB") # Adjust index for 0-based
            
            self.emit("PADD") # Add adjusted index to base address -> address of element
            
            self.visit(rhs_expr_node, context) # Value to store on stack
            self.emit("STORE", 0) # Store value at address (EWVM STORE consumes value and address)
        else:
            raise Exception(f"Invalid LHS for assignment: {lhs_node}")

    def visit_if(self, node, context=None): 
        # ('if', expr_bool, then_stmt) or ('if', expr_bool, then_stmt, else_stmt)
        _if_keyword, expr_bool_node, then_stmt_node = node[0:3]
        else_stmt_node = node[3] if len(node) > 3 else None 
        
        self.visit(expr_bool_node, context) # Evaluate condition, result (0 or 1) on stack
        
        if else_stmt_node:
            else_label = self.new_label("ELSE"); endif_label = self.new_label("ENDIF")
            self.emit("JZ", else_label) # Jump to ELSE if condition is false (0)
            self.visit(then_stmt_node, context)
            self.emit("JUMP", endif_label) # Jump over ELSE block after THEN
            self.emit_label(else_label)
            self.visit(else_stmt_node, context)
            self.emit_label(endif_label)
        else:
            endif_label = self.new_label("ENDIF")
            self.emit("JZ", endif_label) # Jump to ENDIF if condition is false (0)
            self.visit(then_stmt_node, context)
            self.emit_label(endif_label)

    def visit_while(self, node, context=None): 
        _while_keyword, expr_bool_node, stmt_node = node
        loop_start_label = self.new_label("LOOP_START"); loop_end_label = self.new_label("LOOP_END")
        
        self.emit_label(loop_start_label)
        self.visit(expr_bool_node, context) # Evaluate condition
        self.emit("JZ", loop_end_label) # Exit loop if condition is false
        self.visit(stmt_node, context) # Execute loop body
        self.emit("JUMP", loop_start_label) # Jump back to re-evaluate condition
        self.emit_label(loop_end_label)

    def visit_repeat(self, node, context=None): 
        _repeat_keyword, stmts_node_list, expr_bool_node = node
        loop_start_label = self.new_label("REPEAT_START")
        
        self.emit_label(loop_start_label)
        self.visit_Statements(stmts_node_list, context) # Execute body
        self.visit(expr_bool_node, context) # Evaluate condition
        self.emit("JZ", loop_start_label) # Repeat if condition is false (0)

    def visit_for(self, node, context=None):
        _for_keyword, assignment_node, direction_token, end_expr_node, stmt_node = node
        
        iter_var_id = assignment_node[1]
        start_expr_node = assignment_node[2]
        
        # 1. Initialize loop variable
        self.visit(start_expr_node, context)
        self.emit_store_variable(iter_var_id)
        
        loop_condition_label = self.new_label("FOR_COND")
        loop_body_label = self.new_label("FOR_BODY")
        loop_end_label = self.new_label("FOR_END")
        
        self.emit("JUMP", loop_condition_label) # Jump to condition check first
        
        self.emit_label(loop_body_label)
        self.visit(stmt_node, context) # Execute loop body
        
        # 2. Increment/Decrement loop variable
        self.emit_load_variable(iter_var_id)
        self.emit("PUSHI", 1)
        if direction_token.lower() == 'to': # 'to' is from parser rule, it's lowercased
            self.emit("ADD")
        elif direction_token.lower() == 'downto': # 'downto' is from parser rule, it's lowercased
            self.emit("SUB")
        else: 
            raise Exception(f"Unknown FOR loop direction: {direction_token}")
        self.emit_store_variable(iter_var_id)
        
        # 3. Check loop condition
        self.emit_label(loop_condition_label)
        self.emit_load_variable(iter_var_id)
        self.visit(end_expr_node, context) # Evaluate end value
        
        if direction_token.lower() == 'to':
            self.emit("INFEQ") # i <= end
        else: # downto
            self.emit("SUPEQ") # i >= end
            
        self.emit("JZ", loop_end_label) # If condition is false, exit loop
        self.emit("JUMP", loop_body_label) # Otherwise, jump back to loop body
        
        self.emit_label(loop_end_label)

    # --- Expressions & Values ---
    def visit_Const(self, node_value, context=None): 
        if isinstance(node_value, int): self.emit("PUSHI", node_value)
        elif isinstance(node_value, float): self.emit("PUSHF", node_value)
        elif isinstance(node_value, str):
            if node_value == 'TRUE': self.emit("PUSHI", 1) # PLY returns True/False for boolean tokens
            elif node_value == 'FALSE': self.emit("PUSHI", 0)
            else: self.emit("PUSHS", f'"{node_value}"') # String literal
        elif isinstance(node_value, bool): # Handle direct boolean values (True/False from PLY)
            self.emit("PUSHI", 1 if node_value else 0)
        else:
             raise Exception(f"Unknown constant value type in visit_Const: {node_value} (type {type(node_value)})")

    def visit_var(self, node, context=None): 
        # ('var', var_id_str) for simple variable
        # ('var', array_id, index_expr) for array element access
        _var_keyword, var_id_str = node[0:2]
        
        if len(node) == 3: # Array access
            index_expr_node = node[2]
            array_info = self.symbol_table.lookup_symbol(var_id_str)
            if not array_info or not (array_info['type'] in ['array', 'string']):
                 raise Exception(f"'{var_id_str}' is not a declared array or type info missing for indexing.")
            
            # Push base address of the array
            if array_info['scope_id'] == 0: 
                self.emit("PUSHGP"); self.emit("PUSHI", array_info['offset']); self.emit("PADD")
            else: 
                self.emit("PUSHFP"); self.emit("PUSHI", array_info['offset']); self.emit("PADD")
            
            self.visit(index_expr_node, context) # Evaluate index, push onto stack
            
            lower_bound = array_info['type']['range'][0]
            if lower_bound != 0:
                self.emit("PUSHI", lower_bound); self.emit("SUB") # Adjust index for 0-based
            
            self.emit("PADD") # Add adjusted index to base address to get element's address
            self.emit("LOAD", 0) # Load value at calculated address
        else: # Simple variable
            self.emit_load_variable(var_id_str)

    def visit_expr_bool(self, node, context=None):
        node_type = node[0]
        if node_type == 'not':
            self.visit(node[1], context); self.emit("NOT") 
        elif node_type == 'expr_bool': 
            _keyword, left_expr_node, op_rel_str, right_expr_node = node
            self.visit(left_expr_node, context); self.visit(right_expr_node, context)
            
            # op_rel_str comes directly from the token value (e.g., '=', '<>', '<')
            op_map = {'=': "EQUAL", '<': "INF", '>': "SUP", '<=': "INFEQ", '>=': "SUPEQ"}
            if op_rel_str == '<>': # NEQ
                self.emit("EQUAL"); self.emit("NOT")
            elif op_rel_str in op_map: 
                self.emit(op_map[op_rel_str])
            else: 
                raise Exception(f"Unknown relational operator: {op_rel_str}")
        else: 
            # If ExprBool directly holds an Expr, visit it.
            self.visit(node, context)

    def visit_expr(self, node, context=None): 
        if node[0] == 'expr':
            _keyword, left_expr_node, op_add_str, right_termo_node = node
            self.visit(left_expr_node, context); self.visit(right_termo_node, context)
            
            # op_add_str comes directly from the token value (e.g., '+', '-')
            # Corrected keys to match the literal operator symbols from the parser
            op_map = {'+': "ADD", '-': "SUB", 'or': "OR"} 
            if op_add_str in op_map: 
                self.emit(op_map[op_add_str])
            else: 
                raise Exception(f"Unknown additive operator: {op_add_str}")
        else: 
            # If Expr directly holds a Termo, visit it.
            self.visit(node, context)

    def visit_Termo(self, node, context=None): 
        if node[0] == 'termo':
            _keyword, left_termo_node, op_mul_str, right_fator_node = node
            self.visit(left_termo_node, context); self.visit(right_fator_node, context)
            
            # op_mul_str comes directly from the token value (e.g., '*', '/')
            # Corrected keys to match the literal operator symbols from the parser
            op_map = {
                '*': "MUL", '/': "FDIV", 
                'and': "AND", 'mod': "MOD", 'div': "DIV" 
            }
            if op_mul_str in op_map: 
                self.emit(op_map[op_mul_str])
            else: 
                raise Exception(f"Unknown multiplicative operator: {op_mul_str}")
        else: 
            # If Termo directly holds a Fator, visit it.
            self.visit(node, context)
    visit_termo = visit_Termo # Alias for consistency if called with 'termo'

    def visit_Fator(self, node, context=None):
        if isinstance(node, (int, float, str, bool)): # Direct constant values
             self.visit_Const(node, context) 
        elif isinstance(node, tuple):
            if node[0] in ['var', 'func_call']: # If it's a specific AST node type
                self.visit(node, context)
            else: 
                # This handles cases like `('expr_bool', ...)` or `('expr', ...)` directly from the parenthesized expression.
                # The assumption is that `p_fator` already unwrapped the parentheses and passed the inner expression.
                self.visit(node, context) 
        else:
            raise Exception(f"Unknown Fator structure: {node}")

    def visit_var_or_func_call(self, node, context=None):
        # The parser rule p_var_or_func_call creates ('var', ID), ('var', ID, index), or ('func_call', ID, params)
        node_type = node[0]
        if node_type == 'var': 
            self.visit_var(node, context)
        elif node_type == 'func_call': 
            self.visit_func_call(node, context)
        else: 
            if isinstance(node, str): 
                sym_info = self.symbol_table.lookup_symbol(node)
                if sym_info and sym_info['kind'] == 'const': self.visit_Const(sym_info['value'], context)
                elif sym_info and sym_info['kind'] in ['var', 'param']: self.emit_load_variable(node)
                else: raise Exception(f"Unhandled simple ID in VarOrFuncCall context: {node}")
            else: raise Exception(f"Unknown VarOrFuncCall structure: {node}")

    def _handle_predefined_call(self, func_name_lower, predefined_info, params_list_node, context):
        num_expected_args = predefined_info.get('num_args')
        actual_num_args = len(params_list_node) if params_list_node else 0

        if num_expected_args is not None and actual_num_args != num_expected_args and not predefined_info.get('arbitrary_args'):
            raise Exception(f"Predefined function '{func_name_lower}' expects {num_expected_args} arguments, got {actual_num_args}.")

        # Process arguments first for functions that take their values on stack
        arg_types = [] # Store inferred types of evaluated arguments
        if params_list_node:
            for i, param_expr_node in enumerate(params_list_node):
                # For read/readln, params are variables, not expressions to evaluate for value.
                # These are handled specially below, so we only visit value-based params here.
                if func_name_lower not in ['read', 'readln']:
                    self.visit(param_expr_node, context) # Evaluates arg, leaves on stack
                    arg_types.append(self._get_expression_type(param_expr_node, context))

        # Emit EWVM op or custom logic
        # Write/Writeln are handled by `visit_func_call_write_or_writeln` separately
        if func_name_lower == 'read' or func_name_lower == 'readln':
            if params_list_node:
                for param_var_id_node in params_list_node: # These are var IDs from parser's Params rule
                    # param_var_id_node from `p_params` is directly `ExprBool`.
                    # For `read`, the parameter must be a variable *identifier*.
                    if not (isinstance(param_var_id_node, tuple) and param_var_id_node[0] == 'var' and len(param_var_id_node) == 2 and isinstance(param_var_id_node[1], str)):
                        raise Exception(f"'{func_name_lower}' expects variable identifiers as parameters. Got: {param_var_id_node}")
                    
                    var_name = param_var_id_node[1] # Extract the variable name
                    var_info = self.symbol_table.lookup_symbol(var_name)
                    if not var_info or var_info['kind'] != 'var':
                        raise Exception(f"{func_name_lower} parameter '{var_name}' is not a declared variable.")
                    
                    self.emit("READ") # Reads a string from input
                    var_type = var_info['type']
                    if var_type == 'integer': self.emit("ATOI") # Convert string to integer
                    elif var_type == 'real': self.emit("ATOF")   # Convert string to float
                    elif var_type == 'string': pass             # String read directly
                    elif var_type == 'boolean': self.emit("ATOI") # Convert string to int (0/1) for boolean
                    elif var_type == 'char': 
                        # EWVM READ reads a string. For char, it means reading a 1-char string.
                        # If more than 1 char read, standard Pascal truncates. EWVM keeps string.
                        # For simplicity, we'll store the string. If type check needed, string len.
                        print(f"Warning: read/readln for char type '{var_name}' with EWVM READ. Storing as string representation.")
                    else: 
                        raise Exception(f"Cannot {func_name_lower} into variable of type '{var_type}' for '{var_name}'")
                    self.emit_store_variable(var_name) # Store the converted/read value into the variable
            if func_name_lower == 'readln':
                if not params_list_node: # If readln is called without parameters, it just consumes the line
                    self.emit("READ") # Dummy read to consume the line
                    self.emit("POP", 1) # Discard the read string address

        elif func_name_lower == 'length': 
            self.emit("STRLEN") # Expects string address on stack
        elif func_name_lower == 'ord':    
            self.emit("CHRCODE") # Expects string address (1-char string) on stack
        elif func_name_lower == 'chr':    
            # Pascal 'chr' converts integer to character. EWVM doesn't have a direct 'CHR' op.
            # The integer value is already on the stack. If it's used in WRITECHR, it's fine.
            # If used as a string in an expression, it's more complex (e.g., create 1-char string).
            print(f"Warning: Predefined function 'chr' result is its integer argument unless used with WRITECHR. No direct EWVM op for string creation.")
            # (no EWVM op emitted here, int value remains on stack)

        elif func_name_lower == 'sin' or func_name_lower == 'cos': 
            arg_type = arg_types[0] if arg_types else 'unknown'
            if arg_type == 'integer':
                self.emit("ITOF") # Convert integer to float for float trig functions
            self.emit(predefined_info['ewvm_op']) # FSIN or FCOS

        elif func_name_lower == 'trunc': 
            arg_type = arg_types[0] if arg_types else 'unknown'
            if arg_type == 'real':
                self.emit("FTOI") # Convert float to integer (truncates fractional part)
            # If integer, FTOI is not applicable, value is already int. No-op.
        
        elif func_name_lower == 'abs': 
            arg_type = arg_types[0] if arg_types else 'unknown'
            positive_label = self.new_label("ABS_POS")
            self.emit("DUP", 1) # Duplicate the number to check its sign
            if arg_type == 'real':
                self.emit("PUSHF", 0.0)
                self.emit("FINF") # Check if num < 0.0 (result is 1 if true, 0 if false)
            else: # integer
                self.emit("PUSHI", 0)
                self.emit("INF")  # Check if num < 0 (result is 1 if true, 0 if false)
            self.emit("JZ", positive_label) # If not less than 0 (i.e., >= 0), jump to positive
            # If it's negative, negate it
            if arg_type == 'real':
                self.emit("PUSHF", -1.0); self.emit("FMUL")
            else:
                self.emit("PUSHI", -1); self.emit("MUL")
            self.emit_label(positive_label)

        elif func_name_lower == 'round': 
            # Pascal round: round half away from zero.
            # x := round(y) => if y >= 0 then x := trunc(y + 0.5) else x := trunc(y - 0.5)
            # Assumes argument is 'real' based on PREDEFINED_FUNCTIONS_INFO
            add_half_label = self.new_label("ROUND_ADD_HALF")
            sub_half_label = self.new_label("ROUND_SUB_HALF")
            truncate_label = self.new_label("ROUND_TRUNC")

            self.emit("DUP", 1)      # Duplicate the real number 'y' (stack: y, y)
            self.emit("PUSHF", 0.0)  # Push 0.0 (stack: y, y, 0.0)
            self.emit("FSUPEQ")      # y >= 0.0? (result 1 if true, 0 if false; stack: y, (y >= 0.0))
            self.emit("JZ", sub_half_label) # If y < 0 (result 0), jump to sub_half

            # Positive or zero case (y >= 0)
            self.emit_label(add_half_label)
            self.emit("PUSHF", 0.5)  # Push 0.5 (stack: y, 0.5)
            self.emit("FADD")        # y + 0.5 (stack: y+0.5)
            self.emit("JUMP", truncate_label) # Jump to truncation

            # Negative case (y < 0)
            self.emit_label(sub_half_label)
            self.emit("PUSHF", 0.5)  # Push 0.5 (stack: y, 0.5)
            self.emit("FSUB")        # y - 0.5 (stack: y-0.5)
            
            self.emit_label(truncate_label)
            self.emit("FTOI")       # Truncate the result to integer

        else:
            if predefined_info['ewvm_op']:
                self.emit(predefined_info['ewvm_op'])
            else:
                print(f"Warning: Predefined function '{func_name_lower}' has no direct EWVM op and custom logic not fully implemented here.")


    def visit_func_call(self, node, context=None): 
        # ('func_call', func_id_str) or ('func_call', func_id_str, params_list_node)
        _keyword, func_id_str = node[0:2]
        params_list_node = node[2] if len(node) > 2 else None 
        
        func_name_lower = func_id_str.lower()
        if func_name_lower in self.predefined_functions_info:
            predefined_info = self.predefined_functions_info[func_name_lower]
            # Special handling for write/writeln due to arbitrary args and per-arg processing
            if func_name_lower == 'write':
                return self.visit_func_call_write_or_writeln(func_id_str, params_list_node, context, is_writeln=False)
            if func_name_lower == 'writeln':
                return self.visit_func_call_write_or_writeln(func_id_str, params_list_node, context, is_writeln=True)
            
            return self._handle_predefined_call(func_name_lower, predefined_info, params_list_node, context)

        # User-defined function/procedure
        func_info = self.symbol_table.lookup_symbol(func_id_str)
        if not func_info or func_info['kind'] not in ['proc', 'func']:
            raise Exception(f"Call to undeclared procedure/function: {func_id_str}")
        if func_id_str in self.unused_funcs:
             print(f"Warning: Call to unused function '{func_id_str}'. Generating call anyway.")
        
        if params_list_node: 
            for param_expr_node in params_list_node:
                self.visit(param_expr_node, context) # Evaluate each parameter, pushing its value onto the stack
        
        self.emit("PUSHA", func_info['label']) # Push address of the function/procedure
        self.emit("CALL") # Call the function/procedure

    # --- Procedures and Functions Definitions ---
    def visit_procedure(self, node, context=None): 
        _proc_keyword, proc_name_str, args_list_node, content_node = node
        if proc_name_str in self.unused_funcs:
            print(f"Info: Procedure '{proc_name_str}' is unused. Not generating code."); return
        
        proc_label = f"PROC_{proc_name_str}"
        self.symbol_table.add_symbol(proc_name_str, 'proc_type', 'proc', label=proc_label) # Register procedure
        
        self.emit_label(proc_label)
        self.symbol_table.enter_scope() # New scope for procedure
        
        num_params = 0
        if args_list_node and args_list_node[0] == 'args_list': 
            args_tuples_list = args_list_node[1] 
            num_params = len(args_tuples_list)
            for i, arg_def_tuple in enumerate(args_tuples_list):
                arg_name_str = arg_def_tuple[1]; arg_type_str = self.visit_Type(arg_def_tuple[2], context)
                offset = (num_params - i) + 2 # If `add_symbol` adds `offset` to locals, they are negative. Params are positive.
                param_offset_ewvm = i + 2 # Arg (i) + 2 (for old FP + RA)
                self.symbol_table.add_symbol(arg_name_str, arg_type_str, 'param', offset=param_offset_ewvm)
        
        fp_offset_before_locals_visit = self.symbol_table.get_current_fp_offset() 
        self.visit_DeclarationsAndProcedures(local_declarations_list, {'scope': 'local'})
        fp_offset_after_locals_visit = self.symbol_table.get_current_fp_offset()
        
        num_local_slots_needed = abs(fp_offset_after_locals_visit - fp_offset_before_locals_visit)
        
        # Allocate space for locals. PUSHN allocates and moves SP.
        if num_local_slots_needed > 0: 
            self.emit("PUSHN", num_local_slots_needed)
        
        # Visit procedure body
        begin_block_node = content_node[2]
        self.visit(begin_block_node, context)
        
        self.emit("RETURN") # Return from procedure
        self.symbol_table.exit_scope()

    def visit_function(self, node, context=None):
        _func_kwd, func_name_str, args_list_node, ret_type_node, content_node = node # Corrected unpacking based on parser `('function', p[2], p[3], p[5], p[7])`
        if func_name_str in self.unused_funcs:
            print(f"Info: Function '{func_name_str}' is unused. Not generating code."); return
        
        self.current_function_name = func_name_str # Set for handling assignments to function name
        func_label = f"FUNC_{func_name_str}"
        return_type_str = self.visit_Type(ret_type_node, context)
        
        self.symbol_table.add_symbol(func_name_str, return_type_str, 'func', label=func_label, return_type=return_type_str)
        
        self.emit_label(func_label)
        self.symbol_table.enter_scope() # New scope for function
        
        fp_offset_for_return_val_holder = -1 # Assuming the first local variable slot (FP-1) is for return value
        self.symbol_table.add_symbol(
            func_name_str, return_type_str, 'var', # Treat function name as a variable for assignment
            offset=fp_offset_for_return_val_holder, is_return_val_holder=True, 
            func_name_for_return=func_name_str 
        )
        self.symbol_table.fp_offsets[self.symbol_table.current_scope_id] = fp_offset_for_return_val_holder
        
        num_params = 0
        if args_list_node and args_list_node[0] == 'args_list':
            args_tuples_list = args_list_node[1]
            num_params = len(args_tuples_list)
            for i, arg_def_tuple in enumerate(args_tuples_list):
                arg_name_str = arg_def_tuple[1]; arg_type_str = self.visit_Type(arg_def_tuple[2], context)
                param_offset_ewvm = i + 3 # EWVM parameter offset (after RA, FP_caller, and return value slot)
                self.symbol_table.add_symbol(arg_name_str, arg_type_str, 'param', offset=param_offset_ewvm)
        
        local_declarations_list = content_node[1]
        fp_offset_before_true_locals = self.symbol_table.get_current_fp_offset() 
        self.visit_DeclarationsAndProcedures(local_declarations_list, {'scope': 'local'})
        fp_offset_after_true_locals = self.symbol_table.get_current_fp_offset()
        
        num_true_local_slots = abs(fp_offset_after_true_locals - fp_offset_before_true_locals)
        
        total_slots_to_allocate = abs(self.symbol_table.get_current_fp_offset())
        
        if total_slots_to_allocate > 0: 
            self.emit("PUSHN", total_slots_to_allocate)
        
        # Visit function body
        begin_block_node = content_node[2]
        self.visit(begin_block_node, context)
        
        self.emit("PUSHL", fp_offset_for_return_val_holder) # Load the result from the return value holder
        
        self.emit("RETURN") # Return from function
        self.symbol_table.exit_scope()
        self.current_function_name = None

    # --- I/O and specific predefined function handlers ---
    def visit_func_call_write_or_writeln(self, func_id_str, params_list_node, context, is_writeln):
        if params_list_node: 
            for param_expr_node in params_list_node:
                # Evaluate the expression, result is on stack
                self.visit(param_expr_node, context)
                
                expr_type = self._get_expression_type(param_expr_node, context)

                if expr_type == 'integer': self.emit("WRITEI")
                elif expr_type == 'real': self.emit("WRITEF")
                elif expr_type == 'string': self.emit("WRITES")
                elif expr_type == 'char': self.emit("WRITECHR") # Assuming char is int code or a single-char string
                elif expr_type == 'boolean': self.emit("WRITEI") # Bools written as 0 or 1
                else:
                    print(f"Warning: Cannot determine specific WRITE instruction for type '{expr_type}' of param '{param_expr_node}'. Defaulting or erroring.")
                    # Fallback or error, e.g. self.emit("WRITEI") or raise Exception
        if is_writeln:
            self.emit("WRITELN")