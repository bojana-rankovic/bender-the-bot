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
            print(
                f"Failed with status code: {e.response.status_code} and body: {e.response.text}"
            )
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
                await say(
                    channel=message["channel"], text=response_text, thread_ts=thread_ts
                )

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


# Start app
if __name__ == "__main__":
    app.start(port=8443)