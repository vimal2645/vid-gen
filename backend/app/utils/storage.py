# backend/app/utils/storage.py
import os
import uuid
from typing import Dict
from app.config import VIDEO_STORAGE_DIR

os.makedirs(VIDEO_STORAGE_DIR, exist_ok=True)

_jobs: Dict[str, Dict] = {}

def create_job() -> str:
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {
        "status": "queued",
        "message": "Job created",
        "video_path": None,
    }
    return job_id

def set_job_running(job_id: str):
    if job_id in _jobs:
        _jobs[job_id]["status"] = "running"
        _jobs[job_id]["message"] = "Generating video..."

def set_job_failed(job_id: str, msg: str):
    if job_id in _jobs:
        _jobs[job_id]["status"] = "failed"
        _jobs[job_id]["message"] = msg

def set_job_done(job_id: str, video_path: str):
    if job_id in _jobs:
        _jobs[job_id]["status"] = "done"
        _jobs[job_id]["message"] = "Completed"
        _jobs[job_id]["video_path"] = video_path

def get_job(job_id: str):
    return _jobs.get(job_id)

def build_video_url(job_id: str) -> str:
    return f"/videos/{job_id}.mp4"

def get_video_file_path(job_id: str) -> str:
    return os.path.join(VIDEO_STORAGE_DIR, f"{job_id}.mp4")
