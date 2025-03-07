import ast
import pytest
from parsing.function_identifier_parser import FunctionIdentifierExtractor, FunctionIdentifierDetails



#NOTE: the coordinate of the cursor(row, col) start from 1 thus (1, 1) is the first character in the code(top-left corner)

def test_function_identifier_extractor():
    code = '''
class Person:
    def __init__(self, name):
        self.name = name
    def display(self):
        print(self.name)

p1 = Person("C0D3R")
p1.display() 

def print_name(name):
    print(name)

print_name("C0D3R")
'''
    parsed_code = ast.parse(code)
    extractor = FunctionIdentifierExtractor()
    extractor.visit(parsed_code)
    extracted_identifiers = extractor.get_identifiers()
    
    expected_identifiers = {"print_name", "display"}
    assert extracted_identifiers == expected_identifiers

def test_function_identifier_details():
    code = '''
class Person:
    def __init__(self, name):
        self.name = name
    def display(self):
        print(self.name)

p1 = Person("C0D3R")
p1.display() 

def print_name(name):
    print(name)

print_name("C0D3R")
'''
    parsed_code = ast.parse(code)
    extractor = FunctionIdentifierExtractor()
    extractor.visit(parsed_code)
    extracted_identifiers = extractor.get_identifiers()

    splitted_code = code.split("\n")
    identifier_details = FunctionIdentifierDetails(splitted_code, extracted_identifiers)
    json_details = identifier_details.get_detail()

    expected_details =  {
        "display": {
            1: {
                "line": 4,
                "start_col": 9,
                "end_col": 15
            },
            2: {
                "line": 8,
                "start_col": 4,
                "end_col": 10
            }
        },
        "print_name": {
            1: {
                "line": 10,
                "start_col": 5,
                "end_col": 14
            },
            2: {
                "line": 13,
                "start_col": 1,
                "end_col": 10
            }
        }
    }
    assert json_details == expected_details

