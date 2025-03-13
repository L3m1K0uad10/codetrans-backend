import asyncio

from googletrans import Translator
from transformers import MarianMTModel, MarianTokenizer



async def get_translation(comment, **kwargs):
    translator = Translator()
    translated_comment = await translator.translate(comment, dest = "fr")

    return translated_comment.text

def translate_with_googletrans(comment, dest = 'fr'):
    res = asyncio.run(get_translation(comment))

    return res


def translate_with_marian(comment):
    model_name = "Helsinki-NLP/opus-mt-en-fr"
    model = MarianMTModel.from_pretrained(model_name)
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    
    translated = model.generate(**tokenizer(
            comment,
            return_tensors = "pt",
            padding = True
        ))
    
    res = tokenizer.decode(translated[0], skip_special_tokens = True)

    return res


def translate(comment):
    """ 
    code: str - code content
    details: dict - details of the code tokens to be translated 
    """
    
    try:
        return translate_with_marian(comment)
    except Exception as e:
        print(f"MarianMTModel failed: {e}")
        try:
            return translate_with_googletrans(comment)
        except Exception as e:
            print(f"Googletrans failed: {e}")
            return None
        
        
response = translate("# This is a comment")
print(response) 