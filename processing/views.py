import json
import ast

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from parsing import CommentDetails, FunctionIdentifierExtractor, FunctionIdentifierDetails, ClassIdentifierExtractor, ClassIdentifierDetails, VariableExtractor, VariableDetails
from translation import GoogleTranslationLayer, MarianTranslationLayer



def retrieve_tokens(code, level = "Complete"):
    """  
    retrieve the tokens: comments, class and function identifiers from a code file
    """

    splitted_code = code.split("\n")
    parsed_code = ast.parse(code)

    if level == "Complete":
        # comment details
        comment = CommentDetails(code)
        comment_details = comment.get_details()

        # variable details
        variable_extractor = VariableExtractor()
        variable_extractor.visit(parsed_code)
        extracted_variables = variable_extractor.get_variables()

        variable_details = VariableDetails(splitted_code, extracted_variables)
        variable_details = variable_details.get_detail()

        # function identifier details
        function_idf_extractor = FunctionIdentifierExtractor()
        function_idf_extractor.visit(parsed_code)
        extracted_identifiers = function_idf_extractor.get_identifiers()

        function_identifier = FunctionIdentifierDetails(splitted_code, extracted_identifiers)
        function_identifier_details = function_identifier.get_detail()

        # class identifier details
        class_idf_extractor = ClassIdentifierExtractor()
        class_idf_extractor.visit(parsed_code)
        extracted_identifiers = class_idf_extractor.get_identifiers()

        class_identifier = ClassIdentifierDetails(splitted_code, extracted_identifiers)
        class_identifier_details = class_identifier.get_detail()

        data = {
            "comment": comment_details,
            "variable": variable_details,
            "function_identifier": function_identifier_details,
            "class_identifier": class_identifier_details
        }
    else:
        # comment details
        comment = CommentDetails(code)
        comment_details = comment.get_details()

        data = {
            "comment": comment_details,
        }

    return data


def translate_tokens(code, details, level = "Complete"):
    """
    translate the tokens to the code
    code: str - code content
    details: dict - details of the code tokens to be translated 
    """
    try:
        maria_translation_layer = MarianTranslationLayer(code, details)
        maria_translation = maria_translation_layer.translate(level)
        return maria_translation
    except Exception as e:
        print(f"MarianMTModel failed: {e}")
        try:
            google_translation_layer = GoogleTranslationLayer(code, details)
            google_translation = google_translation_layer.translate(level)
            return google_translation
        except Exception as e:
            print(f"Googletrans failed: {e}")
            return None


@csrf_exempt
def ProcessingView(request, pk = None, *args, **kwargs):
    
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))

            code = data.get("file_content")
            level = data.get("level")
            
            details = retrieve_tokens(code, level)
            translated_code = translate_tokens(code, details, level)

            data["translated_code"] = translated_code

            return JsonResponse(data, status = 200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status = 400)
