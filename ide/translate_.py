from transformers import MarianMTModel, MarianTokenizer



"""
NOTE: i handle multiline comments type:
e.g1
    '''
    this is a multiline comment
    end of comment
    '''
e.g2
    '''start of comment:
    this is a multiline comment
    end of comment'''
"""
def translate_with_marian(code, details):
    model_name = "Helsinki-NLP/opus-mt-en-fr"
    model = MarianMTModel.from_pretrained(model_name)
    tokenizer = MarianTokenizer.from_pretrained(model_name)

    comments = details.get("comment")
    variables = details.get("variable")
    function_identifiers = details.get("function_identifier")
    class_identifiers = details.get("class_identifier")

    splitted_code = code.split("\n")
    translated_code = splitted_code

    for key, value in comments.items():
        if key == "single comment" or key == "inline comment":
            for key_, value_ in value.items():
                #print(value_)                      - 1 because while splitting the code, the index starts from 0
                #print(splitted_code[value_["line"] - 1][value_["start_col"] - 1:value_["end_col"]])
                comment = splitted_code[value_["line"] - 1][value_["start_col"] - 1:value_["end_col"]]

                translated = model.generate(**tokenizer(
                    comment,
                    return_tensors = "pt",
                    padding = True
                ))

                translated_str = tokenizer.decode(translated[0], skip_special_tokens = True)
                prev_substring = splitted_code[value_["line"] - 1][:value_["start_col"] - 1]
                translated_code[value_["line"] - 1] = prev_substring + translated_str

        if key == "multiline comment":
            for key_, value_ in value.items():
                post_substring = "" # to store the substring after the comment(end_line handling purposes)
                for i in range(value_["start_line"], value_["end_line"] + 1):
                    comment = splitted_code[i - 1][value_["col"]:len(splitted_code[i - 1]) + 1]
                    if comment != '"""' and comment != "'''":
                        if i == value_["start_line"]:
                            comment = splitted_code[i - 1][value_["col"] + 3:len(splitted_code[i - 1]) + 1]
                            print(comment)
                            prev_substring = splitted_code[i - 1][:value_["col"] + 3]
                        elif i == value_["end_line"]:
                            comment = splitted_code[i - 1][value_["col"] - 1:len(splitted_code[i - 1]) - 3]
                            prev_substring = splitted_code[i - 1][:value_["col"]]
                            post_substring = splitted_code[i - 1][value_["col"] + len(comment) - 1:len(splitted_code[i - 1])]
                        else:
                            prev_substring = splitted_code[i - 1][:value_["col"]]
                    if comment == '"""' or comment == "'''":
                        comment = "null"
                        prev_substring = splitted_code[i - 1][:value_["col"] + 3]

                    translated = model.generate(**tokenizer(
                        comment,
                        return_tensors = "pt",
                        padding = True
                    ))

                    translated_str = tokenizer.decode(translated[0], skip_special_tokens = True)
                    if comment == "null":
                        translated_str = ""
                    if i == value_["end_line"] and post_substring != "":
                        translated_str = translated_str + post_substring
                    translated_code[i - 1] = prev_substring + translated_str
                
    
    translated_code = '\n'.join(translated_code)
    return translated_code


def translate(code, details):
    """ 
    code: str - code content
    details: dict - details of the code tokens to be translated 
    """
    return translate_with_marian(code, details)
    
        
        
file_path = "/Users/apple/Documents/projects/codetrans-backend/ide/code.txt"

# Read the content of the program file
with open(file_path, 'r') as file:
    file_content = file.read()

