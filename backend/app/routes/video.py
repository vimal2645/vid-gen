# backend/app/routes/video.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from app.models.schemas import GenerateVideoRequest, GenerateVideoResponse, JobStatusResponse
from app.services.groq_client import refine_prompt
from app.services.framepack_client import generate_video_with_framepack
from app.utils.storage import (
    create_job,
    set_job_running,
    set_job_done,
    set_job_failed,
    get_job,
    build_video_url,
    get_video_file_path,
)

router = APIRouter(prefix="/api/video", tags=["video"])

def _background_generate(job_id: str, refined_prompt: str, duration_seconds: int):
    try:
        set_job_running(job_id)
        video_path = generate_video_with_framepack(job_id, refined_prompt, duration_seconds)
        set_job_done(job_id, video_path)
    except Exception as e:
        set_job_failed(job_id, str(e))

@router.post("/generate", response_model=GenerateVideoResponse)
async def generate_video(payload: GenerateVideoRequest, background_tasks: BackgroundTasks):
    job_id = create_job()
    prompt = payload.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    refined = prompt
    if payload.refine_with_ai:
        refined = refine_prompt(prompt, payload.duration_seconds)

    background_tasks.add_task(_background_generate, job_id, refined, payload.duration_seconds)
    return GenerateVideoResponse(job_id=job_id)

@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    video_url = None
    if job["status"] == "done":
        video_url = build_video_url(job_id)

    return JobStatusResponse(
        job_id=job_id,
        status=job["status"],
        message=job.get("message"),
        video_url=video_url,
    )

@router.get("/file/{job_id}")
async def download_video(job_id: str):
    job = get_job(job_id)
    if not job or job["status"] != "done":
        raise HTTPException(status_code=404, detail="Video not available")
    file_path = get_video_file_path(job_id)
    return FileResponse(file_path, media_type="video/mp4", filename=f"{job_id}.mp4")
