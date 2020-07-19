import os
import logging
from flask import Flask
from slack import WebClient
from slackeventsapi import SlackEventAdapter
import ssl as ssl_lib
import certifi
import random

# Initialize a Flask app to host the events adapter
app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(os.environ["SLACK_SIGNING_SECRET"], "/slack/events", app)

# Initialize a Web API client
slack_web_client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])


@slack_events_adapter.on("reaction_added")
def reaction_added(event_data):
    emoji = event_data["event"]["reaction"]
    slack_web_client.chat_postMessage(channel="bot", text=emoji)


@slack_events_adapter.on("message")
def handle_message(event_data):
    message = event_data["event"]
    channel = message["channel"]

    response = slack_web_client.users_info(user=message["user"])
    user_name = response["user"]["name"]
    if "joe" in user_name:
        slack_web_client.chat_postMessage(channel=channel, text="Bad touch, Joe.")
        return

    if message.get("subtype") is None and "hi" in message.get('text'):
        message = "Hello <@%s>! :tada:" % message["user"]
        slack_web_client.chat_postMessage(channel=channel, text=message)
        return

    if "!coinflip" in message.get('text'):
        choice = random.randint(0, 1)
        result = "heads"
        if choice is 1:
            result = "tails"
        slack_web_client.chat_postMessage(channel=channel, text=result)


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
    app.run(host='0.0.0.0', port=3000)
