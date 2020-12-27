import spacy
import spacy_lookups_data
import shutil
import httpx
from pathlib import Path
from slugify import slugify
import subprocess
import sys
from typing import List


def clone_object(lang_name,lang_code, spacy_language):
    #Slugify user input to prevent Python and os errors
    new_lang_name = slugify(lang_name).replace('-','_')
    new_lang_code = slugify(lang_code).replace('-','_')

    #Create a directory for the new language
    new_lang_path = (Path.cwd() / 'new_lang' / new_lang_name)
    if new_lang_path.exists(): # TODO Revisit this choice, should we replace if exists? Users might not know this and delete an existing project.
        shutil.rmtree(new_lang_path)
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

    #Handle language exceptions
    if spacy_language == "Norwegian Bokmål":
        spacy_language = "Norwegian"
    if spacy_language == "Multi-language":
        spacy_language = "MultiLanguage"

    # Adjust imports and variable names (ex. GreekLemmatizer becomes AncientGreekLemmatizer)
    # This seems crazy, but spaCy is so consistent, I think it works
    new_files = [x for x in new_lang_path.glob('**/*') if x.is_file() and 'pyc' not in str(x)]
    for file in new_files:
        file_text = file.read_text()
        file_text = file_text.replace(spacy_language, new_lang_name.capitalize())
        file_text = file_text.replace('"'+spacy_code+'"','"'+new_lang_code+'"') # quotes added to avoid false matches
        file_text = file_text.replace('from ...', 'from spacy.')
        file_text = file_text.replace('from ..', 'from spacy.lang.')
        file.write_text(file_text)

    #Install language dependencies
    has_dependencies = get_dependencies(spacy_language,spacy_languages)
    if has_dependencies:
        for dep in has_dependencies:
            if dep['name'] == 'mecab-ko':
                install_mecab_ko()
            if dep['name'] == 'mecab-ko-dic':
                install_mecab_ko_dic()
            else:
                install(dep['name'])
           
    #copy spacy lookups data
    spacy_lookups = Path(spacy_lookups_data.__file__.replace('__init__.py','')) / 'data'
    assert spacy_lookups.exists(), "Spacy lookups  data not installed, please run pip install spacy[lookups] or pip install spacy-lookups-data"

    new_lookups = new_lang_path / 'lookups-data'
    new_lookups.mkdir(parents=True, exist_ok=True)
    lookups_files = [x for x in spacy_lookups.glob('**/*') if x.is_file() and spacy_code+'_' in str(x)]
    for src in lookups_files:
        new_name = src.name.replace(spacy_code, new_lang_code)
        dest = new_lookups / new_name
        shutil.copyfile(src, dest)

    return new_lang_name, new_lang_code


###               ##  
# Helper functions #
##                ##
def install(package):
    "Helper function to pip install from script: https://stackoverflow.com/questions/12332975/installing-python-module-within-code"
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def get_dependencies(spacy_language:str,spacy_languages:List):
    "Helper function to get language dependencies or return False if none."
    for i in range(len(spacy_languages['languages'])):
        if spacy_languages['languages'][i]['name'] == spacy_language:
            try:
                return spacy_languages['languages'][i]['dependencies']
            except KeyError: # Language does not have dependencies
                return False

def install_mecab_ko():
    pass
    # wget https://bitbucket.org/eunjeon/mecab-ko/downloads/mecab-0.996-ko-0.9.1.tar.gz
    # tar zxfv mecab-0.996-ko-0.9.1.tar.gz
    # cd mecab-0.996-ko-0.9.1
    # ./configure
    # make
    # make check
    # sudo make install

def install_mecab_ko_dic():
    """https://konlpy.org/en/v0.3.0/install/"""
    pass 
    # wget https://bitbucket.org/eunjeon/mecab-ko-dic/downloads/mecab-ko-dic-1.6.1-20140814.tar.gz
    # tar zxfv mecab-ko-dic-1.6.1-20140814.tar.gz
    # cd mecab-ko-dic-1.6.1-20140814
    # ./configure
    # sudo ldconfig
    # make
    # sudo sh -c 'echo "dicdir=/usr/local/lib/mecab/dic/mecab-ko-dic" > /usr/local/etc/mecabrc'
    # sudo make install