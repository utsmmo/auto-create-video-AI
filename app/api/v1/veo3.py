from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
import uuid
import asyncio
import json

from services.browser_service import browser_service
from services.profile_manager import profile_manager
from generator import generator
from pipeline.video_pipeline import video_pipeline

router = APIRouter()

# Schema
class VideoRequest(BaseModel):
    prompt: str
    aspect: str = "169"
    provider: str = "flow"
    profile_id: Optional[str] = "4186fbb3-85d4-4d26-b2e8-ce84f773ff8c"
    project_url: Optional[str] = None

class ImageRequest(BaseModel):
    prompt: str
    aspect: str = "169"
    quantity: int = 1
    provider: str = "flow"
    profile_id: Optional[str] = "4186fbb3-85d4-4d26-b2e8-ce84f773ff8c"
    project_url: Optional[str] = None

class BatchImageRequest(BaseModel):
    prompts: List[str]
    aspect: str = "16:9"
    quantity: str = "x1"
    model: str = "Nano Banana 2"
    client_id: Optional[str] = "Default_PC"
    profile_id: Optional[str] = "4186fbb3-85d4-4d26-b2e8-ce84f773ff8c"
    provider: str = "flow"

# Logic Helper
async def process_generation(gen_type: str, prompt: str, aspect: str, quantity: int, provider: str, profile_id: str, project_url: str):
    aspect_map = {
        "16:9": {"w": 1280, "h": 720, "ratio": "16:9"},
        "4:3": {"w": 1024, "h": 768, "ratio": "4:3"},
        "1:1": {"w": 1024, "h": 1024, "ratio": "1:1"},
        "3:4": {"w": 768, "h": 1024, "ratio": "3:4"},
        "9:16": {"w": 720, "h": 1280, "ratio": "9:16"}
    }
    config = aspect_map.get(aspect, aspect_map["16:9"])
    results = []

    if provider in ["flow", "gpm"]:
        await browser_service.start(profile_id)
        if provider == "flow":
            url = project_url if project_url else "https://labs.google/fx/tools/flow"
            qty_str = f"x{quantity}" if isinstance(quantity, int) else quantity
            res = await browser_service.generate_google_flow(prompt, url, aspect=aspect, quantity=qty_str)
            if res["status"] == "success":
                profile_manager.deduct_credit(profile_id)
                results.append(res)
        else:
            for _ in range(min(quantity if isinstance(quantity, int) else 1, 5)):
                res = await browser_service.generate_image(prompt, config["w"], config["h"])
                if res["status"] == "success":
                    profile_manager.deduct_credit(profile_id)
                    results.append(res)
    else:
        for _ in range(min(quantity if isinstance(quantity, int) else 1, 5)):
            res = await generator.generate(prompt, config["w"], config["h"])
            if res["status"] == "success":
                results.append(res)
    return results

# Endpoints
@router.post("/image")
async def generate_image(request: ImageRequest):
    results = await process_generation(
        gen_type="image",
        prompt=request.prompt,
        aspect=request.aspect,
        quantity=request.quantity,
        provider=request.provider,
        profile_id=request.profile_id,
        project_url=request.project_url
    )
    if not results:
        raise HTTPException(status_code=500, detail="Failed to generate images")
    if request.quantity == 1 and len(results) == 1:
        res = results[0]
        if "file_path" in res and os.path.exists(res.get("file_path", "")):
            return FileResponse(res["file_path"])
        return res
    return {"status": "success", "images": results}

@router.post("/batch-image")
async def generate_batch_image(request: BatchImageRequest):
    """
    TẠO HÀNG LOẠT (SONG SONG) VỚI ĐỊNH DANH CLIENT (PROJECT ISOLATION)
    """
    if not request.prompts:
        raise HTTPException(status_code=400, detail="Danh sách prompt trống.")
    
    project_storage = "projects.json"
    saved_projects = {}
    if os.path.exists(project_storage):
        try:
            with open(project_storage, "r") as f:
                saved_projects = json.load(f)
        except: pass
    
    project_id = saved_projects.get(request.client_id)
    project_url = f"https://labs.google/fx/tools/flow/project/{project_id}" if project_id else None

    await browser_service.start(request.profile_id)
    
    tasks = []
    for p in request.prompts:
        tasks.append(browser_service.generate_google_flow(
            p, 
            project_url=project_url,
            gen_type="image",
            aspect=request.aspect,
            quantity=request.quantity,
            model=request.model
        ))
    
    print(f"🚀 [BATCH] {request.client_id} kích hoạt {len(tasks)} luồng song song...")
    responses = await asyncio.gather(*tasks)
    
    new_project_id = None
    for res in responses:
        if res.get("project_id"):
            new_project_id = res["project_id"]
            break
            
    if new_project_id and new_project_id != project_id:
        saved_projects[request.client_id] = new_project_id
        with open(project_storage, "w") as f:
            json.dump(saved_projects, f, indent=4)
        print(f"💾 Saved Project {new_project_id} for Client {request.client_id}")

    return {
        "status": "success",
        "client_id": request.client_id,
        "project_id": new_project_id or project_id,
        "results": responses
    }

@router.post("/video")
async def generate_video(request: VideoRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    background_tasks.add_task(video_pipeline.run, request.prompt)
    return {"status": "processing", "job_id": job_id, "message": "Video generation started in background."}
