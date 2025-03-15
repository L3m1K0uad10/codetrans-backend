import json
import ast
import pytest
from parsing.variable_parser import VariableExtractor, VariableDetails



#NOTE: the coordinate of the cursor(row, col) start from 1 thus (1, 1) is the first character in the code(top-left corner)

def test_variable_extractor():
    code = '''
def get_func_identifier(token_pos, func_token, instruction):
    """ 
    returns a function identifier's positions, start and end col
    """

    identifier_start_pos = token_pos + (len(func_token) - 1) + 2 

    # let's find the occurence position of ( 
    lbracket = instruction.find("(")

    identifier_end_pos  = lbracket - 1 

    varx = 10

    varx = varx + 1 + (varx * varx)

    return identifier_start_pos, identifier_end_pos 

class Person:
    def __init__(self, name):
        self.name = name
    def display(self):
        print(self.name)

p1 = Person("Lemi")
p1.display()
'''
    parsed_code = ast.parse(code)
    extractor = VariableExtractor()
    extractor.visit(parsed_code)
    extracted_identifiers = extractor.get_variables()
    
    extracted_variables = {'token_pos', 'identifier_start_pos', 'p1', 'name', 'lbracket', 'instruction', 'identifier_end_pos', 'varx', 'func_token'}
    assert extracted_identifiers == extracted_variables

def test_variable_details_1():
    code = '''
def get_func_identifier(token_pos, func_token, instruction):
    """ 
    returns a function identifier's positions, start and end col
    """

    identifier_start_pos = token_pos + (len(func_token) - 1) + 2 

    # let's find the occurence position of ( 
    lbracket = instruction.find("(")

    identifier_end_pos  = lbracket - 1 

    varx = 10

    varx = varx + 1 + (varx * varx)

    return identifier_start_pos, identifier_end_pos 

class Person:
    def __init__(self, name):
        self.name = name
    def display(self):
        print(self.name)

p1 = Person("Lemi")
p1.display()
'''
    parsed_code = ast.parse(code)
    extractor = VariableExtractor()
    extractor.visit(parsed_code)
    extracted_identifiers = extractor.get_variables()

    splitted_code = code.split("\n")
    identifier_details = VariableDetails(splitted_code, extracted_identifiers)
    json_details = identifier_details.get_detail()

    expected_details = {
        "token_pos": {
            1: {
                "line": 2,
                "start_col": 24,
                "end_col": 32
            },
            2: {
                "line": 7,
                "start_col": 27,
                "end_col": 35
            }
        },
        "instruction": {
            1: {
                "line": 2,
                "start_col": 47,
                "end_col": 57
            },
            2: {
                "line": 10,
                "start_col": 15,
                "end_col": 25
            }
        },
        "func_token": {
            1: {
                "line": 2,
                "start_col": 35,
                "end_col": 44
            },
            2: {
                "line": 7,
                "start_col": 44,
                "end_col": 53
            }
        },
        "identifier_start_pos": {
            1: {
                "line": 7,
                "start_col": 4,
                "end_col": 23
            },
            2: {
                "line": 18,
                "start_col": 11,
                "end_col": 30
            }
        },
        "lbracket": {
            1: {
                "line": 10,
                "start_col": 4,
                "end_col": 11
            },
            2: {
                "line": 12,
                "start_col": 26,
                "end_col": 33
            }
        },
        "identifier_end_pos": {
            1: {
                "line": 12,
                "start_col": 4,
                "end_col": 21
            },
            2: {
                "line": 18,
                "start_col": 33,
                "end_col": 50
            }
        },
        "varx": {
            1: {
                "line": 14,
                "start_col": 4,
                "end_col": 7
            },
            2: {
                "line": 16,
                "start_col": 11,
                "end_col": 14
            },
            3: {
                "line": 16,
                "start_col": 4,
                "end_col": 7
            },
            4: {
                "line": 16,
                "start_col": 30,
                "end_col": 33
            },
            5: {
                "line": 16,
                "start_col": 23,
                "end_col": 26
            }
        },
        "name": {
            1: {
                "line": 21,
                "start_col": 23,
                "end_col": 26
            },
            2: {
                "line": 22,
                "start_col": 20,
                "end_col": 23
            },
            3: {
                "line": 22,
                "start_col": 13,
                "end_col": 16
            },
            4: {
                "line": 24,
                "start_col": 19,
                "end_col": 22
            }
        },
        "p1": {
            1: {
                "line": 26,
                "start_col": 0,
                "end_col": 1
            },
            2: {
                "line": 27,
                "start_col": 0,
                "end_col": 1
            }
        }
    }
    assert json_details == expected_details


def test_variable_details_2():
    code = """
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def infos(self):
        print(f"NAME: {self.name}")
        print(f"AGE: {self.age}")

company_name = "MINISTRY OF CONSTRUCTION AND URBANISM" 
year = 2023
instance = Person("Leon", 54)
print(f"{company_name} {year}")
instance.infos()
"""
    parsed_code = ast.parse(code)
    extractor = VariableExtractor()
    extractor.visit(parsed_code)
    extracted_identifiers = extractor.get_variables()

    splitted_code = code.split("\n")
    identifier_details = VariableDetails(splitted_code, extracted_identifiers)
    json_details = identifier_details.get_detail()

    expected_details =  {
        "age": {
            1: {
                "line": 3,
                "start_col": 29,
                "end_col": 31
            },
            2: {
                "line": 5,
                "start_col": 19,
                "end_col": 21
            },
            3: {
                "line": 5,
                "start_col": 13,
                "end_col": 15
            },
            4: {
                "line": 9,
                "start_col": 27,
                "end_col": 29
            }
        },
        "name": {
            1: {
                "line": 3,
                "start_col": 23,
                "end_col": 26
            },
            2: {
                "line": 4,
                "start_col": 20,
                "end_col": 23
            },
            3: {
                "line": 4,
                "start_col": 13,
                "end_col": 16
            },
            4: {
                "line": 8,
                "start_col": 28,
                "end_col": 31
            }
        },
        "company_name": {
            1: {
                "line": 11,
                "start_col": 0,
                "end_col": 11
            },
            2: {
                "line": 14,
                "start_col": 9,
                "end_col": 20
            }
        },
        "year": {
            1: {
                "line": 12,
                "start_col": 0,
                "end_col": 3
            },
            2: {
                "line": 14,
                "start_col": 24,
                "end_col": 27
            }
        },
        "instance": {
            1: {
                "line": 13,
                "start_col": 0,
                "end_col": 7
            },
            2: {
                "line": 15,
                "start_col": 0,
                "end_col": 7
            }
        }
    }

    assert json_details == expected_details

