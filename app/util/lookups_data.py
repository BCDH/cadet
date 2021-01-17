import spacy
import srsly
import spacy_lookups_data
import shutil
import httpx
from pathlib import Path
from slugify import slugify
from typing import List


def create_lookups_data(lang_name,lang_code, spacy_language):
    #Slugify user input to prevent Python and os errors
    new_lang_name = slugify(lang_name).replace('-','_')
    new_lang_code = slugify(lang_code).replace('-','_')

    #Create a directory for the new language
    new_lang_path = (Path.cwd() / 'new_lang' / new_lang_name)
    new_lookups_path = new_lang_path / 'lookups'
    if not new_lookups_path.exists():
        new_lookups_path.mkdir(parents=True, exist_ok=True)
    
    #UPOS lookups
    upos_filename = new_lookups_path / (new_lang_code + '_upos_lookup.json.gz')
    srsly.write_gzip_json(upos_filename, {})

    #create symbolic link to lookups dir, during nightly-dev this is only option, but should be replaced by registering lookups in init 
    spacy_lookups_dir = Path(spacy_lookups_data.__file__.replace('__init__.py','')) / 'data'
    spacy_lookups_dir.symlink_to(upos_filename)
    
    #LEMMA lookups 
    lemma_filename = new_lookups_path / (new_lang_code + '_lemma_lookup.json.gz')
    srsly.write_gzip_json(lemma_filename, {})
    spacy_lookups_dir.symlink_to(lemma_filename)


def clone_lookups_data(lang_name,lang_code, spacy_language):
    #Slugify user input to prevent Python and os errors
    new_lang_name = slugify(lang_name).replace('-','_')
    new_lang_code = slugify(lang_code).replace('-','_')

    #Create a directory for the new language
    new_lang_path = (Path.cwd() / 'new_lang' / new_lang_name)
    new_lookups_path = new_lang_path / 'lookups'
    if not new_lookups_path.exists():
        new_lookups_path.mkdir(parents=True, exist_ok=True)

    #Identify spaCy language and directory to clone 
    spacy_languages = httpx.get('https://raw.githubusercontent.com/explosion/spaCy/8cc5ed6771010322954c2211b0e1f5a0fd14828a/website/meta/languages.json').json()
    spacy_code = [a['code'] for a in spacy_languages['languages'] if a['name'] == spacy_language][0]

    spacy_lookups_dir = Path(spacy_lookups_data.__file__.replace('__init__.py','')) / 'data'
    lookups_files = list(spacy_lookups_dir.glob(f'{spacy_code}*'))
    
    for src in lookups_files:
        dest = new_lookups_path / src.name.replace(spacy_code,new_lang_code)
        shutil.copyfile(src, dest)
        spacy_lookups_dir.symlink_to(dest)
