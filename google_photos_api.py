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

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']
TOKEN_FILE = 'google_photos_token.pickle'
CREDENTIALS_FILE = 'google_photos_credentials.json'

class GooglePhotosClient:
    def __init__(self):
        self.service = None
        self.creds = None
        self.authenticate()

    def authenticate(self):
        """Authenticate with Google Photos API"""
        creds = None

        # Load saved credentials
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)

        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save credentials
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
