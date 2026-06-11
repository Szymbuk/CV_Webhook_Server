import sqlite3
from dotenv import load_dotenv
import requests
import os
from shared.pdf_coversion import save_bytes_as_pdf
from shared.base_schemas import BaseCV

import bit_server.crud as crud

load_dotenv()
EC2_URL = os.getenv("EC2_URL")
API_KEY = os.getenv("API_KEY")
CV_DIRECTORY = os.getenv("CV_DIRECTORY")


def fetch_waiting_cv():
    headers = {"API-Key":API_KEY}
    result = requests.get(f"{EC2_URL}send-waiting-cv",headers=headers)
    if result.status_code == 200:
        data = result.json()
        if data == {"response": "no CV found"}:
            print("There are no new CVs to be saved.",end="\t")
            return
        
        successful_ids = []
        failed_ids = []
        
        for cv in data:
            try:
                amazon_id = cv.pop("id")
                cv.pop("status")
                cv = BaseCV.model_validate(cv)
                
                path = save_bytes_as_pdf(CV_DIRECTORY,cv.cv,cv.cv_name)
                cv.cv = path
                crud.add_to_db(cv)
                successful_ids.append(amazon_id)
            except sqlite3.Error as e:
                print("Database Error",end="\t")
                print(e,end="\t")
                failed_ids.append(amazon_id)
        if successful_ids:
            print(f"Successfully added CVs with ids: {successful_ids}",end="\t")
            requests.post(f"{EC2_URL}change-pending", json={"cv_ids": successful_ids}, headers=headers)
        if failed_ids:
            print(f"Failed to add CVs with ids: {failed_ids}",end="\t")    
            requests.post(f"{EC2_URL}change-waiting", json={"cv_ids": failed_ids}, headers=headers)
    else:
        print(f"Failed to connect to the server: {result.status_code}",end="\t")

if __name__ == "__main__":
    crud.create_tables()
    fetch_waiting_cv()
    print(crud.read_database())
