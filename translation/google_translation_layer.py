import asyncio

from googletrans import Translator
from transformers import MarianMTModel, MarianTokenizer

from utils.helpers import string_token_length, construct_tokenized_string



class GoogleTranslationLayer:
    def __init__(self, code, details):
        self.model_name = "Helsinki-NLP/opus-mt-en-fr"
        self.model = MarianMTModel.from_pretrained(self.model_name)
        self.tokenizer = MarianTokenizer.from_pretrained(self.model_name)

        self.code = code 
        self.details = details

        self.splitted_code = self.code.split("\n")
        self.translated_code = self.splitted_code

        self.comments = self.details.get("comment")
        self.variables = self.details.get("variable")
        self.function_identifiers = self.details.get("function_identifier")
        self.class_identifiers = self.details.get("class_identifier")

    async def _get_translation(self, token, **kwargs):
        translator = Translator()
        translated_token = await translator.translate(token, dest = "fr")

        return translated_token.text

    def _translate_comments(self):
        for key, value in self.comments.items():
            if key == "single comment" or key == "inline comment":
                for key_, value_ in value.items():
                    #print(value_)                      - 1 because while splitting the code, the index starts from 0
                    #print(self.splitted_code[value_["line"] - 1][value_["start_col"] - 1:value_["end_col"]])
                    comment = self.splitted_code[value_["line"] - 1][value_["start_col"] - 1:value_["end_col"]]

                    translated_str = asyncio.run(self._get_translation(comment))                    

                    # the translation of '''expr...''' can result into <<expr...>> therefore handle it
                    if translated_str.find("«") == value_["start_col"] - 1 and translated_str.find("»") == value_["end_col"] - 1:
                        symbol = self.splitted_code[value_["line"] - 1][value_["start_col"] - 1:value_["start_col"] + 2]
                        translated_str = translated_str.replace("«", symbol)
                        translated_str = translated_str.replace("»", symbol)

                    prev_substring = self.splitted_code[value_["line"] - 1][:value_["start_col"] - 1]
                    self.translated_code[value_["line"] - 1] = prev_substring + translated_str

            if key == "multiline comment":
                for key_, value_ in value.items():
                    post_substring = "" # to store the substring after the comment(end_line handling purposes)
                    for i in range(value_["start_line"], value_["end_line"] + 1):
                        comment = self.splitted_code[i - 1][value_["col"]:len(self.splitted_code[i - 1]) + 1]
                        if comment != '"""' and comment != "'''":
                            if i == value_["start_line"]:
                                comment = self.splitted_code[i - 1][value_["col"] + 3:len(self.splitted_code[i - 1]) + 1]
                                print(comment)
                                prev_substring = self.splitted_code[i - 1][:value_["col"] + 3]
                            elif i == value_["end_line"]:
                                comment = self.splitted_code[i - 1][value_["col"] - 1:len(self.splitted_code[i - 1]) - 3]
                                prev_substring = self.splitted_code[i - 1][:value_["col"]]
                                post_substring = self.splitted_code[i - 1][value_["col"] + len(comment) - 1:len(self.splitted_code[i - 1])]
                            else:
                                prev_substring = self.splitted_code[i - 1][:value_["col"]]
                        if comment == '"""' or comment == "'''":
                            comment = "null"
                            prev_substring = self.splitted_code[i - 1][:value_["col"] + 3]

                        translated_str = asyncio.run(self._get_translation(comment))

                        if comment == "null":
                            translated_str = ""
                        if i == value_["end_line"] and post_substring != "":
                            translated_str = translated_str + post_substring
                        self.translated_code[i - 1] = prev_substring + translated_str
        
    
    def _translate_variables(self):
        for key, value in self.variables.items():
            for key_, value_ in value.items():
                variable = key 
                variable = construct_tokenized_string(variable)

                translated_var = asyncio.run(self._get_translation(variable))

                # replacing the whitespace with underscore encountered in the translation of the variable in case
                if "'" in translated_var:
                    id = translated_var.find("'")
                    translated_var = translated_var.replace("'", "")
                    translated_var = translated_var.replace(translated_var[id - 1], "")
                if string_token_length(translated_var) > 1:
                    translated_var = translated_var.replace(" ", "_")
    
                # not really using the self.variables details provided, just translating all occurences of the variable
                line = self.splitted_code[value_["line"] - 1]
                translated_line = line.replace(key, translated_var)

                self.translated_code[value_["line"] - 1] = translated_line
                #print("self.translated_code: ", variable, self.translated_code)
    
    def _translate_function_identifier(self):
        for key, value in self.function_identifiers.items():
            for key_, value_ in value.items():
                function_identifier = key 
                function_identifier = construct_tokenized_string(function_identifier)

                translated_func_id = asyncio.run(self._get_translation(function_identifier))

                # replacing the whitespace with underscore encountered in the translation of the function_identifier in case
                # also handling quotes in the translation in case
                if "'" in translated_func_id:
                    id = translated_func_id.find("'")
                    translated_func_id = translated_func_id.replace("'", "")
                    translated_func_id = translated_func_id.replace(translated_func_id[id - 1], "")
                if string_token_length(translated_func_id) > 1:
                    translated_func_id = translated_func_id.replace(" ", "_")
    
                # not really using the function_identifiers details provided, just translating all occurences of the function_identifier
                line = self.splitted_code[value_["line"] - 1]
                translated_line = line.replace(key, translated_func_id)

                self.translated_code[value_["line"] - 1] = translated_line
        
    def _translate_class_identifier(self):
        for key, value in self.class_identifiers.items():
            for key_, value_ in value.items():
                class_identifier = key 
                class_identifier = construct_tokenized_string(class_identifier)

                translated_cls_id = asyncio.run(self._get_translation(class_identifier))

                # replacing the whitespace with underscore encountered in the translation of the class_identifier in case
                # also handling quotes in the translation in case
                if "'" in translated_cls_id:
                    id = translated_cls_id.find("'")
                    translated_cls_id = translated_cls_id.replace("'", "")
                    translated_cls_id = translated_cls_id.replace(translated_cls_id[id - 1], "")
                if string_token_length(translated_cls_id) > 1:
                    translated_cls_id = translated_cls_id.replace(" ", "_")
    
                # not really using the class_identifier details provided, just translating all occurences of the class_identifier
                line = self.splitted_code[value_["line"] - 1]
                translated_line = line.replace(key, translated_cls_id)

                self.translated_code[value_["line"] - 1] = translated_line

    def translate(self, level):
        if level == "Complete":
            self._translate_comments()
            self._translate_variables()
            self._translate_function_identifier()
            self._translate_class_identifier()
        else:
            self._translate_comments()

        translated_code = '\n'.join(self.translated_code)
        return translated_code
    
        
""" 
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
        "print_infos": {
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
print(res) """