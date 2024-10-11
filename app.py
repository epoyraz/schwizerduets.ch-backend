import os
import uuid
from datetime import datetime

import azure.cognitiveservices.speech as speechsdk
from flask import Flask, jsonify, request
from google.cloud import storage

os.environ["GCLOUD_PROJECT"] = "schwizerduetsch"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
    "/home/inozenz/code/schwizerduetsch-backend/application_default_credentials.json"
)

app = Flask(__name__)


def generate_audio(text):
    # Azure Speech Service configuration
    api_key = "9bc1cde5803d4b6c8f4af9981327ec5f"
    endpoint = "switzerlandnorth"

    speech_config = speechsdk.SpeechConfig(subscription=api_key, region=endpoint)
    speech_config.speech_synthesis_voice_name = "de-CH-LeniNeural"

    hash = uuid.uuid4().hex
    # Output file configuration
    output_file = f"./output/{hash}.wav"

    # Configure audio output to a file
    file_config = speechsdk.audio.AudioOutputConfig(filename=output_file)

    # Create speech synthesizer with file output
    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=file_config
    )

    # Synthesize speech
    result = speech_synthesizer.speak_text_async(text).get()

    # Check if synthesis was successful
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"Audio saved to {output_file}")
        return output_file
    else:
        print(f"Speech synthesis failed: {result.cancellation_details.error_details}")


def upload_file(userid, filename):
    storage_client = storage.Client()
    bucket = storage_client.bucket("schwizerduetsch")
    # Set date_variable to the current date
    date = datetime.now().strftime("%Y-%m-%d")
    # Get the current Unix epoch time
    unix_epoch_time = int(datetime.now().timestamp())
    blob = bucket.blob(f"{date}/{unix_epoch_time}/{filename}")
    blob.upload_from_filename(filename)
    return blob.public_url


@app.route("/generateAudio", methods=["POST"])
def generate():
    data = request.get_json()
    text = data["text"]
    print("generating audio from following text: " + text)
    filename = generate_audio(text)
    audioUrl = upload_file(filename)
    return jsonify({"audioUrl": audioUrl})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=7333)
