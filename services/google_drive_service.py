import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def get_drive_service():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            except FileNotFoundError:
                return None, "credentials.json not found. Please create it and try again."
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("drive", "v3", credentials=creds)
        return service, None
    except HttpError as error:
        return None, f"An error occurred: {error}"


def upload_file_to_drive(file_path, folder_name="GPT Researcher Reports"):
    """Uploads a file to a specific folder in Google Drive.
    """
    service, error = get_drive_service()
    if error:
        return None, error
    if not service:
        return None, "Failed to connect to Google Drive."

    try:
        # Search for the folder
        response = (
            service.files()
            .list(
                q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
                spaces="drive",
                fields="nextPageToken, files(id, name)",
            )
            .execute()
        )
        if not response["files"]:
            # Create the folder if it doesn't exist
            file_metadata = {
                "name": folder_name,
                "mimeType": "application/vnd.google-apps.folder",
            }
            file = service.files().create(body=file_metadata, fields="id").execute()
            folder_id = file.get("id")
        else:
            folder_id = response["files"][0].get("id")

        # Upload the file
        file_metadata = {"name": os.path.basename(file_path), "parents": [folder_id]}
        media = MediaFileUpload(file_path)
        file = (
            service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )
        return file.get("id"), None

    except HttpError as error:
        return None, f"An error occurred: {error}"
