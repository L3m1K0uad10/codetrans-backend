import ast
import builtins
import keyword
import json

from utils.helpers import find_all


"""  
TODO: check it works on self.variable (class attributes)... because there are considered as variables

also we consider class instance name belongs to variables group
"""



"""  
ast.NodeVisitor is a base class that allows you to traverse 
the AST of Python code

visit() The Node Visitor is a class that provides a way to visit every node in the AST and perform specific actions for each type of node (like expressions, statements, assignments, etc.). When you traverse the AST, you use a visitor method for each specific type of node. The method name corresponds to the type of AST node, and it is called automatically as you visit that node.
For example:
If you visit a function definition (FunctionDef), the visitor will call a method like visit_FunctionDef().
If you visit an assignment (Assign), the visitor will call visit_Assign().

"""

# A class to visit nodes in the AST
class VariableExtractor(ast.NodeVisitor):
    def __init__(self):
        self.variables = set()  # To store unique variable names
        self.class_names = set() # it'll help with some filtering stuff
        self.builtins = set(dir(builtins))  # Set of built-in identifiers
        self.keywords = keyword.kwlist

    def visit_Name(self, node):
        # Add the name of the variable to the set if it's not a built-in
        if isinstance(node.ctx, (ast.Store, ast.Load)):  # It's a variable used in an assignment or a load context
            """  
            ctx is based on the class threadeddict a.k.a. ThreadedDict . 
            This class creates a dictionary-like object that has attributes 
            specific to the thread process id

            the id store the name e.g Name(id = "fruit", ctx = Store())
            """
            if node.id != "self" and node.id not in self.class_names and node.id not in self.builtins and node.id not in self.keywords:
                # for avoiding retrieving class name instead of variables and self
                self.variables.add(node.id)
        self.generic_visit(node)  # Continue visiting other nodes

    def visit_ClassDef(self, node):  # for avoiding retrieving class name instead of variables
        self.class_names.add(node.name)
        self.generic_visit(node)

    def get_variables(self):
        return self.variables


class VariableDetails:
    variables = []
    def __init__(self, instructions:list, variables:set):
        self.instructions = instructions
        self.variables = variables
    
    def _occurence(self):
        for i, instruction in enumerate(self.instructions):
            tokens_occurences = find_all(instruction) # returns a dictionary of the occurence of all 

            dict_ = {}
            
            for variable in self.variables:
                if variable in tokens_occurences.keys():
                    dict_[variable] = tokens_occurences[variable]

            if len(dict_) != 0:
                dict_["line"] = i + 1
                VariableDetails.variables.append(dict_)
        
        return VariableDetails.variables
    

    def get_detail(self):
        self._occurence()

        json_data = {}
        count = 0

        for line_variables in VariableDetails.variables:
            for variable in self.variables:
                if variable in line_variables.keys():
                    for i in range(len(line_variables[variable])):
                        if variable not in json_data.keys():
                            json_data[variable] = {
                                1:  { 
                                    "line": line_variables["line"],
                                    "start_col": list(line_variables[variable])[i],
                                    "end_col": list(line_variables[variable])[i] + len(variable) - 1
                                }
                            }
                        else:
                            count = len(json_data[variable]) + 1
                            json_data[variable][count] = {
                                "line": line_variables["line"],
                                "start_col": list(line_variables[variable])[i],
                                "end_col": list(line_variables[variable])[i] + len(variable) - 1
                            }
                count = 0

        return json_data


