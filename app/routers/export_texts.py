import srsly
import shutil
from pathlib import Path
from typing import List, Optional
from spacy.tokens import Doc, Span
from spacy.matcher import PhraseMatcher

from fastapi import Request, Form, File, UploadFile, APIRouter, Depends
from fastapi.templating import Jinja2Templates
from app.util.login import get_current_username
from fastapi.responses import FileResponse

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(dependencies=[Depends(get_current_username)])


@router.get("/export-texts")
async def read_items(request: Request):
    return templates.TemplateResponse("export-texts.html", {"request": request})

@router.get("/download")
async def download():
    
    # # update the doc from seeds and lookups 
    #     #check if under updated seeds
    #     #elif in lookups 
    #     #else add to 
    # text = [a for a in texts if a['filename'] == filename][0]
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
        if 'pos' in key:
            pos_data = srsly.read_json(lookup)

    matcher = PhraseMatcher(nlp.vocab)
    for ent in entity_data.keys():
            matcher.add(ent, [nlp(ent)])

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
    Adapted from textacy doc_to_conll function 

    example:
    en-orig.conll	0	0	John	NNP	(TOP(S(NP*)	john	-	-	-	(PERSON)	(A0)	(1)
    en-orig.conll	0	1	went	VBD	(VP*	go	go.02	-	-	*	(V*)	-
    en-orig.conll	0	2	to	TO	(PP*	to	-	-	-	*	*	-
    en-orig.conll	0	3	the	DT	(NP*	the	-	-	-	*	*	(2
    en-orig.conll	0	4	market	NN	*)))	market	-	-	-	*	(A1)	2)
    en-orig.conll	0	5	.	.	*))	.	-	-	-	*	*	-

    Args:
        doc ([type]): [description]
    """
    rows = []
    
    for i, tok in enumerate(doc):
        
        if tok.is_space:
            form = " "
            lemma = " "
        else:
            form = tok.orth_
            lemma = tok.lemma_
        tok_id = i + 1
        
        misc = "SpaceAfter=No" if not tok.whitespace_ else "_"
        rows.append(
            "\t".join(
                [
                    # 1	Document ID	This is a variation on the document filename
                    doc.user_data['filename'],
                    # 2	Part number	Some files are divided into multiple parts numbered as 000, 001, 002, ... etc.
                    "0",
                    # 3	Word number	
                    str(tok_id),
                    # 4	Word itself	This is the token as segmented/tokenized in the Treebank. Initially the *_skel file contain the placeholder [WORD] which gets replaced by the actual token from the Treebank which is part of the OntoNotes release.
                    form,
                    # 5	Part-of-Speech	
                    tok.pos_,
                    # 6	Parse bit	This is the bracketed structure broken before the first open parenthesis in the parse, and the word/part-of-speech leaf replaced with a *. The full parse can be created by substituting the asterix with the "([pos] [word])" string (or leaf) and concatenating the items in the rows of that column.
                    "_",
                    # 7	Predicate lemma	The predicate lemma is mentioned for the rows for which we have semantic role information. All other rows are marked with a "-"
                    lemma,
                    # 8	Predicate Frameset ID	This is the PropBank frameset ID of the predicate in Column 7.
                    "_",
                    # 9	Word sense	This is the word sense of the word in Column 3.
                    "_",
                    # 10	Speaker/Author	This is the speaker or author name where available. Mostly in Broadcast Conversation and Web Log data.
                    "_",
                    # 11	Named Entities	These columns identifies the spans representing various named entities.
                    #ent.label_,
                    # 12:N	Predicate Arguments	There is one column each of predicate argument structure information for the predicate mentioned in Column 7.
                    "_",
                    # N	Coreference	Coreference chain information encoded in a parenthesis structure.
                    "_",
                    
                ]
            )
        )
    return '\n'.join(rows)