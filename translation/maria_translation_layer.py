from transformers import MarianMTModel, MarianTokenizer

from utils.helpers import string_token_length, construct_tokenized_string, is_empty_string



class MarianTranslationLayer:
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

    def _translate_comments(self):
        for key, value in self.comments.items():
            if key == "single comment" or key == "inline comment":
                for key_, value_ in value.items():
                    #print(value_)                      - 1 because while splitting the code, the index starts from 0
                    #print(self.splitted_code[value_["line"] - 1][value_["start_col"] - 1:value_["end_col"]])
                    comment = self.splitted_code[value_["line"] - 1][value_["start_col"] - 1:value_["end_col"]]

                    translated = self.model.generate(**self.tokenizer(
                        comment,
                        return_tensors = "pt",
                        padding = True
                    ))

                    translated_str = self.tokenizer.decode(translated[0], skip_special_tokens = True)

                    # the translation of '''expr...''' can result into <<expr...>> therefore handle it
                    if translated_str.find("«") == value_["start_col"] - 1 and translated_str.find("»") == value_["end_col"] - 1:
                        symbol = self.splitted_code[value_["line"] - 1][value_["start_col"] - 1:value_["start_col"] + 2]
                        translated_str = translated_str.replace("«", symbol)
                        translated_str = translated_str.replace("»", symbol)
                    # another weird case handling e.g ''comment'''
                    if (translated_str[0:2] == "''" and translated_str[2] != "'") or (translated_str[0:2] == '""' and translated_str[2] != '"'):
                        symbol = self.splitted_code[value_["line"] - 1][value_["start_col"] - 1:value_["start_col"] + 2]
                        translated_str = translated_str.replace(self.splitted_code[value_["line"] - 1][value_["start_col"] - 1: value_["start_col"] + 1], symbol)
                        translated_str = translated_str[:len(translated_str) - 1]

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
                                if is_empty_string(comment):
                                    comment = "null"
                                prev_substring = self.splitted_code[i - 1][:value_["col"] + 3]
                            elif i == value_["end_line"]:
                                comment = self.splitted_code[i - 1][value_["col"] - 1:len(self.splitted_code[i - 1]) - 3]
                                prev_substring = self.splitted_code[i - 1][:value_["col"]]
                                post_substring = self.splitted_code[i - 1][value_["col"] + len(comment) - 1:len(self.splitted_code[i - 1])]
                            else:
                                if is_empty_string(comment):
                                    comment = "null"
                                prev_substring = self.splitted_code[i - 1][:value_["col"]]
                        if comment == '"""' or comment == "'''":
                            comment = "null"
                            prev_substring = self.splitted_code[i - 1][:value_["col"] + 3]

                        translated = self.model.generate(**self.tokenizer(
                            comment,
                            return_tensors = "pt",
                            padding = True
                        ))

                        translated_str = self.tokenizer.decode(translated[0], skip_special_tokens = True)

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

                translated = self.model.generate(**self.tokenizer(
                    variable,
                    return_tensors = "pt",
                    padding = True
                ))

                translated_var = self.tokenizer.decode(translated[0], skip_special_tokens = True)

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

                translated = self.model.generate(**self.tokenizer(
                    function_identifier,
                    return_tensors = "pt",
                    padding = True
                ))
                
                translated_func_id = self.tokenizer.decode(translated[0], skip_special_tokens = True)

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

                translated = self.model.generate(**self.tokenizer(
                    class_identifier,
                    return_tensors = "pt",
                    padding = True
                ))
                
                translated_cls_id = self.tokenizer.decode(translated[0], skip_special_tokens = True)

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