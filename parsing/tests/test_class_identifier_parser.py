import ast
import pytest
from parsing.class_identifier_parser import ClassIdentifierExtractor, ClassIdentifierDetails



#NOTE: the coordinate of the cursor(row, col) start from 1 thus (1, 1) is the first character in the code(top-left corner)

def test_class_identifier_extractor():
    code = '''
class Person:
    def __init__(self, name):
        self.name = name
    def display(self):
        print(self.name)

p1 = Person("C0D3R")
p1.display() 
'''
    parsed_code = ast.parse(code)
    extractor = ClassIdentifierExtractor()
    extractor.visit(parsed_code)
    extracted_identifiers = extractor.get_identifiers()
    
    expected_identifiers = {"Person"}
    assert extracted_identifiers == expected_identifiers

def test_class_identifier_details():
    code = '''
class Person:
    def __init__(self, name):
        self.name = name
    def display(self):
        print(self.name)

p1 = Person("C0D3R")
p1.display() 
'''
    parsed_code = ast.parse(code)
    extractor = ClassIdentifierExtractor()
    extractor.visit(parsed_code)
    extracted_identifiers = extractor.get_identifiers()

    splitted_code = code.split("\n")
    identifier_details = ClassIdentifierDetails(splitted_code, extracted_identifiers)
    json_details = identifier_details.get_detail()

    expected_details =  {
        "Person": {
            1: {
                "line": 1,
                "start_col": 7,
                "end_col": 12
            },
            2: {
                "line": 7,
                "start_col": 6,
                "end_col": 11
            }
        }
    }
    assert json_details == expected_details

