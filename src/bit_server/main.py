import sqlite3
from dotenv import load_dotenv
import requests
import os

import crud
import database

load_dotenv()
EC2_URL = os.getenv("EC2_URL")
API_KEY = os.getenv("API_KEY")


def create_database():
    database.create_tables()


def fetch_waiting_cv():
    headers = {"API-Key":API_KEY}
    result = requests.get(f"{EC2_URL}waiting-cv",headers=headers)
    if result.status_code == 200:
        data = result.json()
        if data == {"response": "no CV found"}:
            print("There are no new CVs to be saved")
        try:
            for response in data:
                crud.add_row(response['email'],response['cv_name'],response['cv_file'])
            requests.post(f"{EC2_URL}delete-given",headers=headers)
        except sqlite3.Error as e:

            print("Database Error")
            print(e)
            requests.post(f"{EC2_URL}change-waiting")
    else:
        print(f"Failed to connect to the server: {result.status_code}")

if __name__ == "__main__":
    create_database()
    fetch_waiting_cv()
