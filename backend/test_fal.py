# backend/test_fal.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

FAL_KEY = os.getenv("FAL_KEY")
MODEL_ID = "fal-ai/fast-svd/text-to-video"
URL = f"https://queue.fal.run/{MODEL_ID}"

print("FAL_KEY prefix:", FAL_KEY[:10] if FAL_KEY else None)

headers = {
    "Authorization": f"Key {FAL_KEY}",
    "Content-Type": "application/json",
}

payload = {
    "input": {
        "prompt": "A rocket taking off into the night sky",
        "num_frames": 25,
        "fps": 8,
    }
}

print("Sending request to:", URL)
resp = requests.post(URL, json=payload, headers=headers)
print("Status code:", resp.status_code)
print("Response text (first 500 chars):")
print(resp.text[:500])
