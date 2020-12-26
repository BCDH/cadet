import spacy
import spacy_lookups_data
import shutil
import httpx
from pathlib import Path
from slugify import slugify


def clone_object(lang_name,lang_code, spacy_language):
    #Slugify user input to prevent Python and os errors
    new_lang_name = slugify(lang_name)
    new_lang_code = slugify(lang_code)

    #Create a directory for the new language
    new_lang_path = (Path.cwd() / 'new_lang' / new_lang_name)
    new_lang_path.mkdir(parents=True, exist_ok=True)

    #Identify spaCy language and directory to clone 
    spacy_languages = httpx.get('https://raw.githubusercontent.com/explosion/spaCy/8cc5ed6771010322954c2211b0e1f5a0fd14828a/website/meta/languages.json').json()
    spacy_code = [a['code'] for a in spacy_languages['languages'] if a['name'] == spacy_language][0]
    spacy_lang_path = Path(spacy.__file__.replace('__init__.py','')) / 'lang' / spacy_code
    assert spacy_lang_path.exists(), "spaCy lang directory not found, please install spaCy or check version"

    # copy files from spacy.lang to new_lang directory
    core_files = [x for x in spacy_lang_path.glob('**/*') if x.is_file() and 'pyc' not in str(x)]
    for src in core_files:
        dest = new_lang_path / src.name
        shutil.copyfile(src, dest)

    # Adjust imports and variable names for all other files
    new_files = [x for x in new_lang_path.glob('**/*') if x.is_file() and 'pyc' not in str(x)]
    for file in new_files:
        file_text = file.read_text()
        # DEBUG replace statements not working 
        file_text = file_text.replace(spacy_language, new_lang_name.capitalize()).replace('"'+spacy_code+'"','"'+new_lang_code+'"') # quotes added to avoid false matches
        file_text = file.read_text()
        file_text = file_text.replace('from ...', 'from spacy.')
        file_text = file_text.replace('from ..', 'from spacy.lang.')
        file.write_text(file_text)

    # TODO confirm language dependencies are installed 

    #spacy lookups ~ using pip install spacy[lookups]
    spacy_lookups = Path(spacy_lookups_data.__file__.replace('__init__.py','')) / 'data'
    assert spacy_lookups.exists(), "Spacy lookups  data not installed, please run pip install spacy[lookups] or pip install spacy-lookups-data"

    # Use the iso code to identify lookups-data files
    new_lookups = new_lang_path / 'lookups-data'
    new_lookups.mkdir(parents=True, exist_ok=True)
    lookups_files = [x for x in spacy_lookups.glob('**/*') if x.is_file() and spacy_code+'_' in str(x)]
    for src in lookups_files:
        new_name = src.name.replace(spacy_code, new_lang_code)
        dest = new_lookups / new_name
        shutil.copyfile(src, dest)

    return new_lang_name, new_lang_code