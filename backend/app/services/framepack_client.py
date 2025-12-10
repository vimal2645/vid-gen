# backend/app/services/framepack_client.py
import os
import time
import requests
from app.config import FRAMEPACK_API_URL, FRAMEPACK_STATUS_URL
from app.utils.storage import get_video_file_path

def generate_video_with_framepack(job_id: str, prompt: str, duration_seconds: int) -> str:
    """
    Call video-worker service for video generation.
    """
    if not FRAMEPACK_API_URL or not FRAMEPACK_STATUS_URL:
        raise Exception("FRAMEPACK_API_URL or FRAMEPACK_STATUS_URL not set in .env")

    output_path = get_video_file_path(job_id)

    # 1) Submit job
    payload = {
        "prompt": prompt,
        "duration_seconds": duration_seconds,
        "job_id": job_id,
    }

    try:
        print(f"[{job_id}] Submitting to {FRAMEPACK_API_URL}")
        resp = requests.post(FRAMEPACK_API_URL, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        remote_job_id = data.get("job_id", job_id)
        print(f"[{job_id}] Submitted, remote_job_id: {remote_job_id}")
    except Exception as e:
        raise Exception(f"Failed to submit job to video-worker: {str(e)}")

    # 2) Poll for status
    max_polls = 240  # up to 20 minutes
    delay = 5

    for poll_attempt in range(max_polls):
        try:
            status_url = f"{FRAMEPACK_STATUS_URL}/{remote_job_id}"
            status_resp = requests.get(status_url, timeout=30)
            status_resp.raise_for_status()
            sdata = status_resp.json()
            status = sdata.get("status")

            print(f"[{job_id}] Poll {poll_attempt}: status = {status}")

            if status == "done":
                video_url = sdata.get("video_url")
                if not video_url:
                    raise Exception("Worker reported done but no video_url")

                # 3) Download final video
                print(f"[{job_id}] Downloading from {video_url}")
                v = requests.get(video_url, timeout=600)
                v.raise_for_status()
                with open(output_path, "wb") as f:
                    f.write(v.content)
                
                print(f"[{job_id}] Saved to {output_path}")
                return output_path

            if status == "failed":
                error_msg = sdata.get("message", "Unknown error")
                raise Exception(f"Worker failed: {error_msg}")

            time.sleep(delay)

        except requests.exceptions.RequestException as e:
            raise Exception(f"Status check failed: {str(e)}")

    raise Exception("Video generation timed out")
