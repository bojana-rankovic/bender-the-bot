import os
from slack_bolt.async_app import AsyncApp
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
from bender.components.moddspy import set_dspy, Recommender, PQA


load_dotenv()
set_dspy()
recommend_user = Recommender()
pqa = PQA()


# Initialize the Slack app with your bot token and signing secret
app = AsyncApp(
    token=os.environ.get("SLACK_BOT_TOKEN_2"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET_2"),
)

# Store the bot's user ID
bot_user_id = None
client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN_2"))

# Handle app mentions in private chats
@app.event("app_mention")
async def handle_app_mention(event, say, context):
    global bot_user_id
    
    # Get the bot's user ID from the AuthorizeResult
    if bot_user_id is None:
        bot_user_id = context["bot_user_id"]
    
    # Extract the message text and sender's user ID
    message_text = event["text"]
    user_id = event["user"]

    # Remove the bot mention from the message text
    bot_mention = f"<@{bot_user_id}>"
    message_text = message_text.replace(bot_mention, "").strip()

    # Send the same message back to the user
    await say(text="You have sent a message", channel=user_id)


# Handle messages in a specific channel
@app.event("message")
async def handle_channel_message(event, say):


    usr_id_dict = {
        "Andres": "U0706NQTX09",
        "Bojana": "U06EFLK3NLS",
        "Victor": "U0706NXBVMX"
    }


    usr_ctxt = {
        "Bojana": "Bojana is interested in the application of new kernel methods to improve the performance of Bayesian Optimization.",
        "Andres": "Andres is very interested in the applications of language models to improve the performance of question answering systems.",
        "Victor": "Victor is interested in graph neural networks and new evaluation methods and metrics",
    }

    uid_msg = {uid: usr_ctxt[n] for n, uid in usr_id_dict.items()}

    # Check if the message is a direct message
    if event.get("channel_type") == "im":
        # Ignore messages from the bot itself
        if event.get("bot_id") is None:
            # Extract the message text, sender's user ID, and timestamp
            message_text = event["text"]
            user_id = event["user"]
            thread_ts = event["ts"]

            if event.get("thread_ts"):
                    # Get the first message in the thread
                    first_message = get_first_message_in_thread(event["channel"], event["thread_ts"])
                    
                    # Process the message and generate a response
                    response = generate_response(
                        context=(
                            f"This user will ask questions about this context: CONTEXT {first_message} END_CONTEXT "
                            f"\nHere are the user's interests, they may be relevant: {uid_msg[user_id]}"
                        ),
                        question=message_text
                    )

                    # Send the response as a threaded reply
                    await say(text=response, channel=user_id, thread_ts=thread_ts)
    
    else:


        if event.get("channel") == "C06V8GPLKFU":
            # Ignore messages from the bot itself
            if event.get("bot_id") is None:
                # Extract the message text, sender's user ID, and timestamp

                message_text = event['text']
                user_id = event["user"]
                thread_ts = event["ts"]
                
                # Process the message and perform desired actions
                response = process_message(message_text, user_id, thread_ts, uctxt_l = list(usr_ctxt.values()))
                users = response.users.users

                await say(text=str(response), channel=usr_id_dict['Andres'], thread_ts=thread_ts)
                for u in users:
                    uid = usr_id_dict[u]
                    await say(
                        text=f"Hey there! I think you might be interested in this paper. Here's why: \n\n{response.reasoning}",
                        channel=uid,
                        thread_ts=thread_ts
                    )

def get_first_message_in_thread(channel_id, thread_ts):
    try:
        # Retrieve the conversation replies
        result = client.conversations_replies(channel=channel_id, ts=thread_ts, limit=1, inclusive=True)
        
        # Get the first message from the replies
        first_message = result["messages"][0]["text"]
        
        return first_message
    except SlackApiError as e:
        print(f"Error: {e}")
        return None

def process_message(message_text, user_id, thread_ts, uctxt_l):
    response = recommend_user(
        paper_abstract = message_text,
        user_context = uctxt_l
    )
    return response

def generate_response(context, question):
    response = pqa(
        context=context,
        question=question
    )
    return response.answer


# Start the Slack app
if __name__ == "__main__":
    app.start(port=3001)