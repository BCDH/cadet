import srsly
import shutil
from pathlib import Path
from typing import List, Optional
from spacy.tokens import Doc, Span
from spacy.matcher import PhraseMatcher

from fastapi import Request, Form, File, UploadFile, APIRouter, Depends,HTTPException
from fastapi.templating import Jinja2Templates
from app.util.login import get_current_username
from fastapi.responses import FileResponse,RedirectResponse


templates = Jinja2Templates(directory="app/templates")

router = APIRouter(dependencies=[Depends(get_current_username)])


@router.get("/export-texts")
async def read_items(request: Request):
    new_lang = Path.cwd() / "new_lang"
    if len(list(new_lang.iterdir())) > 0:
        return templates.TemplateResponse("export-texts.html", {"request": request})
    else: 
        return templates.TemplateResponse(
            "error_please_create.html", {"request": request}
        )

@router.get("/download")
async def download():
    

    #confirm json lookups are valid 
    new_lang = Path.cwd() / "new_lang"
    lang_name = list(new_lang.iterdir())[0].name
    lookups_path = new_lang / lang_name / "lookups"
    for lookup in lookups_path.iterdir():
        key = lookup.stem[lookup.stem.find('_') + 1:]
        if 'lemma' in key:
            lemma_data = srsly.read_json(lookup)
            if isinstance(lemma_data, str):
                return RedirectResponse("/edit_lookup?type=lemma")

        if 'features' in key:
            features_data = srsly.read_json(lookup)
            if isinstance(features_data, str):
                return RedirectResponse("/edit_lookup?type=features")
        if 'pos' in key:
            pos_data = srsly.read_json(lookup)
            if isinstance(pos_data, str):
                return RedirectResponse("/edit_lookup?type=pos")
    
    #if valid, continue
    texts = get_texts()
    filenames = get_filenames()
    nlp = get_nlp()
    nlp.max_length = len(max(texts, key=len))+1
    #TODO handle memory errors caused by change above 
    if texts and nlp: 
        docs = [doc for doc in list(nlp.pipe(texts))]
        
        # let each Doc remember the file it came from
        for doc, filename in zip(docs,filenames):
            doc.user_data['filename'] =  filename

        docs = update_tokens_with_lookups(nlp, docs)
        conll = [doc_to_conllu(doc) for doc in docs]

        # write conll to file, TODO this should be possible to do in memory
        temp_path = Path('/tmp/conllu_export')
        if temp_path.exists():
            shutil.rmtree(temp_path)
            temp_path.mkdir(parents=True, exist_ok=True)
        else:
            temp_path.mkdir(parents=True, exist_ok=True)
        for filename, conll in zip(filenames,conll):
            conll_filename = filename.split('.')[0] +'.conllu'
            (temp_path / conll_filename).write_text(conll)

        #shutil.make_archive("zipped_sample_directory", "zip", "sample_directory")
        shutil.make_archive(str(temp_path), 'zip', str(temp_path))
        zip_file = str(temp_path).split('/')[-1]+'.zip'
        #save each doc to a file, return single zip file with all CONFIRM, can import directory into INCEpTION

        return FileResponse(f'/tmp/conllu_export.zip', media_type="application/zip", filename=lang_name + '_'+ zip_file)

def get_filenames() -> List[str]:
    new_lang = Path.cwd() / "new_lang"
    if len(list(new_lang.iterdir())) > 0:
        texts_path = list(new_lang.iterdir())[0] / "texts"
        if not texts_path.exists():
            return None
        filenames = [text.name for text in texts_path.iterdir()]
        return filenames

def get_texts() -> List[str]:
    new_lang = Path.cwd() / "new_lang"
    if len(list(new_lang.iterdir())) > 0:
        texts_path = list(new_lang.iterdir())[0] / "texts"
        if not texts_path.exists():
            return None
        texts = [text.read_text() for text in texts_path.iterdir()]
        return texts

def get_nlp():
    # Load language object as nlp
    new_lang = Path.cwd() / "new_lang"
    lang_name = list(new_lang.iterdir())[0].name
    try:
        mod = __import__(f"new_lang.{lang_name}", fromlist=[lang_name.capitalize()])
    except SyntaxError:  # Unable to load __init__ due to syntax error
        # redirect /edit?file_name=examples.py
        message = "[*] SyntaxError, please correct this file to proceed."
        return RedirectResponse(url="/edit?file_name=tokenizer_exceptions.py")
    cls = getattr(mod, lang_name.capitalize())
    nlp = cls()
    return nlp


