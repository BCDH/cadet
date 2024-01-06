import os
import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()
try:
    env_username = os.environ["CADET_USERNAME"]
except KeyError:
    env_username = b"cadet"
try:
    env_password = os.environ["CADET_PASSWORD"]
except KeyError:
    env_password = b"NewNLP"


def get_current_username(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = env_username
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = env_password
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def logout(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "")
    correct_password = secrets.compare_digest(credentials.password, "")
    if not (correct_username and correct_password):
        return templates.TemplateResponse("login.html", {"request": request})
    return credentials.username
