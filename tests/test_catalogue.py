import unittest
from unittest import mock
from unittest.mock import patch, MagicMock
import requests
import os

BASE_URL = "http://127.0.0.1:3001/catalogue/"

### for delete success on non-mocked vers. will no lomger work as i deleted it but try passing in anything 4-16 besides 10.

class TestCatalogueAPI(unittest.TestCase):

    def test_01_add_track_success(self):
        """Test adding a valid track."""
        
        url = BASE_URL + "tracks"
        print(f"Sending request to: {url}")

        with open("wavs/Blinding Lights.wav", "rb") as audio_file:
            files = {"audio_file": ("Blinding Lights.wav", audio_file, "audio/wav")}
            data = {"title": "Blinding Lights", "artist": "The Weeknd"}

            response = requests.post(url, files=files, data=data)
            
        self.assertEqual(response.status_code, 201, "Expected 201, but got a different status code!")
        self.assertIn("Track added successfully", response.json()["message"], "Unexpected response message!")

    def test_02_add_track_missing_fields(self):
        """Test adding a track with missing fields."""
        
        url = BASE_URL + "tracks"
        print(f"Sending request to: {url}")

        with open("wavs/Blinding Lights.wav", "rb") as audio_file:
            files = {"audio_file": ("Blinding Lights.wav", audio_file, "audio/wav")}
            data = {"title": "", "artist": "The Weeknd"}

            response = requests.post(url, files=files, data=data)
            
        print(f"DEBUG: Add track missing fields response: {response.status_code}, {response.text}")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Missing required fields")

    def test_03_add_track_invalid_audio_format(self):
        """Test adding a track with an invalid audio format."""

        url = BASE_URL + "tracks" 
        print(f"Sending request to: {url}")

        with open("wavs/invalid_file.txt", "rb") as audio_file:
            files = {"audio_file": ("invalid_file.txt", audio_file, "audio/wav")}
            data = {"title": "", "artist": "The Weeknd"}

            response = requests.post(url, files=files, data=data)
            
        print(f"DEBUG: Add track missing fields response: {response.status_code}, {response.text}")

        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid file type", response.json()["error"])
              
    def test_04_add_track_no_audio_file_uploaded(self):
        """Test adding a track with no audio file."""
        url = BASE_URL + "tracks"
        print(f"Sending request to: {url}")
        
        data = {"title": "Blinding Lights", "artist": "The Weeknd"}
        response = requests.post(url, data=data)  # No file attached

        print(f"DEBUG: Add track no audio response: {response.status_code}, {response.text}")

        self.assertEqual(response.status_code, 400)
        self.assertIn("No file uploaded", response.json()["error"])

    def test_05_get_track_success(self):
        """Test retrieving a specific track."""
        url = BASE_URL + "9"  
        print(f"Sending request to: {url}")

        response = requests.get(url)
        print(f"DEBUG: Get track response: {response.status_code}, {response.text}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("title", response.json())
        self.assertIn("artist", response.json())
        self.assertIn("audio_base64", response.json())

    def test_06_get_track_failure(self):
        """Test failure of retrieving a trackk if id is not in the database"""
        url = BASE_URL + "9999"  
        print(f"Sending request to: {url}")

        response = requests.get(url)
        print(f"DEBUG: Get track response: {response.status_code}, {response.text}")
        self.assertEqual(response.status_code, 404)
        self.assertIn("Track not found", response.json()["error"])

    def test_07_delete_track_success(self):
        """Test deleting a track."""
        url = BASE_URL + "10"  
        print(f"Sending request to: {url}")

        response = requests.delete(url)
        print(f"DEBUG: Get track response: {response.status_code}, {response.text}")
        self.assertEqual(response.status_code, 200)
        
        json_response = response.json()
        self.assertIn("Track deleted successfully", json_response["message"])
        self.assertIn("deleted_track", json_response)
        self.assertIn("title", json_response["deleted_track"])
        self.assertIn("artist", json_response["deleted_track"])


    def test_08_delete_nonexistent_track(self):
        """Test deleting a non-existing track."""
        url = BASE_URL + "10"  
        print(f"Sending request to: {url}")

        response = requests.delete(url)
        print(f"DEBUG: Get track response: {response.status_code}, {response.text}")
        self.assertEqual(response.status_code, 404)
        self.assertIn("Track not found", response.json()["error"])

    def test_09_get_all_tracks(self):
        """Test retrieving all tracks."""
        url = "http://127.0.0.1:3001/catalogue"  # Make sure BASE_URL is correct
        print(f"Sending request to: {url}")
        response = requests.get(url)
        print(f"DEBUG: Get all tracks response: {response.status_code}, {response.text}")
        self.assertEqual(response.status_code, 200)

class TestCatalogueAPIMocked(unittest.TestCase):

    @patch("requests.post")
    def test_01_add_track_success(self, mock_post):
        """Mocked test for adding a valid track."""
        url = BASE_URL + "tracks"
        print(f"Mocking request to: {url}")

        # Simulated response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"message": "Track added successfully"}
        mock_post.return_value = mock_response

        with open("wavs/Blinding Lights.wav", "rb") as audio_file:
            files = {"audio_file": ("Blinding Lights.wav", audio_file, "audio/wav")}
            data = {"title": "Blinding Lights", "artist": "The Weeknd"}
            response = requests.post(url, files=files, data=data)

        self.assertEqual(response.status_code, 201)
        self.assertIn("Track added successfully", response.json()["message"])

    @patch("requests.post")
    def test_02_add_track_missing_fields(self, mock_post):
        """Mocked test for adding a track with missing fields."""
        url = BASE_URL + "tracks"

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "Missing required fields"}
        mock_post.return_value = mock_response

        response = requests.post(url, data={"title": "", "artist": "The Weeknd"})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Missing required fields")

    @patch("requests.post")
    def test_03_add_track_invalid_audio_format(self, mock_post):
        """Mocked test for adding a track with missing fields."""
        url = BASE_URL + "tracks"

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "Invalid file type"}
        mock_post.return_value = mock_response

        response = requests.post(url, data={"title": "", "artist": "The Weeknd"})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Invalid file type")

    @patch("requests.post")
    def test_04_add_track_no_audio_file_uploaded(self, mock_post):
        """Mocked test for adding a track with missing fields."""
        url = BASE_URL + "tracks"

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "No file uploaded"}
        mock_post.return_value = mock_response

        response = requests.post(url, data={"title": "", "artist": "The Weeknd"})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "No file uploaded")

    @patch("requests.get")
    def test_05_get_track_success(self, mock_get):
        """Mocked test for retrieving a specific track."""
        url = BASE_URL + "9"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 9,
            "title": "Blinding Lights",
            "artist": "The Weeknd",
            "audio_base64": "mocked_base64_audio"
        }
        mock_get.return_value = mock_response

        response = requests.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("title", response.json())
        self.assertIn("artist", response.json())
        self.assertIn("audio_base64", response.json())

    @patch("requests.get")
    def test_06_get_track_failure(self, mock_get):
        """Mocked test for failing to retrieve a track that doesn't exist."""
        url = BASE_URL + "9999"

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"error": "Track not found"}
        mock_get.return_value = mock_response

        response = requests.get(url)

        self.assertEqual(response.status_code, 404)
        self.assertIn("Track not found", response.json()["error"])

    @patch("requests.delete")
    def test_07_delete_track_success(self, mock_delete):
        """Mocked test for deleting a track."""
        url = BASE_URL + "10"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": "Track deleted successfully",
            "deleted_track": {"title": "Blinding Lights", "artist": "The Weeknd"}
        }
        mock_delete.return_value = mock_response

        response = requests.delete(url)

        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertIn("Track deleted successfully", json_response["message"])
        self.assertIn("deleted_track", json_response)
        self.assertIn("title", json_response["deleted_track"])
        self.assertIn("artist", json_response["deleted_track"])

    @patch("requests.delete")
    def test_08_delete_nonexistent_track(self, mock_delete):
        """Mocked test for deleting a non-existent track."""
        url = BASE_URL + "9999"

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"error": "Track not found"}
        mock_delete.return_value = mock_response

        response = requests.delete(url)

        self.assertEqual(response.status_code, 404)
        self.assertIn("Track not found", response.json()["error"])

    @patch("requests.get")
    def test_09_get_all_tracks(self, mock_get):
        """Mocked test for retrieving all tracks."""
        url = "http://127.0.0.1:3001/catalogue"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "tracks": [{"id": 1, "title": "Blinding Lights", "artist": "The Weeknd"}],
            "total_tracks": 1
        }
        mock_get.return_value = mock_response

        response = requests.get(url)

        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertIn("tracks", json_response)
        self.assertIn("total_tracks", json_response)
        self.assertGreater(json_response["total_tracks"], 0)

   
if __name__ == "__main__":
    unittest.main()
