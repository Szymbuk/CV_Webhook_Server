import requests

def fetch_pending_cv():
    headers = {"API-Key":"D17lore"}
    result = requests.get("http://13.60.27.31:8000/waiting-cv/",headers=headers)
    data = result.json()
    print(data,"\n\n\n")
    for response in data:
        print("e-mail:",response['email'])
        print("cv:",response['cv_link'])
        print("video:",response['video_link'])
        print("status:",response['status'],"\n\n")


fetch_pending_cv()
