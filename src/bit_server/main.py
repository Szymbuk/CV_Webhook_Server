import base64
import sqlite3

from dotenv import load_dotenv
import requests
import os

import crud

load_dotenv()
EC2_URL = os.getenv("EC2_URL")
API_KEY = os.getenv("API_KEY")
from src.bit_server import database


def create_database():
    database.create_tables()

def fetch_waiting_cv():
    headers = {"API-Key":API_KEY}
    result = requests.get(f"{EC2_URL}/waiting-cv/",headers=headers)
    data = result.json()
    try:
        for response in data:
            crud.add_row(response['email'],response['cv_name'],response['cv_file'])
        requests.post(f"{EC2_URL}/delete-given",headers=headers)
    except sqlite3.Error as e:

        print("Database Error")
        print(e)
        # TODO: implement requests.post(f"{EC2_URL}/change-waiting")



def save_bytes_as_pdf(path,bytes_file,file_name):
    pdf = base64.b64decode(bytes_file)
    with  open(f"{path}/{file_name}.pdf", "wb") as f:
        f.write(pdf)


def get_pdf_from_bytes(bytes_file):
    return base64.b64decode(bytes_file)

fetch_waiting_cv()
