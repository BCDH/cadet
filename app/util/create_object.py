import os
from pathlib import Path
from slugify import slugify


def create_object(
    lang_name: str, lang_code: str, direction: str, has_case: bool, has_letters: bool
):
    # Convert user input to prevent Python and os errors
    lang_name = slugify(lang_name).replace("-", "_")
    lang_code = slugify(lang_code).replace("-", "_")

    create_object_file(lang_name, lang_code, direction, has_case, has_letters)
    create_stop_words(lang_name, lang_code)
    create_examples(lang_name, lang_code)
    create_lex_attrs(lang_name, lang_code)
    create_tokenizer_exceptions(lang_name, lang_code)
    create_tag_map(lang_name, lang_code)
    create_punctuation(lang_name, lang_code)
    create_syntax_iterators(lang_name, lang_code)
    create_setup(lang_name, lang_code)
    create_lemmatizer(lang_name, lang_code)
    install_lang(lang_name, lang_code)
    create_base_config(lang_name, lang_code)

    return lang_name, lang_code


def create_object_file(
    lang_name: str, lang_code: str, direction: str, has_case: bool, has_letters: bool
):
    path = Path.cwd() / "new_lang" / lang_name
    path.mkdir(parents=True, exist_ok=True)
    init = path / "__init__.py"
    init.write_text(
        f"""
import spacy
from spacy.language import Language
from spacy.lang.tokenizer_exceptions import URL_MATCH
#from thinc.api import Config
from .stop_words import STOP_WORDS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .punctuation import TOKENIZER_PREFIXES, TOKENIZER_SUFFIXES, TOKENIZER_INFIXES
from .lex_attrs import LEX_ATTRS
from .tag_map import TAG_MAP
from .syntax_iterators import SYNTAX_ITERATORS
from spacy.tokens import Doc
from typing import Optional
from thinc.api import Model
import srsly
from .lemmatizer import {lang_name.capitalize()}Lemmatizer

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

    #custom on init

@{lang_name.capitalize()}.factory(
    "lemmatizer",
    assigns=["token.lemma"],
    default_config={{"model": None, "mode": "lookup", "overwrite": False}},
    default_score_weights={{"lemma_acc": 1.0}},
)
def make_lemmatizer(
    nlp: Language, model: Optional[Model], name: str, mode: str, overwrite: bool
):
    return {lang_name.capitalize()}Lemmatizer(nlp.vocab, model, name, mode=mode, overwrite=overwrite)

#Add locations of lookups data to the registry
@spacy.registry.lookups("{lang_code}")
def do_registration():
    from pathlib import Path
    cadet_path = Path.cwd()
    lookups_path = cadet_path / "new_lang" / "{lang_name}" / "lookups"
    result = {{}}
    for lookup in lookups_path.iterdir():
        key = lookup.stem[lookup.stem.find('_') + 1:]
        result[key] = str(lookup)
    return result

__all__ = ["{lang_name.capitalize()}"]
"""
    )


## David's version
# def create_object_file(
#     lang_name: str, lang_code: str, direction: str, has_case: bool, has_letters: bool
# ):
#     path = Path.cwd() / "new_lang" / lang_name
#     path.mkdir(parents=True, exist_ok=True)
#     init = path / "__init__.py"
#     init.write_text(f"""
# from .stop_words import STOP_WORDS
# from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
# from .punctuation import TOKENIZER_PREFIXES, TOKENIZER_SUFFIXES, TOKENIZER_INFIXES
# from spacy.lang.tokenizer_exceptions import URL_MATCH
# from .tag_map import TAG_MAP
# from .lex_attrs import LEX_ATTRS
# from spacy.language import Language
# from spacy.lang.tokenizer_exceptions import BASE_EXCEPTIONS
# from spacy.lang.norm_exceptions import BASE_NORMS
# from spacy.lookups import Lookups
# from spacy.attrs import LANG, NORM
# from spacy.util import update_exc, add_lookups
# from spacy.tokens import Doc
# import spacy
# import srsly


