import requests
import base64
import os

# Base URL of the API
BASE_URL = "http://127.0.0.1:8000"

# Ensure the path is relative to the script location
IMAGE_PATH = os.path.join(os.path.dirname(__file__), "test_image.jpg")

def test_get_ocr_list():
    """Test the /GetOcrList endpoint to fetch available OCR engines."""
    response = requests.get(f"{BASE_URL}/GetOcrList")
    if response.status_code == 200:
        print("Available OCR Engines:", response.json()["available_engines"])
    else:
        print("Failed to fetch OCR engines:", response.text)

def test_get_ocr(engine_name):
    """Test the /GetOcr endpoint with a specified OCR engine."""
    try:
        # Read and encode the image in Base64
        with open(IMAGE_PATH, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")
        
        # Prepare the payload
        payload = {
            "file": base64_image,
            "engine": engine_name
        }

        # Make the POST request
        response = requests.post(f"{BASE_URL}/GetOcr", json=payload)
        
        # Check the response
        if response.status_code == 200:
            result = response.json()["result"]
            print(f"Engine: {result['engine']}")
            print(f"Execution Time: {result['execution_time']} seconds")
            print("Recognized Text:\n", result["text"])
        else:
            print("Failed to process OCR:", response.text)
    except Exception as e:
        print(f"Error during OCR request: {e}")

if __name__ == "__main__":
    # Test the OCR list endpoint
    test_get_ocr_list()

    # Test the OCR endpoint for each engine
    for engine in ["easyocr", "tesseract", "paddleocr"]:
        print(f"\nTesting OCR with {engine} engine:")
        test_get_ocr(engine)
