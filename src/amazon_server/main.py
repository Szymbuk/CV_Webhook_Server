from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Header
from fastapi.params import Depends
from dotenv import load_dotenv
import os

import crud
from forms_schema import FormsCV, StatusChangeList
from shared.pdf_coversion import save_bytes_as_pdf,get_bytes_from_pdf

waiting = 'waiting'
sent = 'sent'
pending = 'pending'
finished = 'finished'


@asynccontextmanager
async def lifespan(app: FastAPI):
    # code at the start of the server
    print("Launching server...")
    crud.create_tables()
    yield
    # code while shutting down the server
    print("Server is shutting down...")


app = FastAPI(lifespan=lifespan)

load_dotenv()
API_KEY_DEBUG = os.getenv("API_KEY_DEBUG")
API_KEY = os.getenv("API_KEY")
CV_DIRECTORY = os.getenv("CV_DIRECTORY")


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
    path = save_bytes_as_pdf(CV_DIRECTORY,cv.cv,cv.cv_name)
    cv.cv = path
    crud.add_forms(cv)
    print("CV was added to database.")
    return {"response": "Successfully added cv to database"}


@app.get("/send-waiting-cv")
def send_waiting_cv(ids: StatusChangeList, key: str = Depends(key_validation)):
    data = crud.change_from_to(waiting,sent, cv_ids=ids.cv_ids)
    for cv_dict in data:
        path = cv_dict["cv"]
        pdf_b64 = get_bytes_from_pdf(path)
        cv_dict["cv"] = pdf_b64
    if not data:
        print("no CV found")
        return {"response": "no CV found"}
    print("Data sent successfully")
    return data


@app.post("/change-waiting")
def change_set_to_waiting(ids: StatusChangeList,key: str = Depends(key_validation)):
    crud.change_from_to(sent,waiting, cv_ids=ids.cv_ids)
    print("Changed CVs to waiting.")
    return {"response": "Successfully changed sent CVs to waiting"}


@app.post("/change-pending")
def change_to_pending(ids: StatusChangeList,key: str = Depends(key_validation)):
    crud.change_from_to(sent,pending, cv_ids=ids.cv_ids)
    print("Changed CVs to pending.")
    return {"response": "Successfully changed sent CVs to pending"}


@app.post("/change-finished")
def change_to_finished(ids: StatusChangeList, key: str = Depends(key_validation)):
    crud.change_from_to(pending,finished, cv_ids=ids.cv_ids)
    print("Changed CVs to finished.")
    return {"response": "Successfully changed sent CVs to finished"}


@app.post("/delete-finished")
def delete_finished(key: str = Depends(key_validation)):
    crud.delete_finished()
    print("Deleted finished CVs.")
    return {"response": "Successfully deleted finished CVs"}


@app.get("/print-data_new")
def print_database(key: str = Depends(key_validation_debug)):
    data = crud.read_database()
    print(f"Database records:\n {data}")
    return data