# # https://nightly.spacy.io/api/language#defaults
# class {lang_name.capitalize()}Defaults(Language.Defaults):
#     stop_words = STOP_WORDS
#     tokenizer_exceptions = TOKENIZER_EXCEPTIONS
#     prefixes = TOKENIZER_PREFIXES
#     suffixes = TOKENIZER_SUFFIXES
#     infixes = TOKENIZER_INFIXES
#     token_match = None
#     url_match = URL_MATCH
#     tag_map = TAG_MAP
#     writing_system = {{"direction": "{direction}", "has_case": {has_case}, "has_letters": {has_letters}}}


# @spacy.registry.languages("{lang_code}") #https://nightly.spacy.io/api/top-level#registry
# class {lang_name.capitalize()}(Language):
#     lang = "{lang_code}"
#     Defaults = {lang_name.capitalize()}Defaults

# class {lang_name.capitalize()}Lemmatizer:
#     def __call__(self, doc: Doc) -> Doc:
#         lookup = srsly.read_json('{lang_name}/lookups/{lang_code}_lemma_lookup.json')
#         for t in doc:
#             lemma = lookup.get(t.text, None)
#             if lemma:
#                 t.lemma_ = lemma
#         return doc


# @Language.factory(
#     "{lang_code}_lemmatizer",
#     assigns=["token.lemma"],
#     default_config={{}},
#     default_score_weights={{"lemma_acc": 1.0}},
# )
# def make_lemmatizer(
#     nlp: Language,
#     name: str,
# ):
#     return {lang_name.capitalize()}Lemmatizer()

# #Add locations of lookups data to the registry
# @spacy.registry.lookups("{lang_code}")
# def do_registration():
#     return {{'lemma_lookup': 'path/to/lookup.json' }}

# __all__ = ["{lang_name.capitalize()}","make_lemmatizer"]
# """)


def create_stop_words(lang_name: str, lang_code: str):
    path = Path.cwd() / "new_lang" / lang_name
    path = path / "stop_words.py"
    path.write_text(
        f'''
# coding: utf8
from __future__ import unicode_literals


STOP_WORDS = set(
    """
""".split()
)
'''
    )


def create_tokenizer_exceptions(lang_name: str, lang_code: str):
    # see https://github.com/explosion/spaCy/blob/develop/spacy/lang/sr/tokenizer_exceptions.py
    path = Path.cwd() / "new_lang" / lang_name
    path = path / "tokenizer_exceptions.py"
    path.write_text(
        f"""
from spacy.lang.tokenizer_exceptions import BASE_EXCEPTIONS
from spacy.symbols import ORTH, NORM, LEMMA
from spacy.util import update_exc

exclusions = [

]

TOKENIZER_EXCEPTIONS = update_exc(BASE_EXCEPTIONS, *exclusions)
"""
    )


def create_examples(lang_name, lang_code):
    path = Path.cwd() / "new_lang" / lang_name
    path = path / "examples.py"
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
"""
    )


def create_lex_attrs(lang_name: str, lang_code: str):
    path = Path.cwd() / "new_lang" / lang_name
    path = path / "lex_attrs.py"
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
"""
    )


def create_tag_map(lang_name: str, lang_code: str):
    path = Path.cwd() / "new_lang" / lang_name
    path = path / "tag_map.py"
    path.write_text(
        f"""
from spacy.symbols import POS, AUX, ADJ, CCONJ, NUM, ADV, ADP, X, VERB, DET, SCONJ, PUNCT
from spacy.symbols import NOUN, PART, INTJ, PRON

TAG_MAP = {{}}
"""
    )


def create_punctuation(lang_name: str, lang_code: str):
    path = Path.cwd() / "new_lang" / lang_name
    path = path / "punctuation.py"
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
"""
    )


def create_syntax_iterators(lang_name: str, lang_code: str):
    path = Path.cwd() / "new_lang" / lang_name
    path = path / "syntax_iterators.py"
    path.write_text(
        f"""
