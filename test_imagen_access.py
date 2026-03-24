from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

def test_imagen():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ Không tìm thấy GOOGLE_API_KEY")
        return

    client = genai.Client(api_key=api_key)
    
    # Model Imagen 4.0 mới nhất vừa được liệt kê trong API
    model_name = "imagen-4.0-generate-001"
    
    print(f"🚀 Đang thử tạo ảnh với model: {model_name}...")
    
    try:
        response = client.models.generate_images(
            model=model_name,
            prompt="A futuristic city in Vietnam, cinematic, 8k",
            config={
                'number_of_images': 1,
            }
        )
        
        if response.generated_images:
            print("✅ Thành công! Đã tạo được ảnh.")
            # Lưu ảnh để kiểm tra
            output_path = "test_imagen_result.png"
            # Trong SDK plural, generated_images là list và mỗi item có thuộc tính .image (PIL object)
            response.generated_images[0].image.save(output_path)
            print(f"📂 Đã lưu ảnh tại: {output_path}")
        else:
            print("❌ Không có ảnh nào được trả về.")
            
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")
        print("Hệ thống có thể không có quyền truy cập Imagen 3 hoặc model name sai.")

if __name__ == "__main__":
    test_imagen()
