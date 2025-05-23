import logging
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

logging.basicConfig(level=logging.INFO)

class Uploader:
    def __init__(self, creds_path, token_path, retries=3):
        self.scopes = ["https://www.googleapis.com/auth/youtube.upload"]
        self.retries = retries
        self.youtube = self._authenticate(creds_path)

    def _authenticate(self, creds_path):
        flow = InstalledAppFlow.from_client_secrets_file(creds_path, self.scopes)
        creds = flow.run_console()
        return build("youtube", "v3", credentials=creds)

    def upload(self, file_path, metadata):
        media = MediaFileUpload(file_path, resumable=True)
        body = {
            "snippet": {
                "title": metadata["title"],
                "description": metadata["description"],
                "tags": metadata["hashtags"],
                "categoryId": "22"  # People & Blogs
            },
            "status": {
                "privacyStatus": metadata.get("privacy", "public")
            }
        }

        for attempt in range(1, self.retries + 1):
            try:
                request = self.youtube.videos().insert(
                    part="snippet,status",
                    body=body,
                    media_body=media
                )
                response = request.execute()
                vid_id = response.get("id")
                logging.info("Uploaded Short ID: %s", vid_id)
                return vid_id
            except Exception as e:
                logging.warning("Upload attempt %d failed: %s", attempt, e)

        logging.error("All upload attempts failed.")
        raise RuntimeError("YouTube upload failed")
