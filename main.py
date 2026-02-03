import subprocess
import requests
from flask import Flask, request, jsonify
import base64
import os
import time

# Microservice URLs
catalogue_url = "http://localhost:3001/catalogue"
recognise_track_url = "http://localhost:3002/recognise"

app = Flask(__name__)


TEMP_DIR = "temp_audio"
os.makedirs(TEMP_DIR, exist_ok=True)

@app.route("/add_track", methods=["POST"])
def add_track():
    """Forward add_track request to catalogue service."""
    if "audio_file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["audio_file"]
    files = {"audio_file": (file.filename, file.stream, file.mimetype)}
    
    response = requests.post(f"{catalogue_url}/tracks", files=files, data=request.form)
    print (f"Sending track data to catalogue service: {response}")
    return jsonify(response.json()), response.status_code

@app.route("/delete_track/<int:track_id>", methods=["DELETE"])
def delete_track(track_id):
    """Call delete_track microservice."""
    response = requests.delete(f"{catalogue_url}/{track_id}")
    if response.status_code == 200:
        return jsonify(response.json()), 200
    else:
        return jsonify({"error": "Failed to delete track"}), 500, response.status_code

@app.route("/get_all_tracks", methods=["GET"])
def get_all_tracks():
    """Call get_all_tracks microservice."""
    response = requests.get(catalogue_url)
    if response.status_code == 200:
        return jsonify(response.json()), 200
    else:
        return jsonify({"error": "Failed to fetch tracks"}), 500

@app.route("/get_track_and_play/<int:track_id>", methods=["GET"])
def get_track_and_play(track_id):
    print(f"🔍 Fetching track with ID: {track_id}...")
    response = requests.get(f"{catalogue_url}/{track_id}")

    if response.status_code != 200:
        print(f"Error fetching track: {response.status_code}, {response.text}")
        return jsonify({"error": "Failed to fetch track"}), response.status_code

    track_data = response.json()
    title = track_data.get("title", "Unknown_Track")
    artist = track_data.get("artist", "Unknown_Artist")
    print(f"🎵 Track fetched: {title} by {artist}")

    # Extract Base64-encoded audio
    audio_base64 = track_data.get("audio_base64")

    if not audio_base64:
        print("No audio data found")
        return jsonify({"error": "No audio data found"}), 400


    decoded_audio = base64.b64decode(audio_base64)

    # Save to temp directory
    file_path = os.path.join(TEMP_DIR, f"{title}.wav")
    with open(file_path, "wb") as file:
        file.write(decoded_audio)
    
    print(f"Audio file saved: {file_path}")

    # Play the .wav file
    subprocess.run(["afplay", file_path])  # Works on macOS. Use 'play' for Linux, 'start' for Windows.
    
    # Auto-delete file after playing
    try:
        time.sleep(1)  # Ensure afplay finishes using the file before deletion
        os.remove(file_path)
        print(f"Deleted file: {file_path}")
    except Exception as e:
        print(f"Failed to delete file: {e}")

    return jsonify(track_data), 200
    
@app.route("/recognise", methods=["POST"])
def recognise_track():
    """Call recognise_track microservice with file upload support."""
    if "audio_file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["audio_file"]
    files = {"audio_file": (file.filename, file.stream, file.mimetype)}

    # Debugging: Print the response from `recognition.py`
    response = requests.post(recognise_track_url, files=files)
    print("🔍 Raw response from recognition.py:", response.status_code, response.text)

    if response.status_code != 200:
        return jsonify({"error": "Failed to recognize track"}), response.status_code

    try:
        return jsonify(response.json()), response.status_code
    except requests.exceptions.JSONDecodeError:
        return jsonify({"error": "Recognition service did not return JSON", "raw_response": response.text}), 500

@app.route("/recognise_and_add", methods=["POST"])
def recognise_and_add():
    
    """Recognises a track and adds it to the catalogue if found."""
    print("recognise_and_add was called")
    
    if "audio_file" not in request.files:
        print("No file uploaded")
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["audio_file"]
    print(f"Received file: {file.filename}")


    files = {"audio_file": (file.filename, file.stream, file.mimetype)}
    
    print("Sending file to recognition service...")

    # Call `recognition.py`
    response = requests.post(f"{recognise_track_url}", files=files)

    if response.status_code != 200:
        print(f"Recognition failed! Status: {response.status_code}")
        return jsonify({"error": "Failed to recognize track"}), response.status_code

    result = response.json()
    print(f"Recognition result: {result}")

    if not result.get("title") or not result.get("artist"):
        print("No valid metadata found in response")
        return jsonify({"error": "Track recognition failed. No valid metadata."}), 404

    title = result["title"]
    artist = result["artist"]
    print(f"🎵 Track recognized: {title} by {artist}")

    data = {"title": title, "artist": artist}
    files = {"audio_file": (file.filename, file.read(), file.mimetype)}


    print("Sending data to catalogue service...")
    print(f"Data: {data}")
    print(f"Files: {files}")
    
    
    print(f"Sending track data to catalogue service...")
    
    add_response = requests.post(
    f"{catalogue_url}/tracks", files=files, data=data)
# )
    print(f"Catalogue API response: {add_response.status_code}, {add_response.text}")

    if add_response.status_code == 201:
        print("Track added successfully")
        return jsonify({
            "message": "Track recognized and added successfully",
            "title": title,
            "artist": artist,
            "database_response": add_response.json()
        }), 201
    else:
        print("Failed to add track to catalogue")
        return jsonify({"error": "Failed to add track to catalogue"}), add_response.status_code

if __name__ == "__main__":
    app.run(host="localhost", port=3003, debug=True)