# Support Ticket Router

Dự án môn **TMG301** về phân loại văn bản đa lớp, ứng dụng vào điều hướng yêu cầu hỗ trợ khách hàng. Hệ thống sử dụng **TF-IDF + LinearSVC** để phân loại nội dung, xác định phòng ban tiếp nhận, mức ưu tiên, SLA và tạo nội dung phản hồi xác nhận.

Giao diện chính dùng **React + TypeScript**, kết nối với **Flask API**. Repository có sẵn dữ liệu đã xử lý, checkpoint và kết quả đánh giá, cho phép chạy demo mà không cần tải dữ liệu gốc hoặc huấn luyện lại. Mô hình chạy trên CPU, không yêu cầu GPU.

Thông tin website demo và cấu hình hosting: [Đường dẫn triển khai](DOMAIN_LINKS.md).

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

## Cài đặt và chạy

### Yêu cầu

- Git để clone repository.
- **Python 3.11** là phiên bản đã được kiểm tra với checkpoint hiện có; cần `pip` để cài thư viện.
- **Node.js 22.12+** và npm để chạy giao diện React.

Bạn có thể dùng môi trường Python riêng bằng Conda hoặc công cụ quản lý môi trường khác. Các lệnh dưới đây dùng `python` trỏ đến interpreter trong môi trường đã kích hoạt, không yêu cầu tên môi trường hay đường dẫn cài đặt cụ thể. Trên hệ thống dùng tên lệnh `python3`, thay `python` tương ứng.

### 1. Clone repository và cài thư viện Python

```sh
git clone https://github.com/GnurTinz/TMG301_final_project.git
cd TMG301_final_project
python -m pip install -r requirements.txt
```

Giữ **scikit-learn 1.7.2** theo `requirements.txt` để tương thích với checkpoint. Các bước tiếp theo chạy từ thư mục gốc repository, trừ khi có lệnh chuyển thư mục.

### 2. Khởi động Flask API

Trong terminal thứ nhất, với môi trường Python đã kích hoạt:

```sh
python web_app/app.py
```

API chạy tại **http://127.0.0.1:5050**. Mở **http://127.0.0.1:5050/api/health** để kiểm tra; khi nạp được checkpoint, API trả `status: "ready"` và `model_ready: true`.

### 3. Khởi động React frontend

Mở terminal thứ hai tại thư mục gốc repository:

```sh
cd web_app/frontend
npm ci
npm run dev
```

Mở **http://127.0.0.1:5173**, chọn một nội dung mẫu rồi nhấn **Phân loại & điều hướng**. Vite chuyển tiếp yêu cầu API đến backend ở cổng 5050. Cần giữ cả hai terminal đang chạy; dùng `Ctrl+C` để dừng từng server.

Trên Windows PowerShell, nếu `npm` bị chặn do execution policy, dùng `npm.cmd` thay cho `npm` trong các lệnh trên.

### Checkpoint đi kèm

File [`model/saved_models/best_ticket_router_pipeline.joblib`](model/saved_models/best_ticket_router_pipeline.joblib) chứa pipeline **TF-IDF + LinearSVC**, danh sách nhãn, ánh xạ phòng ban và metadata đánh giá. Backend tự nạp file này khi khởi động; không cần huấn luyện lại để chạy demo.

Nếu API báo mô hình chưa sẵn sàng, kiểm tra file checkpoint có trong bản clone, phiên bản scikit-learn và log khởi động backend. Có thể dùng biến môi trường `MODEL_PATH` để chọn checkpoint khác.

### Các giao diện khác

Backend Flask cũng phục vụ giao diện HTML tại **http://127.0.0.1:5050/** và dashboard tại **http://127.0.0.1:5050/dashboard**.

Để chạy Gradio riêng:

```sh
python app.py
```

Mở địa chỉ được Gradio in trong terminal. Giao diện Flask và Gradio sử dụng cùng checkpoint với React.

## Cấu hình và API

Cấu hình mặc định cho phép chạy frontend/backend cùng máy mà không cần tạo file `.env`.

