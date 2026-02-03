import requests
import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import base64
import logging

KEY = os.getenv("API_KEY")
if not KEY:
    raise ValueError("API_KEY is missing. Please set it in your environment variables.")


load_dotenv()
app = Flask(__name__) 


PATH = "https://api.audd.io/"

VALID_FILE_TYPES = [".wav", ".mp3"]

@app.route("/recognise", methods=["POST"])
def recognise_track():
    """Identify a track from an uploaded file using AudD.io."""
    
    print("Received request in recognition.py:", request.files.keys())
    
    if "audio_file" not in request.files:
        return jsonify({"error": "No file uploaded. Invalid input"}), 400

    file = request.files["audio_file"]
    if file.filename == "":
        return jsonify({"error": "No file selected. Invalid input"}), 400

    try:
        wav = file.read()  # Read the file data
        frag = base64.b64encode(wav).decode('ascii')
    except Exception as e:
        return jsonify({"error": f"Failed to process file: {str(e)}"}), 400
    
    data = {"api_token": KEY, "audio": frag, "return": "spotify"}
    try:
        response = requests.post(PATH, data=data)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to connect to AudD.io API: {str(e)}"}), 500
    
    result = response.json()

    if not result.get('result'):
        return jsonify({"error": "Track not recognized by AudD.io"}), 404
    
    title = result["result"].get("title", "Unknown Track")
    artist = result["result"].get("artist", "Unknown Artist")
    
    return jsonify({"title": title, "artist": artist, "data": result["result"]}), 200



if __name__ == "__main__":
    app.run(host="127.0.0.1", port=3002, debug=True)
