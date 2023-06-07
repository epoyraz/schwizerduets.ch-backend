import requests
import time
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify

load_dotenv()

AUTHORIZATION = os.getenv("AUTHORIZATION")
USERID = os.getenv("USERID")

app = Flask(__name__)


def convert(text):
    url = "https://play.ht/api/v1/convert"

    payload = {"content": [text], "voice": "de-CH-LeniNeural", "title": text[:50]}
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": AUTHORIZATION,
        "x-user-id": USERID,
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()["transcriptionId"]


def check(transcriptionId):
    url = "https://play.ht/api/v1/articleStatus?transcriptionId=" + transcriptionId

    headers = {
        "accept": "application/json",
        "authorization": AUTHORIZATION,
        "x-user-id": USERID,
    }

    response = requests.get(url, headers=headers).json()
    retries = 20
    while not "audioUrl" in response:
        response = requests.get(url, headers=headers).json()
        time.sleep(0.5)  # wait a bit between retries
        retries -= 1
        if retries == 0:
            # if no data after all retries, give up
            return "Failed getting data from the server!"
    audioUrl = requests.get(url, headers=headers).json()["audioUrl"]
    return audioUrl


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    text = data["text"]
    transcriptionId = convert(text)
    audioUrl = check(transcriptionId)
    return jsonify({"audioUrl": audioUrl})


if __name__ == "__main__":
    app.run(port=5000, debug=True)
