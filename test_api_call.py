import requests
import os

def call_image_api(prompt):
    # Địa chỉ API của mình
    api_url = "http://localhost:8000/generate"
    
    print(f"🚀 Đang gọi API tạo ảnh cho: {prompt}")
    
    payload = {
        "prompt": prompt,
        "aspect_ratio": "16:9",
        "quality": "high"
    }
    
    try:
        response = requests.post(api_url, json=payload, timeout=60)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                print(f"✅ Thành công!")
                print(f"🔗 Link ảnh từ Pollinations: {data['image_url']}")
                print(f"🔗 Link ảnh lưu tại Server: http://localhost:8000{data['local_url']}")
                print(f"📂 File đã lưu tại: {data['file_path']}")
                return data
            else:
                print(f"❌ API trả về lỗi: {data.get('message')}")
        else:
            print(f"❌ Lỗi HTTP: {response.status_code}")
    except Exception as e:
        print(f"❌ Đã xảy ra lỗi: {e}")
    return None

if __name__ == "__main__":
    # Đảm bảo server đang chạy trước khi test: python main.py
    prompt_test = "A futuristic Vietnam city with flying cars, cinematic style"
    call_image_api(prompt_test)
