import requests
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


#Function to transform text into audio and save it as a file
def save_audio_file(text, HF_API_KEY, filename="output.wav"):
    API_URL = "https://api-inference.huggingface.co/models/facebook/mms-tts-eng"
    headers = {f"Authorization": "Bearer {HF_API_KEY}"}
    payload = {"inputs": text}
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
        return filename
    else:
        return None


#Upload audio file to Slack
async def upload_file_to_slack(channel_id, file_path):
    """Provide channel ID to upload audio file to a specific
    Slack channel"""
    client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    try:
        response = await client.files_upload(
            channels=channel_id,
            file=file_path,
            filename=os.path.basename(file_path),
            title="Here's your audio response!"
        )
        print("File uploaded successfully: ", response["file"]["id"])
    except SlackApiError as e:
        print(f"File upload failed: {e.response['error']}")

