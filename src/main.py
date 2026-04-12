from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Header
from fastapi.security import APIKeyHeader
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
API_KEY_WEBHOOK = os.getenv("API_KEY_WEBHOOK")
API_KEY_GET_CV = os.getenv("API_KEY_GET_CV")

api_key_header_webhook = APIKeyHeader(name="API-Key")
api_key_header_get_cv = APIKeyHeader(name="API-Key")

def key_validation_webhook(api_key: str = Header("API-Key")):
    if api_key != API_KEY_WEBHOOK:
        raise HTTPException(status_code=401,detail= "Incorrect API key.")
    return api_key


def key_validation_get_cv(api_key: str = Header("API-Key")):
    if api_key != API_KEY_GET_CV:
        raise HTTPException(status_code=401,detail= "Incorrect API key.")
    return api_key

@app.post("/webhook")
def upload_forms_data(cv: FormsCV, key: str = Depends(key_validation_webhook)):
    crud.add_forms(cv.email, cv.cv_link, cv.video_link)
    print("SUCCESS! CV was added to database.")
    return {"response": "Successfully added cv to database"}

@app.get("/waiting-cv")
def get_waiting_cv(key: str = Depends(key_validation_get_cv)):
    data = crud.give_waiting_change_to_pending()
    if not data:
        return {"message": "No CV waiting for process" }
    return data


@app.get("/print-data")
def print_database():
    return crud.read_database()
