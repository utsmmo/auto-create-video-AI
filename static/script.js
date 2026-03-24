let currentMode = 'image';

// Chuyển đổi giữa Image và Video
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentMode = btn.dataset.mode;

        // Cập nhật UI tương ứng
        const imageOptions = document.getElementById('image-options');
        const promptLabel = document.getElementById('prompt-label');
        const btnText = document.getElementById('btn-text');
        const promptInput = document.getElementById('prompt');

        if (currentMode === 'video') {
            imageOptions.style.display = 'none';
            promptLabel.innerText = "Chủ đề Video (Topic)";
            promptInput.placeholder = "Ví dụ: Lịch sử thành cổ Loa, Hà Nội tương lai, Hướng dẫn nấu phở...";
            btnText.innerText = "Bắt đầu Tạo Video (Veo 3)";
        } else {
            imageOptions.style.display = 'grid';
            promptLabel.innerText = "Nhập mô tả ý tưởng (Prompt)";
            promptInput.placeholder = "Ví dụ: Một chiếc xích lô bay trên đường phố Hà Nội năm 2077...";
            btnText.innerText = "Tạo Hình Ảnh Ngay";
        }
    });
});

document.getElementById('generate-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const prompt = document.getElementById('prompt').value;
    const aspect = document.getElementById('aspect').value;
    const quality = document.getElementById('quality').value;

    const btn = document.getElementById('submit-btn');
    const loader = document.getElementById('loader');
    const placeholder = document.getElementById('placeholder');
    const resultImg = document.getElementById('result-image');
    const resultVid = document.getElementById('result-video');
    const statusText = document.getElementById('status-text');

    // UI Loading State
    btn.disabled = true;
    loader.style.display = 'block';
    placeholder.style.display = 'none';
    resultImg.style.display = 'none';
    resultVid.style.display = 'none';
    statusText.innerText = "Đang xử lý yêu cầu...";

    try {
        if (currentMode === 'image') {
            // Logic cho Image (Sync)
            const response = await fetch('/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt, aspect_ratio: aspect, quality })
            });
            const data = await response.json();
            if (data.status === 'success') {
                // Ưu tiên sử dụng link local từ server mình (ổn định hơn)
                resultImg.src = data.local_url || data.image_url;
                resultImg.style.display = 'block';
                statusText.innerText = "";
            } else {
                throw new Error(data.message);
            }
        } else {
            // Logic cho Video (Async - Polling)
            const response = await fetch('/api/v1/generate-video', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic: prompt })
            });
            const { job_id } = await response.json();
            pollStatus(job_id);
        }
    } catch (error) {
        console.error(error);
        statusText.innerText = "Lỗi: " + error.message;
        placeholder.style.display = 'block';
    } finally {
        if (currentMode === 'image') {
            btn.disabled = false;
            loader.style.display = 'none';
        }
    }
});

async function pollStatus(jobId) {
    const statusText = document.getElementById('status-text');
    const loader = document.getElementById('loader');
    const btn = document.getElementById('submit-btn');
    const resultVid = document.getElementById('result-video');
    const placeholder = document.getElementById('placeholder');

    const interval = setInterval(async () => {
        try {
            const response = await fetch(`/api/v1/status/${jobId}`);
            const data = await response.json();

            if (data.status === 'completed') {
                clearInterval(interval);
                statusText.innerText = "Hoàn tất! Đang tải video...";
                resultVid.src = data.final_video_url; // Thực tế sẽ là link video file
                resultVid.style.display = 'block';
                loader.style.display = 'none';
                btn.disabled = false;
            } else if (data.status === 'error') {
                clearInterval(interval);
                statusText.innerText = "Lỗi: " + data.message;
                loader.style.display = 'none';
                btn.disabled = false;
                placeholder.style.display = 'block';
            } else {
                statusText.innerText = "Đang render video... (Vui lòng đợi 1-2 phút)";
            }
        } catch (e) {
            console.error(e);
        }
    }, 3000);
}
