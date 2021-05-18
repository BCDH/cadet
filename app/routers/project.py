import srsly
from pathlib import Path
from typing import List, Optional, Set
from fastapi import Request, Form, File, APIRouter, Depends
from fastapi.templating import Jinja2Templates
from app.util.login import get_current_username
from collections import Counter, namedtuple
from itertools import chain
from functools import lru_cache
import importlib
from github import Github, GithubException
from github import InputGitTreeElement



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

def get_lang_name():
    new_lang = Path.cwd() / "new_lang"
    if len(list(new_lang.iterdir())) > 0:
        return list(new_lang.iterdir())[0].name

@router.post("/project")
async def form_post(
    request: Request,
    token:str = Form(None),
    organization:str = Form(None),
    repository:str = Form(None),
):
    g = Github(token)

    #get_user works for both user or organization
    try:
        repo = g.get_user(organization).get_repo(repository) # repo name
    except GithubException as e:
        if e._GithubException__data['message'] == 'Not Found':
            org = g.get_organization(organization)
            repo = org.create_repo(repository.strip()) 
            #TODO actually want from a template https://docs.github.com/en/rest/reference/repos#create-a-repository-using-a-template            
        else:
            return templates.TemplateResponse("project.html", {"request": request, "message":e._GithubException__data['message']})
    return templates.TemplateResponse("project.html", {"request": request, })
    # all_files = []
    # contents = repo.get_contents("")
    # while contents:
    #     file_content = contents.pop(0)
    #     if file_content.type == "dir":
    #         contents.extend(repo.get_contents(file_content.path))
    #     else:
    #         file = file_content
    #         all_files.append(str(file).replace('ContentFile(path="','').replace('")',''))

    # with open('/tmp/file.txt', 'r') as file:
    #     content = file.read()

    # # Upload to github
    # git_prefix = 'folder1/'
    # git_file = git_prefix + 'file.txt'
    # if git_file in all_files:
    #     contents = repo.get_contents(git_file)
    #     repo.update_file(contents.path, "committing files", content, contents.sha, branch="master")
    #     print(git_file + ' UPDATED')
    # else:
    #     repo.create_file(git_file, "committing files", content, branch="master")
    #     print(git_file + ' CREATED')

    #message = f"Successfully uploaded files. <a target='_blank' href='https://github.com/{username}/{repository}'>Click here to proceed to GitHub.</a>"
    #return templates.TemplateResponse("project.html", {"request": request, "message":message})