import uvicorn
import sys
import os

# Thêm thư mục hiện tại vào PYTHONPATH để import app
sys.path.append(os.getcwd())

if __name__ == "__main__":
    print("🚀 Khởi động Veo 3 Video Creator Tool...")
    # Chạy FastAPI từ module app.main
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
