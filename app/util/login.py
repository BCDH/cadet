import os
import secrets
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()
try:
    env_username = os.environ['CADET_USERNAME']
except KeyError:
    env_username = 'cadet'
try:
    env_password = os.environ['CADET_PASSWORD']
except  KeyError:
    env_password = 'NewNLP'

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, env_username)
    correct_password = secrets.compare_digest(credentials.password, env_password)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
