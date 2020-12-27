from pathlib import Path
from slugify import slugify


def create_object(lang_name:str,lang_code:str,direction:str,has_case:bool,has_letters:bool):
    #Convert user input to prevent Python and os errors
    lang_name = slugify(lang_name).replace('-','_')
    lang_code = slugify(lang_code).replace('-','_')
    
    
    create_object_file(lang_name,lang_code,direction,has_case,has_letters)
    create_stop_words(lang_name,lang_code)

    return lang_name, lang_code


def create_object_file(lang_name:str,lang_code:str,direction:str,has_case:bool,has_letters:bool):
    path = (Path.cwd() / 'new_lang' / lang_name)
    path.mkdir(parents=True, exist_ok=True)
    init = path / '__init__.py'
    init.write_text(
f'''import spacy
from spacy.language import Language
from spacy.lang.tokenizer_exceptions import URL_MATCH
from thinc.api import Config
from .stop_words import STOP_WORDS


# https://nightly.spacy.io/api/language#defaults
class {lang_name.capitalize()}Defaults(Language.Defaults):
   stop_words = STOP_WORDS
   prefixes = tuple()
   suffixes = tuple()
   infixes = tuple()
   token_match = None
   url_match = URL_MATCH
   writing_system = {{"direction": "{direction}", "has_case": {has_case}, "has_letters": {has_letters}}}

@spacy.registry.languages("{lang_code}") #https://nightly.spacy.io/api/top-level#registry
class {lang_name.capitalize()}(Language):
    lang = "{lang_code}"
    Defaults = {lang_name.capitalize()}Defaults


__all__ = ["{lang_name.capitalize()}"]
''')


def create_stop_words(lang_name:str,lang_code:str):
    path = (Path.cwd() / 'new_lang' / lang_name)
    path = path / 'stop_words.py'
    path.write_text(
f'''
# coding: utf8
from __future__ import unicode_literals


STOP_WORDS = set(
    """
""".split()
)
''')
    
def create_tokenizer_exceptions(lang_name:str,lang_code:str):
    #see https://github.com/explosion/spaCy/blob/develop/spacy/lang/sr/tokenizer_exceptions.py
    path = (Path.cwd() / 'new_lang' / lang_name)
    path = path / 'tokenizer_exceptions.py'
    path.write_text(
f"""
from spacy.lang.tokenizer_exceptions import BASE_EXCEPTIONS
from spacy.symbols import ORTH, NORM
from spacy.util import update_exc

_exc = {{}}

_new_exc = [] #ex. {{ORTH: "пoн", NORM: "понедељак"}},

for new_exc in _new_exc:
    _exc[new_exc[ORTH]] = [new_exc]

TOKENIZER_EXCEPTIONS = update_exc(BASE_EXCEPTIONS, _exc)
""")