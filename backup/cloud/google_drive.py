import os
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from ..cloud.base_cloud import CloudProvider

class GoogleDriveProvider(CloudProvider):
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    
    def __init__(self):
        self.creds = None
        self.service = None
        self.token_path = Path('config/token.json')
        self.credentials_path = Path('config/credentials.json')

    def authenticate(self) -> bool:
        if self.token_path.exists():
            self.creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            with open(self.token_path, 'w') as token:
                token.write(self.creds.to_json())
        
        self.service = build('drive', 'v3', credentials=self.creds)
        return True

    def upload_file(self, file_path: Path):
        try:
            # Verificar permisos primero
            with open(file_path, 'rb') as test_file:
                test_file.read(100)  # Intentar leer una porción
                
            # Continuar con la subida...
            file_metadata = {'name': file_path.name}
            media = MediaFileUpload(file_path, chunksize=1024*1024, resumable=True)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            return file['id']
            
        except PermissionError:
            raise Exception(f"Sin permisos para leer: {file_path}")
        except Exception as e:
            raise Exception(f"Error al subir: {str(e)}")