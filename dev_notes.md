need to add tokenizer, norm, 

# Create base language object
    - create defaults
    - clone defaults, lookups data
    TODO 
        - change so only one language, give option to delete and start over
        - create lookups-data (not just on clone)

# Tokenizer  https://nightly.spacy.io/usage/linguistic-features#tokenization
    - enter example sentences, 
    - visualize defaults, highlight problems
    - regex
    - add exceptions and alter rules as needed 
      - https://nightly.spacy.io/usage/linguistic-features#native-tokenizers

# Load seed corpus 
    - upload data, save to jsonl
    - tokenize, return frequencies of tokens
    - use frequencies to recommend Stop Words 

# Load Language Data
    - Lemma lists/dicts
    - pre-trained vectors 
    - create/update lookups data (lemmatization dict)

# Serve auto-suggestions 
    - endpoint to serve suggestions from current lang object
    - endpoint to serve suggestions from trained models 
    - serve suggestions from spaCy, Stanza, HuggingFace

# Receive updated annotation data
    - endpoint to receive data
    - format as spacy json 
    - update the object? (lemmata, pos) 
    - save to disk 

    
(focus: on what's needed to get minimum started with INCEpTION)

# export object and training data
    - export packaged language object, ready for training 
    - ready for spacy train with data from inception 



Design problems:
- Allow more than one project in the app?
    - Users will want to experiment and try different approaches (cloned/not-cloned)
    - User will be confused, potentially working on wrong project add errors
    - Simplicity of one app, one project, can easily deploy another copy 