details = {
    "comment": {
        "single comment": {
            "1": {
                "line": 12,
                "start_col": 22,
                "end_col": 55
            },
            "2": {
                "line": 25,
                "start_col": 15,
                "end_col": 41
            }
        },
        "inline comment": {
            "1": {
                "line": 17,
                "start_col": 1,
                "end_col": 37
            },
            "2": {
                "line": 21,
                "start_col": 1,
                "end_col": 46
            }
        },
        "multiline comment": {
            "1": {
                "start_line": 3,
                "col": 4,
                "end_line": 6
            },
            "2": {
                "start_line": 28,
                "col": 4,
                "end_line": 31
            }
        }
    },
    "variable": {
        "name": {
            "1": {
                "line": 4,
                "start_col": 41,
                "end_col": 44
            },
            "2": {
                "line": 7,
                "start_col": 23,
                "end_col": 26
            },
            "3": {
                "line": 8,
                "start_col": 20,
                "end_col": 23
            },
            "4": {
                "line": 8,
                "start_col": 13,
                "end_col": 16
            }
        },
        "nationality": {
            "1": {
                "line": 4,
                "start_col": 47,
                "end_col": 57
            },
            "2": {
                "line": 7,
                "start_col": 29,
                "end_col": 39
            },
            "3": {
                "line": 9,
                "start_col": 27,
                "end_col": 37
            },
            "4": {
                "line": 9,
                "start_col": 13,
                "end_col": 23
            }
        },
        "age": {
            "1": {
                "line": 5,
                "start_col": 8,
                "end_col": 10
            },
            "2": {
                "line": 7,
                "start_col": 42,
                "end_col": 44
            },
            "3": {
                "line": 10,
                "start_col": 19,
                "end_col": 21
            },
            "4": {
                "line": 10,
                "start_col": 13,
                "end_col": 15
            }
        },
        "person1": {
            "1": {
                "line": 18,
                "start_col": 0,
                "end_col": 6
            },
            "2": {
                "line": 22,
                "start_col": 0,
                "end_col": 6
            },
            "3": {
                "line": 34,
                "start_col": 8,
                "end_col": 14
            }
        },
        "person2": {
            "1": {
                "line": 19,
                "start_col": 0,
                "end_col": 6
            },
            "2": {
                "line": 23,
                "start_col": 0,
                "end_col": 6
            },
            "3": {
                "line": 35,
                "start_col": 8,
                "end_col": 14
            }
        },
        "database": {
            "1": {
                "line": 25,
                "start_col": 0,
                "end_col": 7
            },
            "2": {
                "line": 29,
                "start_col": 42,
                "end_col": 49
            },
            "3": {
                "line": 32,
                "start_col": 4,
                "end_col": 11
            },
            "4": {
                "line": 36,
                "start_col": 6,
                "end_col": 13
            }
        },
        "instance": {
            "1": {
                "line": 27,
                "start_col": 12,
                "end_col": 19
            },
            "2": {
                "line": 29,
                "start_col": 16,
                "end_col": 23
            },
            "3": {
                "line": 32,
                "start_col": 20,
                "end_col": 27
            }
        },
        "storage": {
            "1": {
                "line": 27,
                "start_col": 4,
                "end_col": 10
            },
            "2": {
                "line": 34,
                "start_col": 0,
                "end_col": 6
            },
            "3": {
                "line": 35,
                "start_col": 0,
                "end_col": 6
            }
        }
    },
    "function_identifier": {
        "infos": {
            "1": {
                "line": 12,
                "start_col": 9,
                "end_col": 13
            },
            "2": {
                "line": 22,
                "start_col": 9,
                "end_col": 13
            },
            "3": {
                "line": 23,
                "start_col": 9,
                "end_col": 13
            }
        },
        "storage": {
            "1": {
                "line": 27,
                "start_col": 5,
                "end_col": 11
            },
            "2": {
                "line": 34,
                "start_col": 1,
                "end_col": 7
            },
            "3": {
                "line": 35,
                "start_col": 1,
                "end_col": 7
            }
        }
    },
    "class_identifier": {
        "Person": {
            "1": {
                "line": 2,
                "start_col": 7,
                "end_col": 12
            },
            "2": {
                "line": 18,
                "start_col": 11,
                "end_col": 16
            },
            "3": {
                "line": 19,
                "start_col": 11,
                "end_col": 16
            }
        }
    }
}

res = translate(file_content, details)
print(res)