def update_tokens_with_lookups(nlp, docs:List[Doc]) -> List[Doc]:

    #Read the lookups directory, make dict of table names and path to json files
    new_lang = Path.cwd() / "new_lang"
    lang_name = list(new_lang.iterdir())[0].name
    lookups_path = new_lang / lang_name / "lookups"
    for lookup in lookups_path.iterdir():
        key = lookup.stem[lookup.stem.find('_') + 1:]
        if 'lemma' in key:
            lemma_data = srsly.read_json(lookup)
            assert isinstance(lemma_data, dict)

        if 'features' in key:
            features_data = srsly.read_json(lookup)
            assert isinstance(features_data, dict)
        if 'pos' in key:
            pos_data = srsly.read_json(lookup)
            assert isinstance(pos_data, dict)

    matcher = PhraseMatcher(nlp.vocab)
    try:
        for ent in features_data.keys():
                matcher.add(ent, [nlp(ent)])
    except AttributeError as e:
        print(e)

    for doc in docs:
        for t in doc:
            
            lemma = lemma_data.get(t.text, None)
            if lemma:
                t.lemma_ = lemma
            
            pos = pos_data.get(t.text, None)
            if pos:
                try:
                    t.pos_ = pos
                except Exception as e: 
                    raise HTTPException(status_code=404, detail="Invalid part of speech type: " + str(e))
            
        matches = matcher(doc)
        for match_id, start, end in matches:
            string_id = nlp.vocab.strings[match_id]
            #ent_label = entity_data.get(string_id, None)
            span = Span(doc, start, end, label=string_id)
            if doc.spans.get('ents',None):
                doc.spans['ents'].append(span)
            else:
                doc.spans["ents"] = [span]


    return docs

def load_features(doc):
    """Take a Doc object with ent spans.  Use the lookups to label 
    each token in the Doc using the token's index. Returns a dictionary with the 
    token index as key and the entity label as value. If
     
    Args:
        doc (Doc): a spaCy doc object with entries in doc.spans['ents']

    Returns:
        dict: ent lookup by token index
    """
    new_lang = Path.cwd() / "new_lang"
    lang_name = list(new_lang.iterdir())[0].name
    lookups_path = new_lang / lang_name / "lookups"
    for lookup in lookups_path.iterdir():
        key = lookup.stem[lookup.stem.find('_') + 1:]
        if 'features' in key:
            features_data = srsly.read_json(lookup)
            assert isinstance(features_data, dict)
    tokens_with_features = {}
    if doc.spans.get('ents', None):
        for span in doc.spans['ents']:
            feat = features_data.get(span.text,None)
            for t in span:
                tokens_with_features[t.i] = feat
    return tokens_with_features

