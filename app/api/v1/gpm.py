from fastapi import APIRouter, HTTPException, Depends
from services.browser_service import browser_service
from services.profile_manager import profile_manager
from typing import Optional

router = APIRouter()

# Biến toàn cục để lưu trạng thái phiên làm việc (sử dụng cache hoặc state thay thế nếu muốn)
current_session = {"profile_id": None}

@router.post("/start/{profile_id}")
async def start_gpm_profile(profile_id: str):
    success = await browser_service.start(profile_id)
    if success:
        current_session["profile_id"] = profile_id
        return {"status": "success", "message": f"GPM Profile {profile_id} is active."}
    else:
        raise HTTPException(status_code=500, detail="Failed to start GPM profile")

@router.post("/stop")
async def stop_gpm_profile():
    profile_id = current_session["profile_id"]
    if profile_id:
        await browser_service.stop(profile_id)
        current_session["profile_id"] = None
        return {"status": "success", "message": f"GPM Profile {profile_id} stopped."}
    return {"status": "error", "message": "No active session."}
