need to add tokenizer, norm, 

# Create base language object
    x create defaults
    x clone defaults, lookups data
    x change so only one language/project, give option to delete and start over

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