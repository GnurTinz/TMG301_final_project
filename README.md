# Support Ticket Router

Dự án môn **TMG301** về phân loại văn bản đa lớp, ứng dụng vào điều hướng yêu cầu hỗ trợ khách hàng. Hệ thống sử dụng **TF-IDF + LinearSVC** để phân loại nội dung, xác định phòng ban tiếp nhận, mức ưu tiên, SLA và tạo nội dung phản hồi xác nhận.

Giao diện chính dùng **React + TypeScript**, kết nối với **Flask API**. Repository có sẵn dữ liệu đã xử lý, checkpoint và kết quả đánh giá, cho phép chạy demo mà không cần tải dữ liệu gốc hoặc huấn luyện lại.

## Chức năng

| Nhãn dự đoán | Phòng ban tiếp nhận | SLA mặc định |
|---|---|---|
| `Technical Issue` | Hỗ trợ kỹ thuật | 12 giờ |
| `Payment` | Kế toán & Thanh toán | 4 giờ |
| `Return/Refund` | CSKH & Đổi trả | 6 giờ |

- Phân loại yêu cầu và hiển thị điểm của từng lớp.
- Xác định mức ưu tiên theo chủ đề, từ khóa khẩn cấp và ngưỡng điểm 60%. Từ khóa khẩn cấp được xét trước quy tắc yêu cầu người xử lý kiểm tra.
- Tạo mã ticket và nội dung phản hồi; lưu tối đa 20 ticket trong trình duyệt.
- Hiển thị bảng so sánh mô hình, chỉ số theo lớp và các biểu đồ đánh giá.

Dữ liệu huấn luyện là văn bản **tiếng Anh**; giao diện và nội dung phản hồi sử dụng tiếng Việt. Điểm của LinearSVC được tính bằng softmax trên decision scores, chưa phải xác suất đã hiệu chỉnh. Demo tạo kết quả điều hướng và mẫu phản hồi, chưa tích hợp gửi email hoặc chuyển ticket sang hệ thống CRM bên ngoài.

## Chạy cục bộ

Chạy các lệnh từ thư mục gốc repository trên Windows / PowerShell. Cần môi trường Conda **`pyenv`** và Node.js **22.12+** phù hợp với cấu hình frontend hiện tại.

### 1. Cài thư viện Python

```powershell
& 'D:\InstalledApps\MiniConda\envs\pyenv\python.exe' -m pip install -r requirements.txt
```

Đường dẫn trên là cấu hình máy phát triển. Nếu Conda nằm ở vị trí khác, thay bằng đường dẫn Python trong môi trường `pyenv` của bạn. Giữ **scikit-learn 1.7.2** theo `requirements.txt` để tương thích với checkpoint.

### 2. Khởi động Flask API

Trong terminal thứ nhất:

```powershell
.\run_backend_api.bat
```

Script mặc định dùng Python `pyenv` tại đường dẫn trên. Có thể đặt `$env:PYTHON_EXEC` trước khi chạy nếu interpreter nằm ở vị trí khác. API chạy tại **http://127.0.0.1:5050**; kiểm tra trạng thái tại **http://127.0.0.1:5050/api/health**.

### 3. Khởi động React frontend

Trong terminal thứ hai:

```powershell
.\run_frontend_dev.bat
```

Script tự cài npm dependencies nếu chưa có Vite. Mở **http://127.0.0.1:5173**, chọn một nội dung mẫu rồi nhấn **Phân loại & điều hướng**. Vite chuyển tiếp yêu cầu API đến backend ở cổng 5050.

Xem [README frontend](web_app/frontend/README.md) để cấu hình API, CORS, build và triển khai.

### Các giao diện khác

Backend Flask cũng phục vụ giao diện HTML tại **http://127.0.0.1:5050/** và dashboard tại **http://127.0.0.1:5050/dashboard**.

Để chạy Gradio riêng:

```powershell
& 'D:\InstalledApps\MiniConda\envs\pyenv\python.exe' app.py
```

Mở địa chỉ được Gradio in trong terminal. Hai script cũ `run_web_demo.bat` và `run_training.bat` còn tham chiếu môi trường `tmg_project`; các lệnh trong README này sử dụng `pyenv`.

## Dữ liệu và kết quả đánh giá

