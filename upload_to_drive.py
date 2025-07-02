from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import sys
import os


SCOPES = ['https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = '/usr/local/bin/service_account.json'
GD_FOLDER_ID = '1Q4q7P6bEYyT77h9mP0ZRCyALF2wAYKIw'


def upload_file(filepath):
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=credentials)

    file_metadata = {
        'name': os.path.basename(filepath),
        # Optional: specify parent folder ID
        'parents': [GD_FOLDER_ID]
    }
    media = MediaFileUpload(filepath, mimetype='application/gzip')
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    print(f"Uploaded file with ID: {file.get('id')}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python upload_to_drive.py <file_path>")
        sys.exit(1)

    upload_file(sys.argv[1])
