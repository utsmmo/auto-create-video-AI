import os
import requests
import time
import uuid
from app.core.config import settings

class ImageGenerator:
    def __init__(self):
        # Pollinations.ai for FREE image generation
        self.base_url = "https://pollinations.ai/p/"
        self.output_dir = "static/outputs/images"
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        print(f"Khởi tạo ImageGenerator (Lưu tại: {self.output_dir})")

    async def generate(self, prompt: str, width: int = 1280, height: int = 720, seed: int = None):
        """
        Gửi request tạo ảnh đến Pollinations.ai và tải về lưu cục bộ
        """
        try:
            # Làm sạch prompt để đưa vào URL
            encoded_prompt = requests.utils.quote(prompt)
            
            # Cấu hình: width/height, seed=random nếu không có
            if seed is None:
                seed = int(time.time() * 1000)
                
            image_url = f"https://pollinations.ai/p/{encoded_prompt}?width={width}&height={height}&seed={seed}&nologo=true"
            
            print(f"🎨 Đang tạo ảnh ({width}x{height}): {prompt[:50]}...")
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            }
            
            # Tải ảnh từ API (có thử lại nếu trả về HTML)
            filename = f"gen_{uuid.uuid4().hex[:8]}.jpg"
            file_path = os.path.join(self.output_dir, filename)
            
            for attempt in range(3):
                response = requests.get(image_url, headers=headers, timeout=60)
                content_type = response.headers.get('Content-Type', '')
                
                if response.status_code == 200 and ('image' in content_type or 'binary/octet-stream' in content_type):
                    with open(file_path, "wb") as f:
                        f.write(response.content)
                    
                    # Trả về kết quả bao gồm link local để hiển thị trên Web
                    local_url = f"/static/outputs/images/{filename}"
                    
                    return {
                        "status": "success",
                        "message": "Ảnh đã được tải về thành công!",
                        "prompt": prompt,
                        "image_url": image_url,
                        "local_url": local_url,
                        "file_path": file_path,
                        "filename": filename
                    }
                else:
                    print(f"⚠️ Lần {attempt+1}: Content-Type là {content_type}, đang đợi AI xử lý...")
                    time.sleep(5)
            
            return {
                "status": "error", 
                "message": f"Server không trả về ảnh sau 3 lần thử (Status: {response.status_code}, Type: {content_type})"
            }
                
        except Exception as e:
            print(f"❌ Lỗi ImageGenerator: {str(e)}")
            return {"status": "error", "message": f"Lỗi: {str(e)}"}

generator = ImageGenerator()
