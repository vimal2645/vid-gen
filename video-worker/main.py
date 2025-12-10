# video-worker/main.py - DUMMY VERSION (no dependencies issues)
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uuid
import time
import os
from pathlib import Path
import subprocess

app = FastAPI(title="Video Worker Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

jobs_store = {}
OUTPUT_DIR = Path("./outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

class GenerateRequest(BaseModel):
    prompt: str
    duration_seconds: int = 10
    job_id: Optional[str] = None

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    message: Optional[str] = None
    video_url: Optional[str] = None

def create_dummy_mp4(output_path: str, duration_seconds: int = 5):
    """Create a dummy black MP4 file for testing."""
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f", "lavfi",
                "-i", "color=c=black:s=640x360",
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-t", str(min(duration_seconds, 10)),
                output_path,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except Exception as e:
        print(f"Error: {e}")
        with open(output_path, "wb") as f:
            f.write(b"")
        return False

def generate_video_background(job_id: str, prompt: str, duration_seconds: int):
    """Background task to generate video."""
    try:
        jobs_store[job_id]["status"] = "running"
        jobs_store[job_id]["message"] = "Generating video..."
        
        time.sleep(3)
        
        output_file = OUTPUT_DIR / f"{job_id}.mp4"
        success = create_dummy_mp4(str(output_file), duration_seconds)
        
        if success or output_file.exists():
            video_url = f"http://localhost:8082/download/{job_id}"
            jobs_store[job_id]["status"] = "done"
            jobs_store[job_id]["message"] = "Video generated successfully"
            jobs_store[job_id]["video_url"] = video_url
            jobs_store[job_id]["video_path"] = str(output_file)
        else:
            jobs_store[job_id]["status"] = "failed"
            jobs_store[job_id]["message"] = "Failed to generate video"
    
    except Exception as e:
        jobs_store[job_id]["status"] = "failed"
        jobs_store[job_id]["message"] = str(e)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/generate")
async def generate_video(payload: GenerateRequest, background_tasks: BackgroundTasks):
    """Submit a video generation job."""
    job_id = payload.job_id or str(uuid.uuid4())
    prompt = payload.prompt.strip()
    
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    
    jobs_store[job_id] = {
        "status": "queued",
        "message": "Job created",
        "prompt": prompt,
        "duration_seconds": payload.duration_seconds,
        "video_url": None,
        "video_path": None,
    }
    
    background_tasks.add_task(
        generate_video_background,
        job_id,
        prompt,
        payload.duration_seconds
    )
    
    return {"job_id": job_id}

@app.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_status(job_id: str):
    """Get job status."""
    job = jobs_store.get(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobStatusResponse(
        job_id=job_id,
        status=job["status"],
        message=job.get("message"),
        video_url=job.get("video_url"),
    )

@app.get("/download/{job_id}")
async def download_video(job_id: str):
    """Download the generated video file."""
    from fastapi.responses import FileResponse
    
    job = jobs_store.get(job_id)
    
    if not job or job["status"] != "done":
        raise HTTPException(status_code=404, detail="Video not available")
    
    video_path = job.get("video_path")
    if not video_path or not Path(video_path).exists():
        raise HTTPException(status_code=404, detail="Video file not found")
    
    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=f"{job_id}.mp4"
    )

@app.get("/")
async def root():
    return {
        "service": "video-worker",
        "endpoints": {
            "POST /generate": "Submit a video generation job",
            "GET /status/{job_id}": "Get job status",
            "GET /download/{job_id}": "Download video",
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8082)
