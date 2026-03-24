import requests
import os

def test_save_image():
    # Thư mục lưu trữ
    save_dir = r"d:\AutoCode\AutoCreateVideo\Image\Test"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    image_url = "https://picsum.photos/1280/720"
    
    print(f"Đang tải ảnh từ: {image_url}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"
    }
    
    try:
        response = requests.get(image_url, headers=headers)
        if response.status_code == 200:
            # Kiểm tra xem content-type có phải là image không
            content_type = response.headers.get('Content-Type', '')
            if 'image' in content_type:
                file_path = os.path.join(save_dir, "hanoi_2077_test.jpg")
                with open(file_path, "wb") as f:
                    f.write(response.content)
                print(f"Thành công! Ảnh đã được lưu tại: {file_path}")
                print(f"Kích thước file: {len(response.content)} bytes")
            else:
                print(f"Lỗi: Server không trả về ảnh (Trả về {content_type}). Thử lại...")
                # Nếu trả về HTML, có thể cần đợi 1 chút để AI render
        else:
            print(f"Lỗi khi tải ảnh: {response.status_code}")
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")

if __name__ == "__main__":
    test_save_image()
