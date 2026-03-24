import asyncio
import os
import sys

# Thêm thư mục hiện tại vào sys.path để import generator
sys.path.append(os.getcwd())

async def test_direct():
    from generator import generator
    
    test_prompt = "A beautiful sunset over Ha Long Bay, cinematic, 8k, realistic"
    print(f"--- Đang test trực tiếp generator.py ---")
    print(f"Prompt: {test_prompt}")
    
    result = await generator.generate(test_prompt)
    
    if result['status'] == 'success':
        print(f"✅ THÀNH CÔNG!")
        print(f"Local URL: {result['local_url']}")
        print(f"File Path: {result['file_path']}")
        
        # Kiểm tra sự tồn tại của file
        if os.path.exists(result['file_path']):
            print(f"📂 File đã tồn tại trên đĩa: {os.path.getsize(result['file_path'])} bytes")
        else:
            print(f"❌ LỖI: File không tìm thấy sau khi tải!")
    else:
        print(f"❌ THẤT BẠI: {result['message']}")

if __name__ == "__main__":
    asyncio.run(test_direct())
