import requests
import os
import time
from concurrent.futures import ThreadPoolExecutor

def download_image(index):
    save_dir = r"d:\AutoCode\AutoCreateVideo\Image\Test_100"
    prompt = f"Futuristic Hanoi city in 2077, variation {index}, neon lights, cinematic"
    encoded_prompt = requests.utils.quote(prompt)
    
    # Sử dụng seed khác nhau cho mỗi ảnh để đảm bảo ảnh không trùng
    image_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=576&seed={index}&model=flux&nologo=true"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    
    file_path = os.path.join(save_dir, f"hanoi_2077_{index:03d}.jpg")
    
    try:
        # Thử lại tối đa 3 lần nếu server bận
        for attempt in range(3):
            response = requests.get(image_url, headers=headers, timeout=30)
            if response.status_code == 200 and 'image' in response.headers.get('Content-Type', ''):
                with open(file_path, "wb") as f:
                    f.write(response.content)
                print(f"[{index:03d}] Tải thành công ({len(response.content)} bytes)")
                return True
            else:
                print(f"[{index:03d}] Lần thử {attempt+1} thất bại (Status: {response.status_code}). Đang đợi...")
                time.sleep(2) # Đợi 2 giây trước khi thử lại
    except Exception as e:
        print(f"[{index:03d}] Lỗi: {e}")
    return False

def main():
    save_dir = r"d:\AutoCode\AutoCreateVideo\Image\Test_100"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    print("--- BẮT ĐẦU TEST GIỚI HẠN 100 ẢNH ---")
    start_time = time.time()
    
    # Sử dụng ThreadPoolExecutor để tải nhanh hơn (5 luồng cùng lúc để tránh làm quá tải server quá mức)
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(download_image, range(1, 101)))
    
    end_time = time.time()
    success_count = sum(1 for r in results if r)
    
    print("\n--- KẾT QUẢ ---")
    print(f"Tổng số yêu cầu: 100")
    print(f"Thành công: {success_count}")
    print(f"Thất bại: {100 - success_count}")
    print(f"Thời gian thực hiện: {end_time - start_time:.2f} giây")
    print(f"Thư mục: {save_dir}")

if __name__ == "__main__":
    main()
