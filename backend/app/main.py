# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.video import router as video_router
from app.config import FRONTEND_ORIGIN

app = FastAPI(title="AI Video Backend")

origins = [
    FRONTEND_ORIGIN,
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(video_router)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {
        "service": "AI Video Generator Backend",
        "endpoints": {
            "POST /api/video/generate": "Submit a video generation job",
            "GET /api/video/status/{job_id}": "Get job status and video URL",
            "GET /api/video/file/{job_id}": "Download the generated video",
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
