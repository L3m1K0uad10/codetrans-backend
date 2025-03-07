import ast
import pytest
from parsing.comment_parser import CommentExtractor, CommentDetails



#NOTE: the coordinate of the cursor(row, col) start from 1 thus (1, 1) is the first character in the code(top-left corner)


def test_comment_details():
    code = """
# simple addition
result = 5 + 5
print(result) # printing result
\"\"\"multiline comment\"\"\"
'''multiline comment2'''
print("# this is for testing comment")
\"\"\"
nothing is wrong it just a project
\"\"\"

# nested multi-line comments
    '''
        This is another multi-line comment.
        It also contains a nested multi-line comment.
    \"\"\"
        Nested multi-line comment inside another multi-line comment.
    \"\"\"
    '''

# nested strings that contain comment-like content 
nested_string = '''
This is a multi-line string inside a function.
It contains another string that looks like a comment.
\"\"\"
Nested string inside a multi-line string.
\"\"\"
\"\"\"
Another nested string inside a multi-line string.
\"\"\"
Deeply nested string inside another nested string.
\"\"\"
\"\"\"
'''
"""
    comment = CommentDetails(code)
    details = comment.get_details()
    print(details)

    expected_details =  {
        "single comment": {
            1: {
                "line": 2,
                "start_col": 1,
                "end_col": 17
            },
            2: {
                "line": 4,
                "start_col": 15,
                "end_col": 31
            },
            3: {
                "line": 12,
                "start_col": 1,
                "end_col": 28
            },
            4: {
                "line": 21,
                "start_col": 1,
                "end_col": 51
            }
        },
        "inline comment": {
            1: {
                "line": 5,
                "start_col": 1,
                "end_col": 23
            },
            2: {
                "line": 6,
                "start_col": 1,
                "end_col": 24
            }
        },
        "multiline comment": {
            1: {
                "start_line": 8,
                "end_line": 10
            },
            2: {
                "start_line": 13,
                "end_line": 19
            }
        }
    }
    assert details == expected_details

