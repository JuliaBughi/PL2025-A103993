import sys
import os

src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src')
sys.path.insert(0, os.path.abspath(src_path))

from parser import parse, print_ast
from tests_db import tests
from semantic import semantic_analyse, SemanticError
from codegen import CodeGenerator

def main():
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        idx = int(sys.argv[1])
        if 0 <= idx < len(tests):
            print(f"Running test {idx}:")
            print("-" * 40)
            print(f"Code:\n{tests[idx]}")
            print("-" * 40)
            code = tests[idx]
            ast = parse(code)

            if '-s' in sys.argv:
                try :
                    unused_vars, unused_functions = semantic_analyse(ast)
                    print("Semantic analysis passed.")
                    if unused_vars:
                        print("Unused variables:", unused_vars)
                    if unused_functions:
                        print("Unused functions:", unused_functions)
                except SemanticError as e:
                    print(f"Semantic error: {e}")
            elif '-g' in sys.argv:
                try :
                    unused_vars, unused_functions = semantic_analyse(ast)
                    print("Semantic analysis passed.")
                    if unused_vars:
                        print("Unused variables:", unused_vars)
                    if unused_functions:
                        print("Unused functions:", unused_functions)
                    generator = CodeGenerator(unused_vars, unused_functions)
                    code = generator.generate_code(ast)
                    print(code)
                except SemanticError as e:
                    print(f"Semantic error: {e}")
            else:
                print_ast(ast)
                print(ast)
        else:
            print(f"Test index {idx} out of range.")
    else:
        for i, test in enumerate(tests):
            unused_functions = []
            unused_vars = []
            print(f"Test {i}:")
            code = test
            ast = parse(code)
            
            if '-s' in sys.argv:
                try :
                    unused_vars, unused_functions = semantic_analyse(ast)
                    print("Semantic analysis passed.")
                    if unused_vars:
                        print("Unused variables:", unused_vars)
                    if unused_functions:
                        print("Unused functions:", unused_functions)
                except SemanticError as e:
                    print(f"Semantic error: {e}")
            
            elif '-g' in sys.argv:
                try :
                    print_ast('g')
                    unused_vars, unused_functions = semantic_analyse(ast)
                    print("Semantic analysis passed.")
                    if unused_vars:
                        print("Unused variables:", unused_vars)
                    if unused_functions:
                        print("Unused functions:", unused_functions)
                    generator = CodeGenerator(unused_vars, unused_functions)
                    code = (ast)
                    print(code)
                except SemanticError as e:
                    print(f"Semantic error: {e}")

            
            print("-" * 40)

main()