from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Header
from fastapi.params import Depends
from dotenv import load_dotenv
import os

import crud
from schemas import FormsCV, BaseCV
import database


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

# @app.post("/webhook_prev")
# def upload_forms_data(cv: FormsCV, key: str = Depends(key_validation)):
#     crud.add_forms(cv.email, cv.cv_name, cv.cv_content)
#     print("CV was added to database.")
#     return {"response": "Successfully added cv to database"}
#
# @app.get("/waiting-cv")
# def get_waiting_cv(key: str = Depends(key_validation)):
#     data = crud.give_waiting()
#     print(data)
#     if not data:
#         return {"response": "no CV found"}
#     return data
#
#
# @app.post("/delete-given")
# def delete_sent_cv(key: str = Depends(key_validation)):
#     crud.delete_sent()
#     print("Deleted sent CVs.")
#     return {"response": "Successfully deleted sent CVs"}
#
#
# @app.post("/change-waiting")
# def change_set_to_waiting(key: str = Depends(key_validation)):
#     crud.change_to_waiting()
#     print("Changed CV's to waiting.")
#     return {"response": "Successfully changed sent CVs to waiting"}
#
#
# @app.get("/print-data")
# def print_database(key: str = Depends(key_validation_debug)):
#     data =  crud.read_database()
#     print(f"Database records:\n {data}")
#     return data


from pdf_coversion import save_bytes_as_pdf,get_bytes_from_pdf
waiting = 'waiting'
sent = 'sent'
pending = 'pending'
finished = 'finished'


@app.post("/webhook")
def upload_forms_data(cv: BaseCV, key: str = Depends(key_validation)):
    path = save_bytes_as_pdf(CV_DIRECTORY,cv.cv,cv.cv_name)
    cv.cv = path


    crud.add_forms_new(cv)
    print("CV was added to database.")
    return {"response": "Successfully added cv to database"}


@app.get("/send-waiting-cv")
def send_waiting_cv(key: str = Depends(key_validation)):
    data = crud.change_from_to(waiting,sent)
    for cv_dict in data:
        path = cv_dict["cv"]
        pdf_b64 = get_bytes_from_pdf(path)
        cv_dict["cv"] = pdf_b64
    print(data)
    if not data:
        return {"response": "no CV found"}
    return data


@app.post("/change-waiting_new")
def change_set_to_waiting(key: str = Depends(key_validation)):
    crud.change_from_to(sent,waiting)
    print("Changed CVs to waiting.")
    return {"response": "Successfully changed sent CVs to waiting"}


@app.post("/change-pending")
def change_set_to_waiting(key: str = Depends(key_validation)):
    crud.change_from_to(sent,pending)
    print("Changed CVs to pending.")
    return {"response": "Successfully changed sent CVs to pending"}


@app.post("/change-finished")
def change_set_to_waiting(key: str = Depends(key_validation)):
    crud.change_from_to(pending,finished)
    print("Changed CVs to finished.")
    return {"response": "Successfully changed sent CVs to finished"}


@app.post("/delete-finished")
def delete_sent_cv(key: str = Depends(key_validation)):
    crud.delete_finished()
    print("Deleted finished CVs.")
    return {"response": "Successfully deleted finished CVs"}


@app.get("/print-data_new")
def print_database(key: str = Depends(key_validation_debug)):
    data =  crud.read_database_new()
    print(f"Database records:\n {data}")
    return data
