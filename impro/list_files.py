# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
import os.path
import json
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from oauth2client import file
from dotenv import load_dotenv

load_dotenv()
parent_id = os.getenv('parent_id')

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

def get_credentials():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
    
    #Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
    return creds


def main():
    """Lists file names in "Cours" together with their id"
    """
    creds = get_credentials()

    service = build('drive', 'v3', credentials=creds)

    # Call the Drive v3 API
    page_token = None
    list_files = {}
    while True: 
        response = service.files().list(q="'" + parent_id + "'  in parents and trashed=false",
                                           spaces='drive',
                                           fields='nextPageToken, files(id, name)',
                                           pageToken=page_token).execute()
        
        for item in response.get('files', []):
            item_id = item.get('id')
            document = service.files().get(fileId=item_id).execute()
            if document['mimeType']=='application/vnd.google-apps.document':
                list_files[item_id] = item.get('name')
  
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    
    with open('list_files.json', 'w') as f:
        list_files = json.dumps(list_files)
        f.write(list_files)



if __name__ == '__main__':
    main()