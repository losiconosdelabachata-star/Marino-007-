"""
Google Photos API Integration
Pulls photos chronologically from Google Photos albums
"""

import os
import sys
import pickle
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv

import paths

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']
TOKEN_FILE = paths.GOOGLE_PHOTOS_TOKEN
CREDENTIALS_FILE = 'google_photos_credentials.json'

class GooglePhotosClient:
    def __init__(self):
        self.service = None
        self.creds = None
        self.authenticate()

    def _creds_from_env(self):
        """Build credentials from env vars, for headless/deployed runs.

        A server has no browser, so the interactive consent flow can never
        complete there. Supplying a refresh token lets it mint access tokens
        on its own. Generate one locally with get_refresh_token.py.
        """
        refresh_token = os.getenv('GOOGLE_PHOTOS_REFRESH_TOKEN')
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
        """Authenticate with Google Photos API"""
        # Env credentials win, so a deploy never depends on a cached file.
        creds = self._creds_from_env()
        if creds:
            self.creds = creds
            print("✅ Google Photos authenticated (refresh token)")
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
                        "No Google Photos credentials available. On a server, set "
                        "GOOGLE_PHOTOS_REFRESH_TOKEN, GOOGLE_OAUTH_CLIENT_ID and "
                        "GOOGLE_OAUTH_CLIENT_SECRET (run get_refresh_token.py locally)."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)

            with open(TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)

        self.creds = creds
        print("✅ Google Photos authenticated")

    def get_all_photos(self, limit=100):
        """Get all photos from Google Photos, oldest first"""
        try:
            headers = {
                'Authorization': f'Bearer {self.creds.token}'
            }

            url = 'https://photoslibrary.googleapis.com/v1/mediaItems'

            params = {
                'pageSize': min(limit, 100)
            }

            response = requests.get(url, headers=headers, params=params)

            if response.status_code != 200:
                print(f"❌ API error: {response.status_code}")
                return []

            data = response.json()
            media_items = data.get('mediaItems', [])

            # Sort by creation time (oldest first)
            media_items.sort(key=lambda x: x.get('mediaMetadata', {}).get('creationTime', ''))

            photos = []
            for item in media_items[:limit]:
                photos.append({
                    'id': item.get('id'),
                    'filename': item.get('filename'),
                    'url': item.get('baseUrl'),
                    'created_time': item.get('mediaMetadata', {}).get('creationTime'),
                    'description': item.get('description', '')
                })

            return photos

        except Exception as e:
            print(f"❌ Error fetching photos: {e}")
            return []

    def get_albums(self):
        """Get all albums from Google Photos"""
        try:
            headers = {
                'Authorization': f'Bearer {self.creds.token}'
            }

            url = 'https://photoslibrary.googleapis.com/v1/albums'
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                return []

            data = response.json()
            albums = []

            for album in data.get('albums', []):
                albums.append({
                    'id': album.get('id'),
                    'title': album.get('title'),
                    'media_items_count': album.get('mediaItemsCount', 0)
                })

            return albums

        except Exception as e:
            print(f"❌ Error fetching albums: {e}")
            return []

    def get_photos_from_album(self, album_id, limit=50):
        """Get photos from a specific album, oldest first"""
        try:
            headers = {
                'Authorization': f'Bearer {self.creds.token}',
                'Content-Type': 'application/json'
            }

            url = 'https://photoslibrary.googleapis.com/v1/mediaItems:search'

            body = {
                'albumId': album_id,
                'pageSize': min(limit, 100)
            }

            response = requests.post(url, headers=headers, json=body)

            if response.status_code != 200:
                return []

            data = response.json()
            media_items = data.get('mediaItems', [])

            # Sort by creation time (oldest first)
            media_items.sort(key=lambda x: x.get('mediaMetadata', {}).get('creationTime', ''))

            photos = []
            for item in media_items[:limit]:
                photos.append({
                    'id': item.get('id'),
                    'filename': item.get('filename'),
                    'url': item.get('baseUrl'),
                    'created_time': item.get('mediaMetadata', {}).get('creationTime'),
                    'description': item.get('description', '')
                })

            return photos

        except Exception as e:
            print(f"❌ Error fetching album photos: {e}")
            return []


if __name__ == "__main__":
    client = GooglePhotosClient()
    albums = client.get_albums()
    print(f"Found {len(albums)} albums")

    photos = client.get_all_photos(limit=10)
    print(f"Found {len(photos)} photos")
    for photo in photos:
        print(f"  - {photo['filename']} ({photo['created_time']})")
