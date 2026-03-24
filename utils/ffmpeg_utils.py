import os
import subprocess
from app.core.config import settings

def merge_videos(video_list, output_name):
    """
    Sử dụng FFmpeg để ghép các clip video thành một file duy nhất.
    """
    output_path = os.path.join(settings.OUTPUT_DIR, output_name)
    
    # Tạo file inputs.txt cho FFmpeg concat
    inputs_file = "inputs.txt"
    with open(inputs_file, "w") as f:
        for video in video_list:
            # Nếu truyền link URL, FFmpeg cần xử lý khác hoặc tải về.
            # Ở đây chúng ta giả sử video đã được tải về cục bộ.
            f.write(f"file '{video}'\n")

    try:
        # Command concatenate videos
        # -f concat: Dùng mode nối file
        # -safe 0: Cho phép dùng đường dẫn tuyệt đối
        # -c copy: Copy stream (không re-encode) để nhanh hơn
        cmd = f"ffmpeg -y -f concat -safe 0 -i {inputs_file} -c copy {output_path}"
        subprocess.run(cmd, shell=True, check=True)
        
        # Xóa file tạm
        if os.path.exists(inputs_file):
            os.remove(inputs_file)
            
        return output_path
    except Exception as e:
        print(f"Error merging videos: {e}")
        return None
