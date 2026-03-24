# Google Labs Flow Automation API (Batch & Persistent)

Hệ thống cung cấp khả năng tự động hóa Google Labs Flow với các tính năng:
- **Xử lý song song**: Chạy nhiều prompt cùng lúc trên nhiều tab trình duyệt.
- **Project Isolation**: Mỗi định danh máy tính (`client_id`) sẽ được cấp và ghi nhớ một Project ID riêng.
- **Smart Wait**: Tự động phát hiện khi ảnh render xong (không dùng sleep cố định).
- **Base64**: Trả về dữ liệu ảnh trực tiếp dưới dạng chuỗi Base64.

---

## 🎨 1. Tạo ảnh hàng loạt (Parallel Batch)

**Endpoint:** `POST /veo3/batch-image`

### Request Body (JSON)
| Tham số | Kiểu | Mặc định | Mô tả |
| :--- | :--- | :--- | :--- |
| `prompts` | List[str] | Mandatory | Danh sách các câu lệnh tạo ảnh. |
| `aspect` | str | `16:9` | Tỉ lệ ảnh (`16:9`, `4:3`, `1:1`, `3:4`, `9:16`). |
| `quantity` | str | `x1` | Số lượng ảnh mỗi prompt (`x1`, `x2`, `x3`, `x4`). |
| `model` | str | `Nano Banana 2`| Tên model trên Google Labs Flow. |
| `client_id` | str | `Default_PC` | ID máy tính gửi yêu cầu (để cố định Project). |

### Example Request
```json
{
  "prompts": ["Con rồng lửa trên núi", "Lâu đài băng giá"],
  "aspect": "16:9",
  "quantity": "x4",
  "client_id": "PC_Z01"
}
```

### Response (JSON)
```json
{
  "status": "success",
  "client_id": "PC_Z01",
  "project_id": "6320735d-9028-4eba-9f62-11bd52e1c1fd",
  "results": [
    {
      "prompt": "Con rồng lửa trên núi",
      "images": [
        {"url": "...", "base64": "/9j/4AAQSkZ..."},
        {"url": "...", "base64": "..."},
        {"url": "...", "base64": "..."},
        {"url": "...", "base64": "..."}
      ],
      "project_id": "6320735d...",
      "status": "success"
    },
    ...
  ]
}
```

---

## 💾 Cơ chế Lưu trữ Project (Isolation)
1. **Lần đầu:** Nếu `PC_Z01` chưa có project, hệ thống tự động nhấn "New Project" trên Google.
2. **Lưu trữ:** ID của Project mới sẽ được lưu vào file `projects.json` tại thư mục gốc.
3. **Lần sau:** Mọi yêu cầu từ `PC_Z01` sẽ tự động mở đúng ID project đó.
4. **Nếu lỗi:** Nếu project bị xóa hoặc không truy cập được, hệ thống tự tạo project mới và cập nhật lại file `projects.json`.

---

## 🛠 Cách sử dụng (Test Script)
Bạn có thể chạy thử nghiệm bằng file `test_batch_advanced.py`:
```powershell
python test_batch_advanced.py
```
