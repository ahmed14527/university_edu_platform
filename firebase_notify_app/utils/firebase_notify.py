import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from django.conf import settings

SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']

credentials = service_account.Credentials.from_service_account_file(
    settings.FIREBASE_SERVICE_ACCOUNT_FILE,
    scopes=SCOPES
)

def get_access_token():
    request = Request()
    credentials.refresh(request)
    return credentials.token

def send_firebase_notification(token, title, body, data=None):
    access_token = get_access_token()
    project_id = credentials.project_id

    url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"

    message = {
        "message": {
            "token": token,
            "notification": {
                "title": title,
                "body": body
            },
            "data": data or {}
        }
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; UTF-8"
    }

    response = requests.post(url, headers=headers, json=message)
    return response.json()
