import ast 
import builtins
import keyword
import json

from utils.helpers import find_all



class FunctionIdentifierExtractor(ast.NodeVisitor):
    def __init__(self):
        self.identifiers = set()  

    def visit_FunctionDef(self, node):
        if node.name != "__init__":
            self.identifiers.add(node.name)
        self.generic_visit(node)

    def get_identifiers(self):
        return self.identifiers



class FunctionIdentifierDetails:
    identifiers = []
    def __init__(self, instructions:list, identifiers:set):
        self.instructions = instructions
        self.identifiers = identifiers

        self.details = {}

    def _occurence(self):
        for i, instruction in enumerate(self.instructions):
            tokens_occurences = find_all(instruction) # returns a dictionary of the occurence of all 

            dict_ = {}
            
            for identifier in self.identifiers:
                if identifier in tokens_occurences.keys():
                    dict_[identifier] = tokens_occurences[identifier]

            if len(dict_) != 0:
                dict_["line"] = i + 1
                FunctionIdentifierDetails.identifiers.append(dict_)
        
        return FunctionIdentifierDetails.identifiers
    
    def get_detail(self):
        self._occurence()

        count = 0

        for line_identifiers in FunctionIdentifierDetails.identifiers:
            for identifier in self.identifiers:
                if identifier in line_identifiers.keys():
                    for i in range(len(line_identifiers[identifier])):
                        if identifier not in self.details.keys():
                            self.details[identifier] = {
                                1:  { 
                                    "line": line_identifiers["line"],
                                    "start_col": list(line_identifiers[identifier])[i] + 1,
                                    "end_col": list(line_identifiers[identifier])[i] + len(identifier)
                                }
                            }
                        else:
                            count = int(len(self.details[identifier]) + 1)
                            self.details[identifier][count] = {
                                "line": line_identifiers["line"],
                                "start_col": list(line_identifiers[identifier])[i] + 1,
                                "end_col": list(line_identifiers[identifier])[i] + len(identifier)
                            }
                count = 0

        return self.details


