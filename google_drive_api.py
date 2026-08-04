"""
Google Drive API Integration
Pulls documents and images from Google Drive for blog content
"""

import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from io import BytesIO
from dotenv import load_dotenv

import paths

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
TOKEN_FILE = paths.GOOGLE_DRIVE_TOKEN
CREDENTIALS_FILE = 'google_drive_credentials.json'

class GoogleDriveClient:
    def __init__(self):
        self.service = None
        self.authenticate()

    def _creds_from_env(self):
        """Credentials from env vars, for headless/deployed runs. See the
        matching helper in google_photos_api.py."""
        refresh_token = os.getenv('GOOGLE_DRIVE_REFRESH_TOKEN')
        client_id = os.getenv('GOOGLE_OAUTH_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET')

        if not all([refresh_token, client_id, client_secret]):
            return None

        creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            client_id=client_id,
            client_secret=client_secret,
            scopes=SCOPES,
        )
        creds.refresh(Request())
        return creds

    def authenticate(self):
        """Authenticate with Google Drive API"""
        creds = self._creds_from_env()
        if creds:
            self.service = build('drive', 'v3', credentials=creds)
            print("✅ Google Drive authenticated (refresh token)")
            return

        creds = None
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if os.getenv('HEADLESS') or not os.path.exists(CREDENTIALS_FILE):
                    raise RuntimeError(
                        "No Google Drive credentials available. On a server, set "
                        "GOOGLE_DRIVE_REFRESH_TOKEN, GOOGLE_OAUTH_CLIENT_ID and "
                        "GOOGLE_OAUTH_CLIENT_SECRET (run get_refresh_token.py locally)."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)

            with open(TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('drive', 'v3', credentials=creds)
        print("✅ Google Drive authenticated")

    def get_folder_contents(self, folder_name='Los Iconos Blogs'):
        """Get documents from a specific folder"""
        try:
            # Find folder by name
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)',
                pageSize=10
            ).execute()

            folders = results.get('files', [])
            if not folders:
                print(f"❌ Folder '{folder_name}' not found")
                return []

            folder_id = folders[0]['id']

            # Get files in folder
            query = f"'{folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, mimeType, createdTime, modifiedTime)',
                orderBy='createdTime',
                pageSize=100
            ).execute()

            files = results.get('files', [])
            return files

        except Exception as e:
            print(f"❌ Error fetching folder contents: {e}")
            return []

    def get_document_content(self, file_id):
        """Get content from a Google Docs document"""
        try:
            # Export as plain text
            request = self.service.files().export_media(
                fileId=file_id,
                mimeType='text/plain'
            )
            file_content = request.execute()
            return file_content.decode('utf-8')
        except Exception as e:
            print(f"❌ Error fetching document: {e}")
            return ""

    def get_file_metadata(self, file_id):
        """Get metadata for a file"""
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields='id, name, mimeType, webViewLink, createdTime'
            ).execute()
            return file
        except Exception as e:
            print(f"❌ Error fetching metadata: {e}")
            return None

    def list_all_documents(self):
        """List all documents, oldest first"""
        try:
            query = "trashed=false and (mimeType='application/vnd.google-apps.document' or mimeType='application/vnd.google-apps.spreadsheet')"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, mimeType, createdTime)',
                orderBy='createdTime',
                pageSize=100
            ).execute()

            files = results.get('files', [])
            return files
        except Exception as e:
            print(f"❌ Error listing documents: {e}")
            return []

if __name__ == "__main__":
    client = GoogleDriveClient()
    docs = client.list_all_documents()
    print(f"Found {len(docs)} documents")
    for doc in docs[:5]:
        print(f"  - {doc['name']} ({doc['createdTime']})")