Tập dữ liệu hợp nhất gồm **39.955 mẫu** từ **Banking77** và **Bitext Customer Support (BSCS)**, ánh xạ về ba nhóm chủ đề. Pipeline chia dữ liệu theo tỷ lệ **70% train / 15% validation / 15% test**, có phân tầng theo nhãn và `random_state=42`.

TF-IDF sử dụng unigram và bigram. Bốn mô hình được tinh chỉnh trên tập validation; kết quả dưới đây lấy từ [bảng đánh giá đã lưu](model/results/model_comparison_metrics.csv) trên tập test **5.994 mẫu**.

| Mô hình | Accuracy | Macro F1 | Weighted F1 |
|---|---:|---:|---:|
| **LinearSVC** | **97,46%** | **97,19%** | **97,47%** |
| Logistic Regression | 97,41% | 97,14% | 97,42% |
| MultinomialNB | 96,83% | 96,45% | 96,85% |
| ComplementNB | 96,70% | 96,35% | 96,72% |

Đây là kết quả trên tập dữ liệu của dự án; cần đánh giá thêm trước khi áp dụng cho dữ liệu thực tế hoặc ngôn ngữ khác.

## Huấn luyện và suy luận

Huấn luyện lại từ dữ liệu hợp nhất có sẵn:

```powershell
& 'D:\InstalledApps\MiniConda\envs\pyenv\python.exe' model/train_ticket_router.py
```

Lệnh này cập nhật checkpoint, log, biểu đồ và kết quả trong `model/`. Để chạy thử suy luận với các yêu cầu mẫu:

```powershell
& 'D:\InstalledApps\MiniConda\envs\pyenv\python.exe' model/router_inference.py
```

Xem [hướng dẫn dữ liệu gốc](datasets/README.md) để tái lập bước xử lý dữ liệu hoặc EDA; xem [tài liệu mô hình](model/README.md) để biết cấu hình và đầu ra huấn luyện.

## Cấu trúc repository

```text
project/
├── app.py                       # Giao diện Gradio
├── datasets/README.md           # Hướng dẫn chuẩn bị dữ liệu gốc
├── EDA/                         # Notebook và script khảo sát dữ liệu
├── processing_datasets/         # Xử lý dữ liệu, ánh xạ nhãn và hợp nhất
├── processed_datasets/          # Dữ liệu đã xử lý
├── model/
│   ├── config.py                # Cấu hình dữ liệu, huấn luyện và CRM
│   ├── train_ticket_router.py   # Huấn luyện và đánh giá
│   ├── router_inference.py      # Suy luận và quy tắc điều hướng
│   ├── saved_models/            # Checkpoint TF-IDF + mô hình
│   ├── results/                 # Kết quả CSV, JSON
│   └── plots/                   # Biểu đồ đánh giá
├── web_app/
│   ├── app.py                   # Flask API và giao diện HTML
│   ├── frontend/                # React + TypeScript + Vite
│   ├── templates/               # Template Flask
│   ├── static/                  # CSS và JavaScript cho Flask
│   └── tests/                   # Kiểm thử API
├── requirements.txt
├── run_backend_api.bat
└── run_frontend_dev.bat
```

## Kiểm tra dự án

Kiểm thử Flask API:

```powershell
& 'D:\InstalledApps\MiniConda\envs\pyenv\python.exe' -m unittest discover -s web_app/tests -v
```

Kiểm tra TypeScript và build frontend sau khi cài npm dependencies:

```powershell
Set-Location web_app/frontend
npm.cmd run build
```

Hướng dẫn kiểm thử trình duyệt nằm trong [README frontend](web_app/frontend/README.md).

## Tài liệu và quy tắc Git

- [Cấu hình và vận hành frontend/backend](web_app/frontend/README.md).
- [Đối chiếu chức năng giao diện](web_app/frontend/docs/FEATURE_PARITY.md).
- [Kết quả đánh giá chi tiết](model/results/test_evaluation_summary.json).
- [Thông tin đường dẫn demo](DOMAIN_LINKS.md).

Thư mục `draft/` lưu báo cáo nháp như `report.md`, `reportV2.md` và được loại khỏi Git. Các thư mục presentation, dependencies phục vụ dựng slide và file PowerPoint cũng được ignore để giữ cục bộ. Dữ liệu gốc, môi trường cá nhân, cache, dependencies và kết quả build/test được loại trừ theo [`.gitignore`](.gitignore).
