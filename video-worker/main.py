from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uuid
import torch
import os

# Disable xformers to avoid DLL issues on Windows
os.environ["DISABLE_XFORMERS"] = "1"

from diffusers import DiffusionPipeline
from pathlib import Path

app = FastAPI(title="🎬 Free AI Video Generator - ZeroScope")

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

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
pipe = None

def load_model():
    """Load ZeroScope model"""
    global pipe
    if pipe is not None:
        return
    
    print(f"📦 Loading ZeroScope model on {DEVICE}...")
    try:
        pipe = DiffusionPipeline.from_pretrained(
            "cerspense/zeroscope_v2_576w",
            torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
        )
        pipe = pipe.to(DEVICE)
        print("✅ Model loaded!")
    except Exception as e:
        print(f"❌ Model load error: {e}")
        raise

class GenerateRequest(BaseModel):
    prompt: str
    num_frames: int = 24
    job_id: Optional[str] = None

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    message: Optional[str] = None
    video_url: Optional[str] = None

def generate_video_background(job_id: str, prompt: str, num_frames: int):
    """Generate video in background"""
    try:
        jobs_store[job_id]["status"] = "running"
        jobs_store[job_id]["message"] = "🤖 Loading model..."
        
        load_model()
        
        jobs_store[job_id]["message"] = f"🎬 Generating {num_frames} frames..."
        
        with torch.no_grad():
            result = pipe(
                prompt,
                negative_prompt="low quality, blurry",
                num_frames=num_frames,
                num_inference_steps=20,
                guidance_scale=7.5,
            )
        
        frames = result.frames[0]
        
        # Save as GIF
        output_file = OUTPUT_DIR / f"{job_id}.gif"
        frames[0].save(
            str(output_file),
            save_all=True,
            append_images=frames[1:],
            duration=100,
            loop=0,
        )
        
        jobs_store[job_id]["status"] = "done"
        jobs_store[job_id]["message"] = "✅ Video ready!"
        jobs_store[job_id]["video_url"] = f"/download/{job_id}"
        jobs_store[job_id]["video_path"] = str(output_file)
        
        print(f"✅ Video generated: {job_id}")
        
    except Exception as e:
        jobs_store[job_id]["status"] = "failed"
        jobs_store[job_id]["message"] = f"❌ {str(e)[:50]}"
        print(f"Error: {e}")

@app.on_event("startup")
async def startup():
    print("🚀 Service starting...")

@app.get("/health")
async def health():
    return {
        "status": "✅ OK",
        "device": DEVICE,
        "gpu": torch.cuda.is_available()
    }

@app.post("/generate")
async def generate(payload: GenerateRequest, bg: BackgroundTasks):
    """Submit video generation job"""
    job_id = payload.job_id or str(uuid.uuid4())
    prompt = payload.prompt.strip()
    
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt required")
    
    num_frames = max(8, min(payload.num_frames, 48))
    
    jobs_store[job_id] = {
        "status": "queued",
        "message": "⏳ Queued...",
        "prompt": prompt,
        "video_url": None,
        "video_path": None,
    }
    
    bg.add_task(generate_video_background, job_id, prompt, num_frames)
    
    return {
        "job_id": job_id,
        "message": "📹 Generation started",
        "status_url": f"/status/{job_id}"
    }

@app.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_status(job_id: str):
    """Get job status"""
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
async def download(job_id: str):
    """Download video"""
    from fastapi.responses import FileResponse
    
    job = jobs_store.get(job_id)
    if not job or job["status"] != "done":
        raise HTTPException(status_code=404, detail="Video not ready")
    
    video_path = Path(job.get("video_path"))
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        video_path,
        media_type="image/gif",
        filename=f"{job_id}.gif"
    )

@app.get("/")
async def root():
    return {
        "service": "🎬 ZeroScope AI Video Generator",
        "model": "cerspense/zeroscope_v2_576w",
        "device": DEVICE,
        "endpoints": {
            "POST /generate": "Generate video",
            "GET /status/{job_id}": "Check status",
            "GET /download/{job_id}": "Download video",
            "GET /health": "Health check"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8082)