| Biến môi trường | Thành phần | Ý nghĩa |
|---|---|---|
| `HOST` | Backend | Địa chỉ bind; mặc định `0.0.0.0`. Đặt `127.0.0.1` nếu chỉ muốn truy cập từ máy đang chạy. |
| `PORT` | Backend | Cổng HTTP, mặc định `5050`. |
| `MODEL_PATH` | Backend | Đường dẫn checkpoint thay thế; bỏ trống để dùng file đi kèm repo. |
| `CORS_ORIGINS` | Backend | Các origin được phép, phân cách bằng dấu phẩy; mặc định cho phép localhost/127.0.0.1 ở cổng 5173 và 4173. |
| `API_PROXY_TARGET` | Vite | Đích proxy khi phát triển, mặc định `http://127.0.0.1:5050`. |
| `VITE_API_BASE_URL` | Frontend | Origin API khi gọi trực tiếp, không thêm `/api`; mặc định dùng URL tương đối qua proxy. |

Backend đọc biến từ môi trường tiến trình, không tự nạp file `.env`. Với frontend, có thể sao chép [`web_app/frontend/.env.example`](web_app/frontend/.env.example) thành `.env.local` trong cùng thư mục, chỉnh giá trị và khởi động lại Vite. Khi triển khai frontend riêng, đặt `VITE_API_BASE_URL` trước khi build và cấu hình `CORS_ORIGINS` ở backend theo origin frontend.

| Endpoint | Chức năng |
|---|---|
| `GET /api/health` | Kiểm tra trạng thái backend và mô hình. |
| `POST /api/route-ticket` | Phân loại ticket và trả thông tin điều hướng. |
| `GET /api/model-info` | Thông tin mô hình, nhãn và chỉ số đánh giá. |
| `GET /api/samples?source=gradio` | Các nội dung mẫu để thử dự đoán. |
| `GET /api/dashboard-data` | Dữ liệu đánh giá cho dashboard. |
| `GET /plots/<filename>` | Biểu đồ đánh giá đã lưu. |

Body JSON cho `POST /api/route-ticket`:

```json
{
  "message": "I returned the shoes but have not received my refund.",
  "customer_email": "customer@example.com"
}
```

`message` là bắt buộc; `customer_email` có thể bỏ qua. Kết quả thành công có dạng `{ "success": true, "data": { ... } }`, gồm nhãn, điểm, phòng ban, mức ưu tiên, SLA và mẫu phản hồi. API trả HTTP 400 khi dữ liệu đầu vào không hợp lệ, HTTP 503 nếu mô hình chưa sẵn sàng.

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

```sh
python model/train_ticket_router.py
```

Lệnh này cập nhật checkpoint, log, biểu đồ và kết quả trong `model/`. Để chạy thử suy luận với các yêu cầu mẫu:

```sh
python model/router_inference.py
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
├── requirements.txt             # Thư viện Python
└── DOMAIN_LINKS.md              # Đường dẫn và cấu hình triển khai
```

## Kiểm tra dự án

Kiểm thử Flask API:

```sh
python -m unittest discover -s web_app/tests -v
```

Kiểm tra TypeScript và build frontend sau khi cài npm dependencies:

```sh
cd web_app/frontend
npm run build
```

Build kiểm tra kiểu TypeScript và tạo bundle trong `web_app/frontend/dist/`. Hướng dẫn kiểm thử trình duyệt và cấu hình triển khai chi tiết nằm trong [README frontend](web_app/frontend/README.md).

## Tài liệu liên quan

- [Cấu hình và vận hành frontend/backend](web_app/frontend/README.md).
- [Đối chiếu chức năng giao diện](web_app/frontend/docs/FEATURE_PARITY.md).
- [Kết quả đánh giá chi tiết](model/results/test_evaluation_summary.json).
- [Thông tin đường dẫn demo](DOMAIN_LINKS.md).
- [Chuẩn bị dữ liệu gốc và EDA](datasets/README.md).
- [Cấu hình mô hình và đầu ra huấn luyện](model/README.md).

Dữ liệu gốc không đi kèm repository. Dữ liệu đã xử lý, checkpoint và kết quả đánh giá được lưu trong Git; môi trường cá nhân, cache, dependencies và kết quả build/test được loại trừ theo [`.gitignore`](.gitignore).
