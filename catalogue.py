from flask import Flask, request, jsonify, abort
import os
from dotenv import load_dotenv
from database import db 
import base64
import requests
from repository import *

app = Flask(__name__)

VALID_FILE_TYPES = [".wav", ".mp3"]

load_dotenv()
ADMIN_KEY = os.getenv("API_KEY")

@app.route('/catalogue/tracks', methods=['POST'])
def add_track():
    """Add a track with Base64-encoded audio."""
    
    # TODO: Implement check if file already in db (if it is do not add as redundant)
    
    if "audio_file" not in request.files:
        return jsonify({"error": "No file uploaded. Invalid input"}), 400

    file = request.files["audio_file"]
    if file.filename == "":
        return jsonify({"error": "No file selected. Invalid input"}), 400
    
    # Validate file type
    file_ext = os.path.splitext(file.filename)[1].lower()  # Extract file extension
    if file_ext not in VALID_FILE_TYPES:
        return jsonify({"error": f"Invalid file type: {file_ext}. Allowed: {', '.join(VALID_FILE_TYPES)}"}), 400

    try:
        wav = file.read()  # Read the file data
        audio_base64 = base64.b64encode(wav).decode('ascii')  # Encode to base64
    except Exception as e:
        return jsonify({"error": f"Failed to process file: {str(e)}"}), 400
    
    # Get title & artist from form data
    title = request.form.get("title", "Unknown Track")
    artist = request.form.get("artist", "Unknown Artist")
    
    # Debugging missing fields
    missing_fields = []
    if not title:
        missing_fields.append("title")
    if not artist:
        missing_fields.append("artist")
    if not "audio_base64":
        missing_fields.append("audio_base64")

    if missing_fields:
        print(f"Missing fields: {missing_fields}")
        print(f"Received Data: title={title}, artist={artist}")
        return jsonify({
            "error": "Missing required fields",
            "missing_fields": missing_fields,
            "received_data": {
                "title": title or "None",
                "artist": artist or "None",
                "audio_file": "Present" if audio_base64 else "Missing"
            }
        }), 400
    try:
        db.insert(title, artist, audio_base64)
    except Exception as e:
        return jsonify({"error": f"Failed to add track to database. Server error: {str(e)}"}), 500
    
    return jsonify({"message": "Track added successfully"}), 201

@app.route('/catalogue/<int:track_id>', methods=['GET'])
def get_track(track_id):
    # READ TRACK GET REQUEST
    track = db.get_by_id(track_id)  # Use the `get_by_id` method from `repository`
    if not track:
        return jsonify({"error": "Track not found"}), 404
    
    # Format the track data into a dictionary
    track_data = {"id": track[0], "title": track[1], "artist": track[2], "audio_base64": track[3]}
    return jsonify(track_data), 200


@app.route('/catalogue/<int:track_id>', methods=['DELETE'])
def delete_track(track_id):
    try:
        track = db.get_by_id(track_id)
        if not track:
            return jsonify({"error": "Track not found"}), 404
        
        deleted_rows = db.delete(track_id)
        if deleted_rows == 0:
            raise Exception("Database delete operation failed")  # Force a 500 error

        # Format the track data into a dictionary
        track_data = {"id": track[0], "title": track[1], "artist": track[2], "audio_base64": track[3]}
        return jsonify({"message": "Track deleted successfully", "deleted_track": track_data}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete track. Server error: {str(e)}"}), 500


@app.route('/catalogue', methods=['GET'])
def get_all_tracks():
    try:
        tracks = db.get_all()
        
        if tracks is None:
            raise Exception("Database retrieval failed")  # Simulating an error
        
        track_list = [{"id": track[0], "title": track[1], "artist": track[2], "audio_base64": track[3]} for track in tracks]
        count = len(track_list)
        return jsonify({"tracks": track_list, "total_tracks": count}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve tracks. Server error: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host="localhost",port =3001, debug=True)
