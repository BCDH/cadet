import httpx
import string
import random
from fastapi.testclient import TestClient
from pathlib import Path
from app.main import app

client = TestClient(app)


def test_read_open():
    response = client.get("/")
    assert response.status_code == 200


def test_read_main_no_password():
    response = client.get("/main")
    assert response.status_code == 401


def test_create_language():
    pass
    # assert that works with various problems


def test_clone_language():
    from app.util.clone_object import clone_object

    spacy_languages = httpx.get(
        "https://raw.githubusercontent.com/explosion/spaCy/8cc5ed6771010322954c2211b0e1f5a0fd14828a/website/meta/languages.json"
    ).json()
    spacy_languages = [a["name"] for a in spacy_languages["languages"]]

    for language in spacy_languages:
        if language == "Macedonian" or language == "Korean":
            # Macedonian is listed as a supported language, but there is no mk in spacy.lang in nightly (will probably be added)
            # Korean has dependencies that require sudo to compile
            continue
        else:
            print(f"[*] Running test, clone language({language})")
            lang_name = "".join(random.choices(string.ascii_letters, k=5))
            lang_code = "".join(random.choices(string.ascii_letters, k=3))

            new_lang_name, new_lang_code = clone_object(lang_name, lang_code, language)
            assert (Path.cwd() / "new_lang" / new_lang_name).exists()
            assert (Path.cwd() / "new_lang" / new_lang_name / "__init__.py").exists()
            assert (
                f"class {new_lang_name.capitalize()}(Language)"
                in (Path.cwd() / "new_lang" / new_lang_name / "__init__.py").read_text()
            )
