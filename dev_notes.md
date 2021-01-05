1. add code editor for all files in the object 

# Create base language object
    x create defaults
    x clone defaults, lookups data
    x change so only one language/project, give option to delete and start over
    - lex_attrs = rules for token.like_num() add to _num_words
    - prefixes = tuple()
    - suffixes = tuple()
    - infixes = tuple()

# Tokenizer  https://nightly.spacy.io/usage/linguistic-features#tokenization
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

Start on documentation now!

# List of all files types in spacy.lang 
64 '__init__.py',
63 'stop_words.py', 
53 'examples.py', 
44 'lex_attrs.py', like_num 
33 'tokenizer_exceptions.py'}
29 'tag_map.py', dict of tags and cooresponding UD labels 
26 'punctuation.py', 
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
 
