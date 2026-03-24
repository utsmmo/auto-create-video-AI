import asyncio
from playwright.async_api import async_playwright
import os
import requests
import time

async def generate_single_image(context, index, prompt):
    save_dir = r"d:\AutoCode\AutoCreateVideo\Image\Test_10_Browser"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    file_path = os.path.join(save_dir, f"hanoi_2077_{index:02d}.jpg")
    
    # URL với seed khác nhau để ảnh không bị trùng
    encoded_prompt = requests.utils.quote(prompt)
    url = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=576&seed={index}&nologo=true"
    
    page = await context.new_page()
    print(f"[{index:02d}] Đang bắt đầu tạo ảnh...")
    
    try:
        # Truy cập trang
        await page.goto(url, wait_until="networkidle", timeout=60000)
        
        # Đợi AI vẽ (Khoảng 5 giây là an toàn cho model Flux)
        await asyncio.sleep(7) 
        
        # Chụp màn hình để lấy ảnh
        await page.screenshot(path=file_path)
        print(f" ✅ [{index:02d}] Thành công: {file_path}")
        return True
    except Exception as e:
        print(f" ❌ [{index:02d}] Thất bại: {e}")
        return False
    finally:
        await page.close()

async def main():
    prompt = "A breathtaking view of Hanoi in 2077, cyberpunk city, neon lights, flying cars, 4k"
    
    print(f"--- BẮT ĐẦU TẠO 10 ẢNH BẰNG BROWSER ---")
    start_time = time.time()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        
        # Chạy 3 ảnh cùng lúc (Parallel) để tăng tốc nhưng không làm sập server
        batch_size = 3
        for i in range(1, 11, batch_size):
            tasks = []
            for j in range(i, min(i + batch_size, 11)):
                tasks.append(generate_single_image(context, j, prompt))
            
            await asyncio.gather(*tasks)
            print(f"--- Đã xong đợt {i} - {min(i + batch_size - 1, 10)} ---")
            await asyncio.sleep(2) # Nghỉ 2 giây giữa các đợt

        await browser.close()
    
    end_time = time.time()
    print(f"\n--- HOÀN THÀNH ---")
    print(f"Tổng thời gian: {end_time - start_time:.2f} giây")
    print(f"Thư mục lưu: d:\\AutoCode\\AutoCreateVideo\\Image\\Test_10_Browser")

if __name__ == "__main__":
    asyncio.run(main())
