from services.gemini_service import gemini_service
from services.veo_service import veo_service
from app.core.config import settings
import os
import asyncio
import time

class VideoPipeline:
    def __init__(self):
        self.output_dir = settings.OUTPUT_DIR
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    async def run(self, topic: str):
        # 1. Tạo kịch bản (Scripting)
        print(f"🎬 Đang viết kịch bản cho: {topic}")
        scenes = await gemini_service.generate_script(topic)
        
        video_clips = []
        
        # 2. Tạo từng scene video (Veo 3)
        print(f"🎥 Đang tạo {len(scenes)} phân cảnh bằng Veo 3...")
        for scene in scenes:
            print(f"--- Đang tạo Scene {scene['scene']}: {scene['visual_prompt']}")
            video_url = await veo_service.generate_video(scene['visual_prompt'])
            video_clips.append({
                "url": video_url,
                "narration": scene['narration'],
                "duration": scene.get('duration', 5)
            })
            
            # (Phần sau sẽ thêm FFmpeg để ghép clips - Temporary dummy merge)
        
        # 3. Ghép video (Sẽ gọi FFmpeg tại đây)
        # Giả lập kết quả cuối cùng là ghép các link này lại.
        
        final_video_name = f"final_video_{int(time.time())}.mp4"
        final_video_path = os.path.join(self.output_dir, final_video_name)
        
        return {
            "status": "completed",
            "topic": topic,
            "scenes": video_clips,
            "final_video_url": f"/{self.output_dir}/{final_video_name}"
        }

video_pipeline = VideoPipeline()
