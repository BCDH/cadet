# Create base language object
    x create defaults
    x clone defaults, lookups data
    x change so only one language/project, give option to delete and start over
    - lex_attrs = rules for token.like_num() add to _num_words
    - prefixes = tuple()
    - suffixes = tuple()
    - infixes = tuple()

# Tokenization  https://nightly.spacy.io/usage/linguistic-features#tokenization
    X enter example sentences, 
    - visualize defaults, highlight problems
    - regex
    - add exceptions and alter rules as needed 
      - https://nightly.spacy.io/usage/linguistic-features#native-tokenizers

# Lemmatization/Lookups Data
    - create/update lookups-data (not just on clone)
    - Lemma lists/dicts
    - pre-trained vectors 
    - create/update lookups data (lemmatization dict)

# Load seed corpus     
    - upload data, save to jsonl
    - tokenize, return frequencies of tokens
    - use frequencies to recommend Stop Words 

# Quickly bulk-annotate frequent terms (w/context?)
    - mark pos, morph, (rule-based lookups)

# Serve auto-suggestions 
    - endpoint to serve suggestions from current lang object
    - endpoint to serve suggestions from trained models 
    - serve suggestions from spaCy, Stanza, HuggingFace

# Receive updated annotation data, update lookups

# export object and training data
    - export packaged language object, ready for training 
    - ready for spacy train with data from inception 



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