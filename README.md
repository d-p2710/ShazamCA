# Music Recognition & Catalogue Microservice System

A Flask-based microservice system for audio track recognition and cataloguing, integrating external APIs for audio processing and identification.

## Features

- **Audio Recognition**: Identify tracks using AudD.io API
- **Microservice Architecture**: Three independent services (catalogue, recognition, API gateway)
- **RESTful API**: Complete CRUD operations for track management
- **Audio Processing**: Support for WAV/MP3 formats with Base64 encoding
- **Database Integration**: SQLite for persistent storage

## Architecture

```text
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   API Gateway   │────▶│  Catalogue Svc  │────▶│    SQLite DB    │
│   (Port: 3003)  │     │   (Port: 3001)  │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                         │
         ▼                         │
┌─────────────────┐                │
│ Recognition Svc │◀───────────────┘
│   (Port: 3002)  │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│   AudD.io API   │
└─────────────────┘

```

## Quick Start

### Prerequisites
- Python 3.9+
- AudD.io API key (free tier available)

### Installation

```bash
# Clone the repository
git clone https://github.com/d-p2710/ShazamCA.git
cd ShazamCA

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
echo "API_KEY=your_auddio_api_key_here" > .env
```
### Running the Services
```
# Terminal 1: Catalogue Service
python catalogue.py

# Terminal 2: Recognition Service  
python recognition.py

# Terminal 3: Main API Gateway
python main.py
```

### API Endpoints
#### Catalogue Service (Port: 3001)
POST /catalogue/tracks - Add a new track \
GET /catalogue/<track_id> - Retrieve specific track \
GET /catalogue - List all tracks \
DELETE /catalogue/<track_id> - Remove a track 

#### Recognition Service (Port: 3002)
POST /recognise - Identify audio track using AudD.io 

#### Main Gateway (Port: 3003)
POST /add_track - Add track to catalogue \
POST /recognise - Recognise and return track info \
POST /recognise_and_add - Recognise and auto-add to catalogue \
GET /get_track_and_play/<id> - Retrieve and play audio \
GET /get_all_tracks - List all catalogue entries \
DELETE /delete_track/<id> - Remove track

### Technology Stack
- Backend: Python, Flask 
- Database: SQLite 
- External APIs: AudD.io (audio recognition) 
- Audio Processing: Base64 encoding/decoding 
- Architecture: Microservices, REST APIs

### Project Structure
```
ShazamCA/
├── catalogue.py          # Catalogue microservice
├── recognition.py        # Audio recognition service  
├── main.py              # API gateway
├── database.py          # Database initialization
├── repository.py        # Database operations
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
└── README.md           # This file\
```

### Configuration
1. Get a free API key from AudD.io
2. Create .env file:
    ``` API_KEY=your_auddio_api_key_here ``` \
   Supported audio formats: .wav, .mp3

### Testing
```
# Test catalogue endpoints
curl -X POST http://localhost:3001/catalogue/tracks \
  -F "audio_file=@sample.wav" \
  -F "title=Sample Track" \
  -F "artist=Sample Artist"

# Test recognition
curl -X POST http://localhost:3002/recognise \
  -F "audio_file=@unknown.wav"

# Test integrated flow
curl -X POST http://localhost:3003/recognise_and_add \
  -F "audio_file=@song.wav"
```

