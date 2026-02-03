import unittest
from unittest.mock import patch, MagicMock
import requests
import os
import base64

BASE_URL = "http://127.0.0.1:3002/"  # Ensure this matches your actual running service

class TestRecognitionAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up test files and mock data before running tests."""
        os.makedirs("wavs", exist_ok=True)
        cls.valid_audio_path = "wavs/~Blinding Lights.wav"
        cls.invalid_audio_path = "wavs/invalid_file.txt"
        cls.empty_audio_path = "wavs/empty.wav"

        # Create an invalid file
        with open(cls.invalid_audio_path, "w") as f:
            f.write("This is not an audio file.")

        # Create an empty file
        open(cls.empty_audio_path, "wb").close()

    @classmethod
    def tearDownClass(cls):
        """Clean up test files after all tests are done."""
        os.remove(cls.valid_audio_path)
        os.remove(cls.invalid_audio_path)
        os.remove(cls.empty_audio_path)

    def test_01_valid_audio_file(self):
        """Test recognition with a valid audio file."""
        with open(self.valid_audio_path, "rb") as file:
            response = requests.post(BASE_URL + "recognise", files={"audio_file": file})

        print("DEBUG Response:", response.status_code, response.text)

        self.assertEqual(response.status_code, 200)
        self.assertIn("artist", response.json())
        self.assertIn("title", response.json())
        print("test_01_valid_audio_file passed!")

    def test_02_missing_audio_file(self):
        """Test when no file is uploaded."""
        response = requests.post(BASE_URL + "recognise", files={})  # No file provided

        self.assertEqual(response.status_code, 400)
        self.assertIn("No file uploaded", response.json()["error"])
        print("test_02_missing_audio_file passed!")

    def test_03_empty_audio_file(self):
        """Test when an empty file is uploaded."""
        with open(self.empty_audio_path, "rb") as file:
            response = requests.post(BASE_URL + "recognise", files={"audio_file": file})

        self.assertEqual(response.status_code, 400)
        self.assertIn("No file selected", response.json()["error"])
        print("test_03_empty_audio_file passed!")

    def test_04_invalid_file_format(self):
        """Test when an invalid file format (e.g., text file) is uploaded."""
        with open(self.invalid_audio_path, "rb") as file:
            response = requests.post(BASE_URL + "recognise", files={"audio_file": file})

        self.assertEqual(response.status_code, 400)
        self.assertIn("Failed to process file", response.json()["error"])
        print("test_04_invalid_file_format passed!")

if __name__ == "__main__":
    unittest.main()
