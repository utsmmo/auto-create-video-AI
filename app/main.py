from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from pydantic import BaseModel
from pipeline.video_pipeline import video_pipeline
from generator import generator # Maintain image generator
from typing import Dict
import uuid

app = FastAPI(title="Google Veo 3 Creative Suite")

# Lưu trữ trạng thái jobs (Vì video cần thời gian render)
jobs: Dict[str, dict] = {}

# Mount static folders
if not os.path.exists("static/outputs"):
    os.makedirs("static/outputs")

app.mount("/static", StaticFiles(directory="static"), name="static")

class GenerationRequest(BaseModel):
    prompt: str
    aspect_ratio: str = "1:1"
    quality: str = "high"

class VideoRequest(BaseModel):
    topic: str

@app.get("/health")
async def health():
    return {"status": "ok", "message": "Veo 3 Creator is running"}

@app.post("/generate")
async def generate_image(request: GenerationRequest):
    # Backward compatibility with original endpoint
    if not request.prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    result = await generator.generate(request.prompt)
    return result

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.post("/api/v1/generate-video")
async def generate_video(request: VideoRequest, background_tasks: BackgroundTasks):
    if not request.topic:
        raise HTTPException(status_code=400, detail="Topic is required")
    
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "processing", "topic": request.topic}
    
    # Chạy pipeline trong background (để tránh timeout HTTP)
    background_tasks.add_task(run_task, job_id, request.topic)
    
    return {"job_id": job_id, "status": "processing"}

@app.get("/api/v1/list-images")
async def list_images():
    image_dir = "static/outputs/images"
    if not os.path.exists(image_dir):
        return {"images": []}
    
    files = []
    for f in os.listdir(image_dir):
        if f.endswith(('.jpg', '.jpeg', '.png')):
            files.append({
                "filename": f,
                "url": f"/static/outputs/images/{f}",
                "path": os.path.join(image_dir, f)
            })
    return {"images": files[::-1]} # Mới nhất lên đầu

@app.get("/api/v1/status/{job_id}")
async def get_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]

async def run_task(job_id: str, topic: str):
    try:
        result = await video_pipeline.run(topic)
        jobs[job_id] = result
    except Exception as e:
        jobs[job_id] = {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
