import unittest
import requests
import requests_mock
import base64
import os

# Set up base URL for microservice
BASE_URL = "http://127.0.0.1:3003"

class TestAPIEndpoints(unittest.TestCase):
    
    def setUp(self):
        """Set up mock data for testing."""
        self.mock_audio_data = base64.b64encode(b"fake_audio_data").decode("utf-8")
        self.track_data = {
            "id": 1,
            "title": "Everybody",
            "artist": "Backstreet Boys",
            "audio_base64": self.mock_audio_data
        }

    @requests_mock.Mocker()
    def test_add_track_success(self, mock):
        """Test adding a track successfully."""
        mock.post(f"{BASE_URL}/add_track", json={"message": "Track added successfully"}, status_code=201)
        
        response = requests.post(f"{BASE_URL}/add_track", files={"audio_file": ("test.wav", b"data", "audio/wav")}, data={"title": "Test", "artist": "Artist"})
        self.assertEqual(response.status_code, 201)
        self.assertIn("Track added successfully", response.json()["message"])

    @requests_mock.Mocker()
    def test_add_track_missing_file(self, mock):
        """Test adding a track with missing file."""
        mock.post(f"{BASE_URL}/add_track", json={"error": "No file uploaded"}, status_code=400)

        response = requests.post(f"{BASE_URL}/add_track", data={"title": "Test", "artist": "Artist"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("No file uploaded", response.json()["error"])

    @requests_mock.Mocker()
    def test_delete_track_success(self, mock):
        """Test deleting a track successfully."""
        mock.delete(f"{BASE_URL}/delete_track/1", json={"message": "Track deleted"}, status_code=200)

        response = requests.delete(f"{BASE_URL}/delete_track/1")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Track deleted", response.json()["message"])

    @requests_mock.Mocker()
    def test_delete_track_not_found(self, mock):
        """Test deleting a track that doesn't exist."""
        mock.delete(f"{BASE_URL}/delete_track/999", json={"error": "Track not found"}, status_code=404)

        response = requests.delete(f"{BASE_URL}/delete_track/999")
        self.assertEqual(response.status_code, 404)
        self.assertIn("Track not found", response.json()["error"])

    @requests_mock.Mocker()
    def test_get_all_tracks_success(self, mock):
        """Test fetching all tracks successfully."""
        mock.get(f"{BASE_URL}/get_all_tracks", json=[self.track_data], status_code=200)

        response = requests.get(f"{BASE_URL}/get_all_tracks")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["title"], "Everybody")

    @requests_mock.Mocker()
    def test_get_track_and_play_success(self, mock):
        """Test fetching and playing a track successfully."""
        mock.get(f"{BASE_URL}/get_track_and_play/1", json=self.track_data, status_code=200)

        response = requests.get(f"{BASE_URL}/get_track_and_play/1")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Everybody", response.json()["title"])

    @requests_mock.Mocker()
    def test_get_track_and_play_not_found(self, mock):
        """Test fetching a track that doesn't exist."""
        mock.get(f"{BASE_URL}/get_track_and_play/999", json={"error": "Track not found"}, status_code=404)

        response = requests.get(f"{BASE_URL}/get_track_and_play/999")
        self.assertEqual(response.status_code, 404)
        self.assertIn("Track not found", response.json()["error"])

    @requests_mock.Mocker()
    def test_recognise_track_success(self, mock):
        """Test recognising a track successfully."""
        mock.post(f"{BASE_URL}/recognise", json={"title": "Everybody", "artist": "Backstreet Boys"}, status_code=200)

        response = requests.post(f"{BASE_URL}/recognise", files={"audio_file": ("test.wav", b"data", "audio/wav")})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "Everybody")

    @requests_mock.Mocker()
    def test_recognise_and_add_success(self, mock):
        """Test recognising and adding a track successfully."""
        mock.post(f"{BASE_URL}/recognise_and_add", json={"message": "Track recognized and added successfully"}, status_code=201)

        response = requests.post(f"{BASE_URL}/recognise_and_add", files={"audio_file": ("test.wav", b"data", "audio/wav")})
        self.assertEqual(response.status_code, 201)
        self.assertIn("Track recognized and added successfully", response.json()["message"])

    @requests_mock.Mocker()
    def test_recognise_and_add_failure(self, mock):
        """Test failing to recognise a track."""
        mock.post(f"{BASE_URL}/recognise_and_add", json={"error": "Failed to recognize track"}, status_code=400)

        response = requests.post(f"{BASE_URL}/recognise_and_add", files={"audio_file": ("test.wav", b"data", "audio/wav")})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Failed to recognize track", response.json()["error"])

if __name__ == "__main__":
    unittest.main()