def doc_to_conllu(doc) -> str:
    """
    Converts a spaCy Doc object to string formatted using CoNLL-U format 
    https://dkpro.github.io/dkpro-core/releases/2.2.0/docs/format-reference.html#format-ConllU
    
    The CoNLL-U format format targets dependency parsing. 
    Columns are tab-separated. Sentences are separated by a blank new line.
    ID  FORM    LEMMA   CPOSTAG POSTAG  FEATS   HEAD    DEPREL  DEPS    MISC   
    
    example:
    1	They	they	PRON	PRN	Case=Nom|Number=Plur	2	nsubj	4:nsubj	_
    2	buy	buy	VERB	VB	Number=Plur|Person=3|Tense=Pres	0	root	_	_
    3	and	and	CONJ	CC	_	2	cc	_	_
    4	sell	sell	VERB	VB	Number=Plur|Person=3|Tense=Pres	2	conj	0:root	_
    5	books	book	NOUN	NNS	Number=Plur	2	dobj	4:dobj	SpaceAfter=No
    6	.	.	PUNCT	.	_	2	punct	_	_
    
    Args:
        doc ([type]): [description]
    """
    data = []
    
    tokens_with_features = load_features(doc)
    # split into sents on \n, then after each sent add blank row
    index = 0
    for tok in doc:
        if is_nl_token(tok) and len(data) > 0:  # to avoid generating the first line as empty
            data.append({})
            index = 0
        else:
            if tok.is_space:
                form = "_"
                lemma = "_"
            else:
                form = tok.orth_
                lemma = tok.lemma_
            tok_id = index + 1  # tok.i + 1
            index += 1
            
            misc = "SpaceAfter=No" if not tok.whitespace_ else "_"
            row = {}
            #ID  FORM    LEMMA   CPOSTAG POSTAG  FEATS   HEAD    DEPREL  DEPS    MISC   

            row["ID"] = str(tok_id) # Word index, integer starting at 1 for each new sentence; may be a range for tokens with multiple words.
            row["FORM"] = "_" if form == '' else form #Word form or punctuation symbol.
            row["LEMMA"] = '_' if lemma == '' else lemma #Lemma or stem of word form.        
            row["CPOSTAG"] = "_" if tok.pos_ == '' else tok.pos_ #Part-of-speech tag from the universal POS tag set.
            row["POSTAG"] = "_" #Language-specific part-of-speech tag; underscore if not available.
            # FEATS List of morphological features from the universal feature inventory or from a defined language-specific extension; underscore if not available.
            if tok.i in tokens_with_features.keys():
                row["FEATS"] = tokens_with_features[tok.i]
            else:
                row["FEATS"] = "_"
            if row["FEATS"] == '':
                row["FEATS"] = '_'
            row["HEAD"] = "_"
            row["DEPREL"] = "_"
            row["DEPS"] = "_"
            row["MISC"] = "_"
            data.append(row)
    output_file = f""""""
    for row in data:
        if len(row.keys()) == 0:
            output_file += '\n'
        else:
            for column in row.keys():
                if column == "MISC":
                    output_file += row[column] + '\n'
                else:
                    output_file += row[column] + '\t'
    return output_file

def doc_to_conll(doc) -> str:
    """
    Converts a spaCy Doc object to string formatted using CoreNLP CoNLL format for pos, lemma and entity
    https://dkpro.github.io/dkpro-core/releases/2.2.0/docs/format-reference.html#format-ConllCoreNlp
    
    The CoreNLP CoNLL format is used by the Stanford CoreNLP package. 
    Columns are tab-separated. Sentences are separated by a blank new line.

    example:
    1	Selectum	Selectum	NNP	O	_	_
    2	,	,	,	O	_	_
    3	Société	Société	NNP	O	_	_
    4	d'Investissement	d'Investissement	NNP	O	_	_
    5	à	à	NNP	O	_	_
    6	Capital	Capital	NNP	O	_	_
    7	Variable	Variable	NNP	O	_	_
    8	.	.	.	O	_	_
    
    Args:
        doc ([type]): [description]
    """
    data = []
    
    tokens_with_features = load_features(doc)
    # split into sents on \n, then after each sent add blank row
    for tok in doc:
        if is_nl_token(tok):
            data.append({})
        else:
            if tok.is_space:
                form = "_"
                lemma = "_"
            else:
                form = tok.orth_
                lemma = tok.lemma_
            tok_id = tok.i +1
            
            misc = "SpaceAfter=No" if not tok.whitespace_ else "_"
            row = {}
            
            row["ID"] = str(tok_id) # Token counter, starting at 1 for each new sentence.
            row["FORM"] = "_" if form == '' else form #Word form or punctuation symbol.
            row["LEMMA"] = '_' if lemma == '' else lemma #Lemma of the word form.        
            row["POSTAG"] = "_" if tok.pos_ == '' else tok.pos_ #Fine-grained part-of-speech tag
            #Named Entity tag, or underscore if not available. 
            # If a named entity covers multiple tokens, all of the tokens simply carry 
            # the same label without (no sequence encoding).
            # INCEpTION interprets this data as ent spans, yay! 
            if tok.i in tokens_with_features.keys():
                row["NER"] = tokens_with_features[tok.i]
            else:
                row["NER"] = "_" 
            row["HEAD"] = "_"
            row["DEPREL"] = "_"
            
            data.append(row)
    output_file = f""""""
    for row in data:
        if len(row.keys()) == 0:
            output_file += '\n'
        else:
            for column in row.keys():
                if column == "DEPREL":
                    output_file += row[column] + '\n'
                else:
                    output_file += row[column] + '\t'
    return output_file

def is_nl_token(t):
    # if a token consists of all space, and has at least one newline char, we segment as a sentence.
    if t.is_space and '\n' in t.text:
        return True
    else:
        return False
