import srsly
from pathlib import Path
from typing import List, Optional, Set
from fastapi import Request, Form, File, APIRouter, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse,RedirectResponse

from app.util.login import get_current_username
from collections import Counter, namedtuple
from itertools import chain
from functools import lru_cache
import importlib
import shutil



templates = Jinja2Templates(directory="app/templates")

router = APIRouter(dependencies=[Depends(get_current_username)])


@router.get("/project")
async def project(request:Request):
    
    new_lang = Path.cwd() / "new_lang"
    if len(list(new_lang.iterdir())) > 0:
        return templates.TemplateResponse("project.html", {"request": request})
    else:
        return templates.TemplateResponse(
            "error_please_create.html", {"request": request}
        )


@router.get("/download_project")
async def download_project():
    """Package all files noted in the template. 
    1. original text files.
    2.  lookups for lemma, pos and features
    3. serialize your new spaCy language object
    4. a spaCy project file template

    Returns:
        FileResponse: project zip file
    """
    new_lang = Path.cwd() / "new_lang"
    lang_name = list(new_lang.iterdir())[0].name
    new_lang = new_lang / lang_name
    
    make_project()
    
    #make export directory 
    export_path = Path.cwd() / lang_name
    

    #shutil.make_archive("zipped_sample_directory", "zip", "sample_directory")
    shutil.make_archive(str(export_path), 'zip', str(new_lang))
    zip_file = Path.cwd() / (lang_name + '.zip')
    
    return FileResponse(str(zip_file), media_type="application/zip", filename=lang_name +'.zip')


def get_nlp():
    # Load language object as nlp
    new_lang = Path.cwd() / "new_lang"
    lang_name = list(new_lang.iterdir())[0].name
    mod = __import__(f"new_lang.{lang_name}", fromlist=[lang_name.capitalize()])
    cls = getattr(mod, lang_name.capitalize())
    nlp = cls()
    return nlp
    
        
    
def make_project():
    new_lang = Path.cwd() / "new_lang"
    if len(list(new_lang.iterdir())) > 0:
        lang_name = list(new_lang.iterdir())[0].name
        lookups_path = new_lang/ lang_name / "lookups"
        print(lookups_path,list(lookups_path.glob("*upos*")))
        json_file = list(lookups_path.glob("*upos*"))[0]
        lang_code = json_file.name.split('_')[0] 
        project_path = new_lang / lang_name / 'project.yml'
        project_path.write_text(
f"""
title: "New Language Project for Part-of-speech Tagging, Lemmatizer and Features from CoNLL-U data"
description: "This project template lets you train a part-of-speech tagger, lemmatizer and features from a [Universal Dependencies-style](https://universaldependencies.org/) corpus. It takes care of downloading the treebank, converting it to spaCy's format and training and evaluating the model. Just make sure to adjust the `lang` and treebank settings in the variables below."

# Variables can be referenced across the project.yml using ${{vars.var_name}}
vars:
  base_config: "base_config"
  lang: "{lang_code}"
  treebank: "{lang_name}"
  train_name: "{lang_code}_set-ud-train"
  dev_name: "{lang_code}_set-ud-dev"
  test_name: "{lang_code}_set-ud-test"
  package_name: "ud_{lang_code}_set"
  package_version: "0.0.0"
  gpu: -1

# These are the directories that the project needs. The project CLI will make
# sure that they always exist.
directories: ["assets", "corpus", "training", "metrics", "configs", "packages"]

assets:
  - dest: "assets/${{vars.treebank}}"
    git:
      repo: "https://github.com/New-Languages-for-NLP/${{vars.treebank}}"
      branch: "main"
      path: ""
  - dest: "assets/lookups"
    git:
      repo: "https://github.com/New-Languages-for-NLP/${{vars.treebank}}"
      branch: "main"
      path: "1_lookups_data/"
  - dest: "assets/tag_map"
    git:
      repo: "https://github.com/New-Languages-for-NLP/${{vars.treebank}}"
      branch: "master"
      path: "2_new_language_object"

workflows:
  all:
    - convert
    - install
    - train
    - evaluate
    - test_examples

commands:
  - name: install
    help: "Install {lang_name} lang files as package with entry point srp"
    script: 
      - "pip install -e 2_new_language_object/"
    deps:
      - "lang/{lang_name}/"

  - name: convert
    help: "Convert the data to spaCy's format"
    # Make sure we specify the branch in the command string, so that the
    # caching works correctly.
    script:
      - "mkdir -p corpus/${{vars.treebank}}"
      - "python -m spacy convert assets/${{vars.treebank}}/${{vars.train_name}}.conllu corpus/${{vars.treebank}}/ --converter conllu --n-sents 10 --merge-subtokens"
      - "python -m spacy convert assets/${{vars.treebank}}/${{vars.dev_name}}.conllu corpus/${{vars.treebank}}/ --converter conllu --n-sents 10 --merge-subtokens"
      - "python -m spacy convert assets/${{vars.treebank}}/${{vars.test_name}}.conllu corpus/${{vars.treebank}}/ --converter conllu --n-sents 10 --merge-subtokens"
      - "mv corpus/${{vars.treebank}}/${{vars.train_name}}.spacy corpus/${{vars.treebank}}/train.spacy"
      - "mv corpus/${{vars.treebank}}/${{vars.dev_name}}.spacy corpus/${{vars.treebank}}/dev.spacy"
      - "mv corpus/${{vars.treebank}}/${{vars.test_name}}.spacy corpus/${{vars.treebank}}/test.spacy"
    deps:
      - "assets/${{vars.treebank}}/${{vars.train_name}}.conllu"
      - "assets/${{vars.treebank}}/${{vars.dev_name}}.conllu"
      - "assets/${{vars.treebank}}/${{vars.test_name}}.conllu"
    outputs:
      - "corpus/${{vars.treebank}}/train.spacy"
      - "corpus/${{vars.treebank}}/dev.spacy"
      - "corpus/${{vars.treebank}}/test.spacy"

  - name: train
    help: "Train ${{vars.treebank}}"
    script:
      - "spacy init fill-config configs/${{vars.base_config}}.cfg configs/config.cfg"
      - "spacy train configs/config.cfg --output training"
    deps:
      - "corpus/${{vars.treebank}}/train.spacy"
      - "corpus/${{vars.treebank}}/dev.spacy"
      - "configs/${{vars.base_config}}.cfg"
    outputs:
      - "training/${{vars.treebank}}/model-best"

  - name: evaluate
    help: "Evaluate on the test data and save the metrics"
    script:
      - "python -m spacy evaluate ./training/model-best ./corpus/${{vars.treebank}}/test.spacy --output ./metrics/${{vars.treebank}}.json --gpu-id ${{vars.gpu}}"
    deps:
      - "training/model-best"
      - "corpus/${{vars.treebank}}/test.spacy"
    outputs:
      - "metrics/${{vars.treebank}}.json"

  - name: test_examples
    help: "test an example document and show model output"
    script:
      - "python scripts/test_examples.py"
    deps:
      - "training/model-best"

  - name: clean
    help: "Remove intermediate files"
    script:
      - "rm -rf training/*"
      - "rm -rf metrics/*"
      - "rm -rf corpus/*"    
""")
