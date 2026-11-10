# Đường dẫn triển khai Support Ticket Router

Dự án **TMG301 – Multi-class Text Classification** được triển khai với frontend trên **Vercel** và backend trên **Render**.

## Website chính thức

**[Mở Support Ticket Router](https://tmg-301-final-project.vercel.app)**

Đây là địa chỉ truy cập giao diện React để nhập yêu cầu hỗ trợ, xem kết quả phân loại, phòng ban tiếp nhận, mức ưu tiên, SLA và các thống kê đánh giá mô hình.

| Thành phần | Nền tảng | Địa chỉ |
|---|---|---|
| Frontend React + TypeScript | Vercel | [tmg-301-final-project.vercel.app](https://tmg-301-final-project.vercel.app) |
| Backend Flask API | Render | [tmg301-final-project.onrender.com](https://tmg301-final-project.onrender.com) |
| Kiểm tra trạng thái backend và mô hình | Render | [/api/health](https://tmg301-final-project.onrender.com/api/health) |
| Mã nguồn | GitHub | [GnurTinz/TMG301_final_project](https://github.com/GnurTinz/TMG301_final_project) |

## Cách frontend kết nối với mô hình

```text
Người dùng
    → Frontend React trên Vercel
    → Flask API trên Render
    → Pipeline TF-IDF + LinearSVC
    → Kết quả trả về giao diện
```

Backend nạp checkpoint `model/saved_models/best_ticket_router_pipeline.joblib` khi khởi động và thực hiện suy luận trên máy chủ Render. Frontend gửi nội dung yêu cầu đến API và hiển thị kết quả; trình duyệt không tải checkpoint để chạy mô hình.

Các endpoint chính:

| Endpoint trên backend Render | Chức năng |
|---|---|
| `GET /api/health` | Kiểm tra backend và khả năng nạp mô hình |
| `POST /api/route-ticket` | Phân loại yêu cầu và trả về thông tin điều hướng |
| `GET /api/model-info` | Thông tin mô hình, nhãn và chỉ số đánh giá |
| `GET /api/dashboard-data` | Dữ liệu cho màn hình phân tích |
| `GET /plots/<filename>` | Các biểu đồ đánh giá đã lưu |

## Cấu hình kết nối khi triển khai

Frontend trên Vercel sử dụng biến môi trường:

```dotenv
VITE_API_BASE_URL=https://tmg301-final-project.onrender.com
```

Backend trên Render cho phép origin của frontend qua biến:

```dotenv
CORS_ORIGINS=https://tmg-301-final-project.vercel.app
```

Đây là các giá trị cần cấu hình trong môi trường hosting. `VITE_API_BASE_URL` được đưa vào frontend lúc build, nên cần build và triển khai lại frontend sau khi thay đổi. Backend đọc `CORS_ORIGINS` từ môi trường của tiến trình. Chi tiết nằm trong [README frontend/backend](web_app/frontend/README.md).

## Đường dẫn chạy cục bộ

| Thành phần | Địa chỉ mặc định |
|---|---|
| React frontend | http://127.0.0.1:5173 |
| Flask API và giao diện HTML | http://127.0.0.1:5050 |
| Flask dashboard | http://127.0.0.1:5050/dashboard |
| API health check | http://127.0.0.1:5050/api/health |

Xem [README chính](README.md) để cài dependencies và khởi động frontend/backend.
