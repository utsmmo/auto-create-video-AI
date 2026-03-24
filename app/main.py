from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os

# Import Routers
from app.api.v1.veo3 import router as veo3_router
from app.api.v1.gpm import router as gpm_router

app = FastAPI(title="Google Veo 3 Creative Suite")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static folders
if not os.path.exists("static/outputs/images"):
    os.makedirs("static/outputs/images")

app.mount("/static", StaticFiles(directory="static"), name="static")

# Include Routers
app.include_router(veo3_router, prefix="/veo3", tags=["Veo3 Generation"])
app.include_router(gpm_router, prefix="/gpm", tags=["GPM Browser Management"])

@app.get("/health")
async def health():
    return {"status": "ok", "message": "Veo 3 Creator is running with modular API."}

@app.get("/")
async def root():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
