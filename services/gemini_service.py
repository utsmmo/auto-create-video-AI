import os
from google import genai
from app.core.config import settings
import json

class GeminiService:
    @property
    def client(self):
        if not settings.GOOGLE_API_KEY:
            return None
        return genai.Client(api_key=settings.GOOGLE_API_KEY)

    async def generate_script(self, topic: str):
        if not self.client:
            raise Exception("Vui lòng cấu hình GOOGLE_API_KEY trong file .env để sử dụng tính năng này.")
        
        """
        Tạo kịch bản và phân cảnh cho video ngắn (30-60s)
        """
        prompt = f"""
        Tạo kịch bản video AI cho chủ đề: "{topic}".
        Hãy chia kịch bản thành các phân cảnh (scenes). 
        Mỗi phân cảnh cần: 
        1. "narration": Lời thoại thuyết minh.
        2. "visual_prompt": Mô tả chi tiết hình ảnh cho AI Gen Video (Veo) - bằng tiếng Anh.
        3. "duration": Thời lượng (thường là 5 giây).

        Hãy trả về định dạng JSON list.
        Ví dụ:
        [
          {{"scene": 1, "narration": "...", "visual_prompt": "Cinematic shot of...", "duration": 5}},
          ...
        ]
        """
        
        response = self.client.models.generate_content(
            model="gemini-1.5-pro",
            contents=prompt,
            config={
                'response_mime_type': 'application/json'
            }
        )
        
        return json.loads(response.text)

gemini_service = GeminiService()
