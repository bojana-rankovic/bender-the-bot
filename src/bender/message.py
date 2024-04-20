from slack_bolt.async_app import AsyncApp
import os
from urllib.parse import urlparse
import re
import logging
from paperqa import Docs

logging.basicConfig(level=logging.DEBUG)

app = AsyncApp(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
)


def contains_url(string):
    url_pattern = r"(http[s]?://\S+)"
    return re.search(url_pattern, string) is not None


from html.parser import HTMLParser
import requests


class TitleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_title_tag = False
        self.title = ""

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "title":
            self.in_title_tag = True

    def handle_data(self, data):
        if self.in_title_tag:
            self.title += data

    def handle_endtag(self, tag):
        if tag.lower() == "title":
            self.in_title_tag = False


# Function to get the title of the webpage
def get_page_title(url):
    try:
        response = requests.get(url, timeout=50)
        response.raise_for_status()  # will throw an error if the status is not OK
        parser = TitleParser()
        parser.feed(response.text)
        return parser.title.strip()
    except requests.RequestException as e:
        print(f"Request failed: {type(e).__name__}, {e}")
        if e.response:
            print(f"Failed with status code: {e.response.status_code} and body: {e.response.text}")
        return "Error fetching title"


thread_url_map = {}
docs = Docs()


async def process_amessage(message, say, client, thread_url_map, logger):
    try:
        text = message["text"]
        thread_ts = message.get("thread_ts") or message["ts"]
        bot_user_id = "U06EG8QHJUA"
        mention_tag = f"<@{bot_user_id}>"

        if contains_url(text):
            urls = re.findall(r"https?://[^\s>]+", text)
            if urls:
                local_docs = Docs()  # Create a new Docs instance for each URL
                local_docs.add_url(urls[0])
                thread_url_map[thread_ts] = local_docs

        if mention_tag in text:
            local_docs = thread_url_map.get(thread_ts, None)
            if local_docs:
                query_text = text.replace(mention_tag, "").strip()
                answer = await local_docs.aquery(query_text)
                response_text = f"{answer}"
                await say(channel=message["channel"], text=response_text, thread_ts=thread_ts)

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        error_message = "Sorry, I encountered an error processing your request."
        await say(channel=message["channel"], text=error_message, thread_ts=thread_ts)


# Slack event handler
@app.message(re.compile(".+"))
async def handle_message_events(ack, message, say, client, logger):
    await ack()
    await process_amessage(message, say, client, thread_url_map, logger)


@app.event("url_verification")
async def handle_url_verification_events(body, ack):
    await ack(body.get("challenge"))


from openai import ChatCompletion


@app.command("/motivate")
async def handle_motivation_command(ack, body, say):
    await ack()  # Acknowledge the command request

    # Parse the command parameter, if provided
    text = body.get("text", "").strip().lower()
    topic = text if text in ["life", "phd", "love", "job"] else "general"

    # Generate a motivational message
    try:
        response = ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"You are an assistant who provides motivational messages about {topic} in the style of Bender from Futurama.",
                },
                {"role": "user", "content": "I need some motivation today."},
            ],
        )
        motivational_message = response["choices"][0]["message"]["content"]
    except Exception as e:
        motivational_message = "Failed to generate motivation due to an error."
        print(f"Error: {e}")

    # Send the motivational message to the user
    await say(motivational_message)


import json
import os

LAST_READ_FILE = "last_read_timestamps.json"

# Initialize our in-memory store
last_read_store = {}


def load_last_read_timestamps():
    if os.path.exists(LAST_READ_FILE):
        with open(LAST_READ_FILE, "r") as file:
            return json.load(file)
    return {}


def get_last_read_timestamp(user_id, channel_id):
    # Load timestamps from the file system
    global last_read_store
    last_read_store = load_last_read_timestamps()

    # Retrieve the last read timestamp from the store
    return last_read_store.get(f"{user_id}_{channel_id}", "0")


def set_last_read_timestamp(user_id, channel_id, timestamp):
    # Update the last read timestamp in the store
    last_read_store[f"{user_id}_{channel_id}"] = timestamp

    # Write the updated store back to the file system
    with open(LAST_READ_FILE, "w") as file:
        json.dump(last_read_store, file)


async def get_new_messages(client, channel_id, user_id):
    # Retrieve the last read timestamp from storage
    last_read_timestamp = get_last_read_timestamp(user_id, channel_id)

    # Call the conversations.history Slack API method to fetch messages since the last read timestamp
    response = await client.conversations_history(
        channel=channel_id, oldest=last_read_timestamp, limit=100
    )

    # Check for success and get messages
    if response["ok"]:
        new_messages = [
            msg
            for msg in response["messages"]
            if msg.get("user") != "U06EG8QHJUA" and not msg.get("bot_id")
        ]

        # Update the last read timestamp with the latest one from the fetched messages
        if new_messages:
            latest_timestamp = new_messages[0]["ts"]
            set_last_read_timestamp(user_id, channel_id, latest_timestamp)

        return new_messages
    else:
        raise Exception("Failed to fetch messages from Slack API")


@app.command("/tldr")
async def tldr_command(ack, body, say, client):
    await ack()  # Acknowledge the command request
    channel_id = body["channel_id"]
    user_id = body["user_id"]

    # Fetch the latest messages since the user last checked
    new_messages = await get_new_messages(client=client, channel_id=channel_id, user_id=user_id)
    new_messages = new_messages[::-1]
    print("THESE ARE NEW MESSAGEs")
    print(new_messages)
    print()
    if not new_messages:
        await say("There are no new messages to summarize.")
        return

    # Concatenate messages into a single text
    conversation_text = " ".join([msg["text"] for msg in new_messages])

    # Generate a summary using the LLM
    summary_prompt = f"Please summarize the following conversation: {conversation_text}"

    try:
        response = ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"Your job is to summarize long discussion in slack channels, cause aint nobody got time to read all that. Do it in style of Bender from Futurama.",
                },
                {
                    "role": "user",
                    "content": f"Yo Bender, I need tldr for this conversation: {conversation_text}",
                },
            ],
        )
        summary = response["choices"][0]["message"]["content"]
    except Exception as e:
        summary = "Failed to generate tldr due to an error."
        print(f"Error: {e}")

    # Post the summary back to the channel or the user
    await say(summary)


# Start app
if __name__ == "__main__":
    app.start(port=8443)
