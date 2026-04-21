import base64
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Header
#from fastapi.security import APIKeyHeader
from fastapi.params import Depends

from dotenv import load_dotenv

import os

import crud
from schemas import FormsCV
import database



@asynccontextmanager
async def lifespan(app: FastAPI):
    # code at the start of the server
    print("Launching server...")
    database.create_tables()
    yield
    # code while shutting down the server
    print("Server is shutting down...")

app = FastAPI(lifespan=lifespan)

load_dotenv()
API_KEY_DEBUG = os.getenv("API_KEY_DEBUG")
API_KEY = os.getenv("API_KEY")

#api_key_header_webhook = APIKeyHeader(name="API-Key")
#api_key_header_get_cv = APIKeyHeader(name="API-Key")

def key_validation_debug(api_key: str = Header("API-Key")):
    if api_key != API_KEY_DEBUG:
        raise HTTPException(status_code=401,detail= "Incorrect API key.")
    return api_key


def key_validation(api_key: str = Header("API-Key")):
    if api_key != API_KEY:
        raise HTTPException(status_code=401,detail= "Incorrect API key.")
    return api_key

@app.post("/webhook")
def upload_forms_data(cv: FormsCV, key: str = Depends(key_validation)):
    crud.add_forms(cv.email, cv.cv_name, cv.cv_content)
    print("SUCCESS! CV was added to database.")
    return {"response": "Successfully added cv to database"}

@app.get("/waiting-cv")
def get_waiting_cv(key: str = Depends(key_validation)):
    data = crud.give_waiting()
    if not data:
        raise HTTPException(status_code=404, detail="CV nie znalezione")
    return data


@app.post("/delete-given")
def delete_sent_cv(key: str = Depends(key_validation)):
    crud.delete()
    return {"response": "Successfully deleted sent cv's"}



@app.get("/print-data")
def print_database(key: str = Depends(key_validation_debug)):
    return crud.read_database()
