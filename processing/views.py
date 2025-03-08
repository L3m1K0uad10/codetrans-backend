import json
import ast

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from parsing.comment_parser import CommentDetails
from parsing.function_identifier_parser import FunctionIdentifierExtractor, FunctionIdentifierDetails
from parsing.class_identifier_parser import ClassIdentifierExtractor, ClassIdentifierDetails



def retrieve_tokens(code):
    """  
    retrieve the tokens: comments, class and function identifiers from a code file
    """

    splitted_code = code.split("\n")
    parsed_code = ast.parse(code)

    # comment details
    comment = CommentDetails(code)
    comment_details = comment.get_details()

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
        "function_identifier": function_identifier_details,
        "class_identifier": class_identifier_details
    }

    return data


def translate_tokens(data, code):
    """
    translate the tokens to the code
    """
    pass


@csrf_exempt
def ProcessingView(request, pk = None, *args, **kwargs):
    
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))

            code = data.get("file_content")
            
            data = retrieve_tokens(code)

            return JsonResponse(data, status = 200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status = 400)
