from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from fastapi.staticfiles import StaticFiles
from pathlib import Path
app_dir = Path.cwd()
templates = Jinja2Templates(directory="app/templates")

app = FastAPI()
app.mount('/static', StaticFiles(directory='./app/static'), name='static')

PASSWORD = 'fishandchips'


#app.include_router(home.router)
#app.include_router(weather_app.router)

#routers
# social authentication 
# load/connect to corpus, get seeds for annotation, create initial ling data
# create language object
# create config.cfg and train
# project.yml
# create model 
# load texts and data 
# 

# 1 Create basic language object
# 2 Create basic model with pipelines
# 3 Create custom model with transformers, pytorch models, and so on

@app.get("/")
def root(request: Request, ):
   
    return templates.TemplateResponse("index.html", {"request": request, "time": datetime.now() })

from fastapi import FastAPI, File, Form, UploadFile

@app.post("/")
def login(request: Request, password: str = Form(...)):
        
    if password == PASSWORD: 
        
        return templates.TemplateResponse("index.html", {"request": request, })
    else:
        message = "Please try again"
        return templates.TemplateResponse("index.html", {"request": request, "message": message })
