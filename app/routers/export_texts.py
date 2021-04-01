import srsly
import shutil
from pathlib import Path
from typing import List, Optional
from spacy.tokens import Doc, Span
from spacy.matcher import PhraseMatcher
import pandas as pd
from fastapi import Request, Form, File, UploadFile, APIRouter, Depends
from fastapi.templating import Jinja2Templates
from app.util.login import get_current_username
from fastapi.responses import FileResponse,RedirectResponse


templates = Jinja2Templates(directory="app/templates")

router = APIRouter(dependencies=[Depends(get_current_username)])


@router.get("/export-texts")
async def read_items(request: Request):
    return templates.TemplateResponse("export-texts.html", {"request": request})

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

        if 'entity' in key:
            entity_data = srsly.read_json(lookup)
            if isinstance(entity_data, str):
                return RedirectResponse("/edit_lookup?type=entity")
        if 'pos' in key:
            pos_data = srsly.read_json(lookup)
            if isinstance(pos_data, str):
                return RedirectResponse("/edit_lookup?type=pos")
    
    #if valid, continue
    texts = get_texts()
    filenames = get_filenames()
    nlp = get_nlp()
    if texts and nlp: 
        docs = [doc for doc in list(nlp.pipe(texts))]
        
        # let each Doc remember the file it came from
        for doc, filename in zip(docs,filenames):
            doc.user_data['filename'] =  filename

        docs = update_tokens_with_lookups(nlp, docs)
        conll = [doc_to_conll(doc) for doc in docs]

        temp_path = Path('/tmp/text_export')
        temp_path.mkdir(parents=True, exist_ok=True)
        for filename, conll in zip(filenames,conll):
            (temp_path / filename).write_text(conll)

        #shutil.make_archive("zipped_sample_directory", "zip", "sample_directory")
        shutil.make_archive(str(temp_path), 'zip', str(temp_path))
        zip_file = str(temp_path).split('/')[-1]+'.zip'
        #save each doc to a file, return single zip file with all CONFIRM, can import directory into INCEpTION

        return FileResponse('/tmp/text_export.zip', media_type="application/zip", filename=zip_file)

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
           
        if 'entity' in key:
            entity_data = srsly.read_json(lookup)
            assert isinstance(lemma_data, dict)
        if 'pos' in key:
            pos_data = srsly.read_json(lookup)
            assert isinstance(lemma_data, dict)

    matcher = PhraseMatcher(nlp.vocab)
    try:
        for ent in entity_data.keys():
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
                t.pos_ = pos
            
        matches = matcher(doc)
        for match_id, start, end in matches:
            string_id = nlp.vocab.strings[match_id]
            ent_label = entity_data.get(string_id, None)
            if ent_label:
                span = Span(doc, start, end, label=ent_label)
                doc.ents = list(doc.ents) + [span]

    return docs

def doc_to_conll(doc) -> str:
    """
    Converts a spaCy Doc object to string formatted using Conll 2012 standards for pos, lemma and entity
    https://inception-project.github.io/releases/0.19.0/docs/user-guide.html#sect_formats_conll2012
    https://dkpro.github.io/dkpro-core/releases/2.2.0/docs/format-reference.html#format-Conll2012
    
    The CoNLL 2012 format targets semantic role labeling and coreference. Columns are whitespace-separated 
    (tabs or spaces). Sentences are separated by a blank new line.

    example:
    #begin document (mz/sinorama/10/ectb_1072); part 000
    mz/sinorama/10/ectb_1072          0          0          A         DT (TOP(S(NP*          -          -          -          -          *     (ARG1*          -
    mz/sinorama/10/ectb_1072          0          1        Gao        NNP      (NML*          -          -          -          -   (PERSON*          *         (8
    mz/sinorama/10/ectb_1072          0          2   Xingjian        NNP         *)          -          -          -          -         *)          *         8)
    mz/sinorama/10/ectb_1072          0          3      Storm         NN         *)          -          -          -          -          *         *)          -
    mz/sinorama/10/ectb_1072          0          4      Blows        VBZ       (VP*       blow         01          2          -          *       (V*)          -
    mz/sinorama/10/ectb_1072          0          5    through         IN       (PP*          -          -          -          -          * (ARGM-DIR*          -
    # end document
    Args:
        doc ([type]): [description]
    """
    data = []
    
    for i, tok in enumerate(doc):
        
        if tok.is_space:
            form = "_"
            lemma = "_"
        else:
            form = tok.orth_
            lemma = tok.lemma_
        tok_id = i +1
        
        misc = "SpaceAfter=No" if not tok.whitespace_ else "_"
        row = {}
        
        row["ID"] = str(tok_id)
        row["FORM"] = "_" if form == '' else form
        row["LEMMA"] = '_' if lemma == '' else lemma
        
        row["POSTAG"] = "_" if tok.pos_ == '' else tok.pos_
        row["NER"] = "_"   #TODO add ent.label_ = "_"
    
        row["HEAD"] = "_"
        row["DEPREL"] = "_"
        
        data.append(row)
    output_file = f""""""
    for row in data:
        for column in row.keys():
            if column == "DEPREL":
                output_file += row[column] + '\n'
            else:
                output_file += row[column] + '\t'
    return output_file