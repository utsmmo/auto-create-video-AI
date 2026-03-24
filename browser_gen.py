import asyncio
from playwright.async_api import async_playwright
import os
import requests
import time

async def generate_with_browser(prompt: str, filename: str):
    save_dir = r"d:\AutoCode\AutoCreateVideo\Image\Test_Browser"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    file_path = os.path.join(save_dir, filename)
    
    async with async_playwright() as p:
        # Mở trình duyệt ẩn danh
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # URL tạo ảnh
        encoded_prompt = requests.utils.quote(prompt)
        url = f"https://pollinations.ai/p/{encoded_prompt}?width=1280&height=720&nologo=true"
        
        print(f"Đang mở trình duyệt để tạo: {prompt}")
        
        try:
            # Truy cập trang
            await page.goto(url, wait_until="networkidle", timeout=60000)
            
            # Đợi thêm một chút để AI thực sự render xong ảnh
            await asyncio.sleep(5) 
            
            # Chụp ảnh màn hình của cả trang (vì trang này chỉ chứa mỗi tấm ảnh)
            # Hoặc lấy buffer ảnh trực tiếp nếu nó là image element
            await page.screenshot(path=file_path)
            
            print(f"Thành công! Đã lưu ảnh qua Browser tại: {file_path}")
            return True
        except Exception as e:
            print(f"Lỗi Browser: {e}")
            return False
        finally:
            await browser.close()

async def main():
    prompt = "A majestic dragon flying over futuristic Hanoi, 8k, cinematic"
    await generate_with_browser(prompt, "dragon_hanoi_browser.jpg")

if __name__ == "__main__":
    asyncio.run(main())