SYNTAX_ITERATORS = {{}}
"""
    )


def create_setup(lang_name, lang_code):
    path = Path.cwd() / "new_lang" / lang_name
    path = path / "setup.py"
    path.write_text(
        f"""
from setuptools import setup
setup(
    name="{lang_code}",
    entry_points={{
        "spacy_languages": ["{lang_code} = {lang_code}:{lang_name.capitalize()}"],
    }}
)
"""
    )


def install_lang(lang_name, lang_code):
    os.system(f"pip install -e  ./new_lang/{lang_name}")


def create_base_config(lang_name, lang_code):
    path = Path.cwd() / "new_lang" / lang_name
    path = path / "base_config.cfg"
    path.write_text(
        f"""[system]
gpu_allocator = null

[nlp]
lang = "{lang_code}"
pipeline = ["tok2vec","tagger","parser", "attribute_ruler", "lemmatizer"]
tokenizer = {{"@tokenizers": "spacy.Tokenizer.v1"}}
batch_size = 1000

[nlp.vocab.lookups]
lemma_lookup = "new_lang/{lang_name}/lookups/{lang_code}_lemma_lookup.json"
#lexeme_norm_lookup = "assets/lookups/srp_lexeme_norm.json"

[components]

[components.tok2vec]
factory = "tok2vec"

[components.tok2vec.model]
@architectures = "spacy.Tok2Vec.v2"

[components.tok2vec.model.embed]
@architectures = "spacy.MultiHashEmbed.v1"
width = ${{components.tok2vec.model.encode.width}}
attrs = ["ORTH", "SHAPE"]
rows = [5000, 2500]
include_static_vectors = false

[components.tok2vec.model.encode]
@architectures = "spacy.MaxoutWindowEncoder.v2"
width = 96
depth = 4
window_size = 1
maxout_pieces = 3

[components.attribute_ruler]
factory = "attribute_ruler"


# There are no recommended transformer weights available for language 'sr'
# yet, so the pipeline described here is not transformer-based.


[components.tagger]
factory = "tagger"

[components.tagger.model]
@architectures = "spacy.Tagger.v1"
nO = null

[components.parser]
factory = "parser"

[components.parser.model]
@architectures = "spacy.TransitionBasedParser.v1"
tok2vec=${{components.tok2vec.model}}
state_type = "parser"
extra_state_tokens = false
hidden_width = 128
maxout_pieces = 3
use_upper = true
nO = null

[initialize]

[initialize.components]

[initialize.components.attribute_ruler]

[initialize.components.attribute_ruler.tag_map]
@readers = "srsly.read_json.v1"
path = "new_lang/{lang_name}/lookups/{lang_code}_tag_map.json"
"""
    )


def create_lemmatizer(lang_name: str, lang_code: str):
    path = Path.cwd() / "new_lang" / lang_name
    path.mkdir(parents=True, exist_ok=True)
    init = path / "lemmatizer.py"
    init.write_text(
        f"""
from typing import List, Tuple
from spacy.pipeline import Lemmatizer
from spacy.tokens import Token
from spacy.vocab import Vocab
from typing import Optional, List, Dict, Tuple
from thinc.api import Model
import spacy 

class {lang_name.capitalize()}Lemmatizer(Lemmatizer):
    def __init__(
        self,
        vocab: Vocab,
        model: Optional[Model],
        name: str = "lemmatizer",
        *,
        mode: str = "lookup",
        overwrite: bool = False,
    ) -> None:
        super().__init__(vocab, model, name, mode=mode, overwrite=overwrite)
        
        lookups_tables = spacy.registry.lookups.get({lang_code})()
        if not nlp.vocab.lookups.has_table('lemma_lookup'):
            language_data = srsly.read_json(lookups_tables["lemma_lookup"])
            nlp.vocab.lookups.add_table("lemma_lookup", language_data)
           
    
    def rule_lemmatize(self, token: Token) -> List[str]:
        pass

    def lookup_lemmatize(self, token: Token) -> List[str]:

        lookup_table = self.lookups.get_table("lemma_lookup")
        string = token.text.lower()
        return [lookup_table.get(string, string)]


"""
    )
