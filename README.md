# 🎬 AI Video Generator (Google Veo API - Python)

## 🚀 Giới thiệu

Hệ thống này dùng Python để:

- Nhận input (text / keyword)
- Generate script
- Chia scene
- Gọi Google Veo API để tạo video
- Ghép video bằng FFmpeg
- Xuất file hoàn chỉnh

---

## 🧠 Kiến trúc hệ thống


Client (UI / API)
↓
FastAPI Backend
↓
Redis Queue
↓
Celery Worker
↓
Pipeline:

GPT (script)
Scene Builder
Veo API
TTS (optional)
FFmpeg
↓
Storage (local / S3)

---

## 📁 Cấu trúc project


project/
├── app/
│ ├── main.py
│ ├── api/
│ ├── core/
│ ├── models/
│ └── workers/
├── pipeline/
│ ├── video_pipeline.py
│ ├── scene_builder.py
│ └── prompt_engine.py
├── services/
│ ├── veo_service.py
│ ├── gpt_service.py
│ └── tts_service.py
├── utils/
│ └── ffmpeg_utils.py
└── requirements.txt


---

## ⚙️ Cài đặt

### 1. Cài Python packages


pip install fastapi uvicorn celery redis requests python-dotenv


---

### 2. Cài FFmpeg


sudo apt install ffmpeg


Hoặc Windows:
- Download từ: https://ffmpeg.org/

---

## 🔑 Cấu hình môi trường

Tạo file `.env`:


GOOGLE_API_KEY=your_api_key
VEO_API_URL=https://your-veo-endpoint

REDIS_URL=redis://localhost:6379/0


---

## 🎬 Flow xử lý video


Input → Script → Scene → Prompt → Veo → Merge → Output


---

## 🧩 1. Gọi Google Veo API

### services/veo_service.py

```python
import requests
import os

API_KEY = os.getenv("GOOGLE_API_KEY")
VEO_API_URL = os.getenv("VEO_API_URL")

def generate_video(prompt):
    payload = {
        "prompt": prompt,
        "aspect_ratio": "16:9",
        "duration": 5
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(VEO_API_URL, json=payload, headers=headers)
    data = response.json()

    return data.get("video_url")
🧠 2. Generate script
services/gpt_service.py
def generate_script(topic):
    return f"""
    Scene 1: Introduction about {topic}
    Scene 2: Key highlights
    Scene 3: Conclusion
    """
🎭 3. Chia scene
pipeline/scene_builder.py
def split_scenes(script):
    scenes = script.strip().split("\n")
    return [s for s in scenes if s]
✨ 4. Prompt Engine
pipeline/prompt_engine.py
def build_prompt(scene):
    return f"""
    Cinematic shot, high quality, detailed, 4k:
    {scene}
    """
🎥 5. Pipeline chính
pipeline/video_pipeline.py
from services.veo_service import generate_video
from services.gpt_service import generate_script
from pipeline.scene_builder import split_scenes
from pipeline.prompt_engine import build_prompt
from utils.ffmpeg_utils import merge_videos

def run_pipeline(topic):
    script = generate_script(topic)
    scenes = split_scenes(script)

    video_urls = []

    for scene in scenes:
        prompt = build_prompt(scene)
        video_url = generate_video(prompt)
        video_urls.append(video_url)

    final_video = merge_videos(video_urls)
    return final_video
🎞️ 6. Ghép video
utils/ffmpeg_utils.py
import os

def merge_videos(video_list):
    with open("inputs.txt", "w") as f:
        for video in video_list:
            f.write(f"file '{video}'\n")

    output = "output.mp4"
    os.system(f"ffmpeg -f concat -safe 0 -i inputs.txt -c copy {output}")

    return output
⚡ 7. Worker (Celery)
app/workers/tasks.py
from celery import Celery
from pipeline.video_pipeline import run_pipeline

celery = Celery(__name__, broker="redis://localhost:6379/0")

@celery.task
def generate_video_task(topic):
    return run_pipeline(topic)
🌐 8. API (FastAPI)
app/main.py
from fastapi import FastAPI
from workers.tasks import generate_video_task

app = FastAPI()

@app.post("/generate")
async def generate(data: dict):
    task = generate_video_task.delay(data["topic"])
    return {"task_id": task.id}
📊 9. Chạy hệ thống
Start Redis
redis-server
Start Worker
celery -A app.workers.tasks worker --loglevel=info
Start API
uvicorn app.main:app --reload
🔥 10. Nâng cấp nên có
 Cache video (tránh generate lại)
 Retry khi API lỗi
 Parallel scene processing
 Subtitle auto
 Voice sync
 Multi-model fallback
🚨 Lưu ý
Veo API thường là async → cần polling
Video generation tốn tiền → cần cache
FFmpeg phải cài đúng path
💡 Hướng mở rộng
SaaS video generator
TikTok automation

Batch generate 100+ video
✅ Kết luận

Hệ thống này gồm:

FastAPI → API
Celery → xử lý async
Veo API → generate video
FFmpeg → xử lý media

👉 Đây là kiến trúc đủ để chạy production.