from pathlib import Path
from slugify import slugify


def create_object(lang_name:str,lang_code:str,direction:str,has_case:bool,has_letters:bool):
    #Convert user input to prevent Python and os errors
    lang_name = slugify(lang_name).replace('-','_')
    lang_code = slugify(lang_code).replace('-','_')
    
    
    create_object_file(lang_name,lang_code,direction,has_case,has_letters)
    create_stop_words(lang_name,lang_code)
    create_examples(lang_name,lang_code)
    create_lex_attrs(lang_name,lang_code)
    create_tokenizer_exceptions(lang_name,lang_code)
    create_tag_map(lang_name,lang_code)
    create_punctuation(lang_name,lang_code)
    create_syntax_iterators(lang_name,lang_code)
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
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .punctuation import TOKENIZER_PREFIXES, TOKENIZER_SUFFIXES, TOKENIZER_INFIXES
from .lex_attrs import LEX_ATTRS
from .tag_map import TAG_MAP
from .syntax_iterators import SYNTAX_ITERATORS

# https://nightly.spacy.io/api/language#defaults
class {lang_name.capitalize()}Defaults(Language.Defaults):
    stop_words = STOP_WORDS
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    prefixes = TOKENIZER_PREFIXES
    suffixes = TOKENIZER_SUFFIXES
    infixes = TOKENIZER_INFIXES
    token_match = None
    url_match = URL_MATCH
    tag_map = TAG_MAP
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

def create_examples(lang_name,lang_code):
    path = (Path.cwd() / 'new_lang' / lang_name)
    path = path / 'examples.py'
    path.write_text(
f"""
# coding: utf8
from __future__ import unicode_literals


'''
Example sentences to test spaCy and its language models.

>>> from new_lang.{lang_code}.examples import sentences
>>> docs = nlp.pipe(sentences)
'''


sentences = [  ]
""")

def create_lex_attrs(lang_name:str,lang_code:str):
    path = (Path.cwd() / 'new_lang' / lang_name)
    path = path / 'lex_attrs.py'
    path.write_text(
f"""
from spacy.attrs import LIKE_NUM

_num_words = []

def like_num(text):
    if text.startswith(("+", "-", "±", "~")):
        text = text[1:]
    text = text.replace(",", "").replace(".", "")
    if text.isdigit():
        return True
    if text.count("/") == 1:
        num, denom = text.split("/")
        if num.isdigit() and denom.isdigit():
            return True
    if text.lower() in _num_words:
        return True
    return False

LEX_ATTRS = {{LIKE_NUM: like_num}}
""")



def create_tag_map(lang_name:str,lang_code:str):
    path = (Path.cwd() / 'new_lang' / lang_name)
    path = path / 'tag_map.py'
    path.write_text(
f"""
from spacy.symbols import POS, AUX, ADJ, CCONJ, NUM, ADV, ADP, X, VERB, DET, SCONJ, PUNCT
from spacy.symbols import NOUN, PART, INTJ, PRON

TAG_MAP = {{}}
""")

def create_punctuation(lang_name:str,lang_code:str):
    path = (Path.cwd() / 'new_lang' / lang_name)
    path = path / 'punctuation.py'
    path.write_text(
f"""
from spacy.lang.char_classes import LIST_ELLIPSES, LIST_ICONS, LIST_PUNCT, LIST_QUOTES
from spacy.lang.char_classes import CURRENCY, UNITS, PUNCT
from spacy.lang.char_classes import CONCAT_QUOTES, ALPHA, ALPHA_LOWER, ALPHA_UPPER
from spacy.lang.punctuation import TOKENIZER_PREFIXES as BASE_TOKENIZER_PREFIXES
from spacy.lang.punctuation import TOKENIZER_SUFFIXES as BASE_TOKENIZER_SUFFIXES
from spacy.lang.punctuation import TOKENIZER_INFIXES as BASE_TOKENIZER_INFIXES


_prefixes = BASE_TOKENIZER_PREFIXES

_suffixes = BASE_TOKENIZER_SUFFIXES

_infixes = BASE_TOKENIZER_INFIXES


TOKENIZER_PREFIXES = _prefixes
TOKENIZER_SUFFIXES = _suffixes
TOKENIZER_INFIXES = _infixes
""")

def create_syntax_iterators(lang_name:str,lang_code:str):
    path = (Path.cwd() / 'new_lang' / lang_name)
    path = path / 'syntax_iterators.py'
    path.write_text(
f"""
SYNTAX_ITERATORS = {{}}
""")

def create_lemmatizer(lang_name:str,lang_code:str):
    path = (Path.cwd() / 'new_lang' / lang_name)
    path = path / 'lemmatizer.py'
    path.write_text(
f"""
""")