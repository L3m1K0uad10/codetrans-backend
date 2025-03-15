import ast
import json
import tokenize # library for tokenizing the code
from io import StringIO # library for input/output string



class CommentExtractor(ast.NodeVisitor):
    def __init__(self):
        self.comments = []

    def visit_Expr(self, node):
        if isinstance(node.value, ast.Str):
            self.comments.append(node.value.s)
        self.generic_visit(node)

    def extract_comments(self, code):
        # StringIO is used to convert the code string into a file-like object
        tokens = tokenize.generate_tokens(StringIO(code).readline) # tokenize the code
        for token in tokens:
            if token.type == tokenize.COMMENT: # check if the token is a comment
                self.comments.append(token.string)
        return self.comments
    

class CommentDetails:
    def __init__(self, code):
        self.code = code
        self.comments = {
            "single comment": {},
            "inline comment": {},
            "multiline comment": {}
        }
        self.extract_comments()

    def extract_comments(self):
        tokens = tokenize.generate_tokens(StringIO(self.code).readline) # gets the information of the tokens like start and end position

        """ line_comments = {}
        multiline_comments = []
        current_multiline = None """

        for token in tokens:
            if token.type == tokenize.COMMENT:
                self.comments["single comment"][len(self.comments["single comment"]) + 1] = {
                    "line": token.start[0],
                    "start_col": token.start[1] + 1,
                    "end_col": token.end[1]
                }
            elif token.type == tokenize.STRING:
                if token.string.startswith(('"""', "'''")):
                    # check if the possibility of nested strings that contain comment-like content
                    # for that we will check if it is preceded by an arithmetic operator or an assignment operator

                    if token.string.endswith(('"""', "'''")) and "\n" not in token.string:
                        precedent =  token.line[token.start[1] - 3 : token.start[1]] # get the 3 characters before the start of the string for checking the possibility of nested strings

                        if precedent != "":
                            if "+ - * / = ( [ {".find(precedent) == -1:
                                self.comments["inline comment"][len(self.comments["inline comment"]) + 1] = {
                                    "line": token.start[0],
                                    "start_col": token.start[1] + 1,
                                    "end_col": token.end[1]
                                }
                        else:
                            self.comments["inline comment"][len(self.comments["inline comment"]) + 1] = {
                                "line": token.start[0],
                                "start_col": token.start[1] + 1,
                                "end_col": token.end[1]
                            }
                    else:
                        precedent =  token.line[token.start[1] - 3 : token.start[1]] # get the 3 characters before the start of the string for checking the possibility of nested strings

                        if precedent != "":
                            if "+ - * / = ( [ {".find(precedent) == -1:
                                self.comments["multiline comment"][len(self.comments["multiline comment"]) + 1] = {
                                    "start_line": token.start[0],
                                    "col": token.start[1],
                                    "end_line": token.end[0]
                                }
                        else:
                            self.comments["multiline comment"][len(self.comments["multiline comment"]) + 1] = {
                                "start_line": token.start[0],
                                "col": token.start[1],
                                "end_line": token.end[0]
                            }    

    def get_details(self):
        return self.comments
    