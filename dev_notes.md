Jan 15 Working on: 
- lookups for pos, lemmata, 
- stop words and freqent terms from corpus


# Create base language object
    x create defaults
    x clone defaults, lookups data
    x change so only one language/project, give option to delete and start over
    - lex_attrs = rules for token.like_num() add to _num_words
    - prefixes = tuple()
    - suffixes = tuple()
    - infixes = tuple()

# Sentences 
    x add example sentences to test tokenizer defaults 

# Tokenization  https://nightly.spacy.io/usage/linguistic-features#tokenization
    X enter example sentences, 
    - visualize defaults, highlight problems
    - regex
    - add exceptions and alter rules as needed 
      - https://nightly.spacy.io/usage/linguistic-features#native-tokenizers

    - Tokenize texts and export them as conllu for import into INCEpTION, otherwise they'll use something else. 

# Lookups and Matching Data
    - create/update lookups-data (not just on clone)
    - Lemma lists/dicts
    - Pos dict
    - Cadet serves automatic suggestions to INCEpTION to create model training data.  To facilitate annotation, Cadet can serve suggestions from lists of lemmata, part-of-speech or entities.


# Load sample corpus texts, export tokenized texts to INCEpTION
    - upload data, save to jsonl
    - tokenize, return frequencies of tokens
    - use frequencies to recommend Stop Words 
    - Tokenize texts and export them as conllu for import into INCEpTION, otherwise they'll use something else. https://github.com/inception-project/inception/issues/1707

# Identify and create stop words, frequent terms with annotation suggestions
    - Quickly bulk-annotate frequent terms (w/context?)
    - mark pos, morph, (rule-based lookups)
    - add to lookups lists for auto-suggestion 

# Serve auto-suggestions 
    - endpoint to serve suggestions from current lang object
    - endpoint to serve suggestions from trained models 
    - serve suggestions from spaCy, Stanza, HuggingFace

# Receive data from INCEpTION save as spaCy training data, run debug
    https://github.com/inception-project/inception/blob/master/inception-active-learning/src/main/java/de/tudarmstadt/ukp/inception/active/learning/ActiveLearningServiceImpl.java
# export object and training data
    - export packaged language object, ready for training 
    - ready for spacy train with data from inception 

## deployment
- Heroku (Hobby per app)
- Deta(problem with cassis dependency)
- Digital Ocean(paid per app) 
- DO VM w/ redirect from princeton domain


Design problems:
- Allow more than one project in the app? NO
    - Users will want to experiment and try different approaches (cloned/not-cloned)
    - User will be confused, potentially working on wrong project add errors
    - Simplicity of one app, one project, can easily deploy another copy 


 --- Updates Jan 5, 2021 ---

1. Updated create and clone language object to spacy3, working on generic object that can be updated in cadet and exported. Workflow to add components:

# List of all files types in spacy.lang 
64 '__init__.py',
63 'stop_words.py', 
53 'examples.py', 
44 'lex_attrs.py', like_num 
33 'tokenizer_exceptions.py'
29 'tag_map.py', dict of tags and coresponding UD labels 
26 'punctuation.py', tokenizer suffix,prefix, infix
11 'syntax_iterators.py', noun_chunks
7 'lemmatizer.py',

fr id'_tokenizer_exceptions_list.py',
fa 'generate_verbs_exc.py',
el 'get_pos_from_wiktionary.py',
ga 'irish_morphology_helpers.py',
sr 'lemma_lookup_licence.txt',
hr 'lemma_lookup_license.txt',
ja 'tag_bigram_map.py',
ja 'tag_orth_map.py',
 
create object > examples > tokenization > texts > stop words > 
  
2. @spacy.registry.languages("pkl") #https://nightly.spacy.io/api/top-level#registry

    - Need to register lookups @spacy.registry.lookups("pkl")
        - https://github.com/explosion/spaCy/blob/develop/spacy/util.py

3. 'syntax_iterators.py', noun_chunks, what are noun_chunks?

4. In lang_clone most language dependencies install without problem.  Korean is an issue and would require a bash script with permissions. 
    - https://github.com/apjanco/cadet-nightly/blob/c8d213322eeb1ae2d869957ecf24572b8750158c/app/util/clone_object.py#L100 

5. Problem with Heroku. On sleep we lose user data. Not a problem for workshops, but would like a long-term no-cost option other than paid tier. 

6. Started on documentation with MkDocs



Lemmatizer (from data vs from lookups)

data work from English and Greek examples
@English.factory(
    "lemmatizer",
    assigns=["token.lemma"],
    default_config={"model": None, "mode": "rule"},
    default_score_weights={"lemma_acc": 1.0},
)
def make_lemmatizer(nlp: Language, model: Optional[Model], name: str, mode: str):
    return EnglishLemmatizer(nlp.vocab, model, name, mode=mode)

tokenizer exceptions, defaults:
URL_PATTERN
BASE_EXCEPTIONS (extra space, \n \t also letter with period and emoticons)

punctuation, defaults:
TOKENIZER_PREFIXES
TOKENIZER_SUFFIXES (good but all Latin)
TOKENIZER_INFIXES