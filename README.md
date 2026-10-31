# Support Ticket Router - CRM Điều Hướng Khiếu Nại Khách Hàng

> **Dự án Môn học**: TMG301 - Multi-class Text Classification  
> **Sinh viên thực hiện**: `gnurtinz`  
> **Mô hình**: Support Vector Machine (LinearSVC) & Naive Bayes  

---

## Giao diện React mới — chạy cục bộ

Giao diện React + TypeScript nằm trong `web_app/frontend`, sử dụng lại Flask API và checkpoint hiện có. Có hai màn hình: điều hướng yêu cầu và phân tích mô hình. Gradio trong `app.py`, demo Flask cũ và `run_web_demo.bat` vẫn được giữ nguyên.

1. Cài backend bằng môi trường Python `pyenv`: `& 'D:\InstalledApps\MiniConda\envs\pyenv\python.exe' -m pip install -r requirements.txt`.
2. Từ thư mục project, chạy `./run_backend_api.bat` trong terminal thứ nhất.
3. Chạy `./run_frontend_dev.bat` trong terminal thứ hai; lần đầu script sẽ cài npm dependencies.
4. Mở **http://127.0.0.1:5173**, chọn một mẫu thử rồi nhấn **Phân loại & điều hướng**.

Xem [hướng dẫn kiến trúc, cài đặt, kiểm thử và triển khai](web_app/frontend/README.md) cùng [bảng đối chiếu chức năng](web_app/frontend/docs/FEATURE_PARITY.md).

## Nội dung repository

Repository chứa source Python/React, dữ liệu đã xử lý, checkpoint, kết quả đánh giá, biểu đồ và các báo cáo [Checkpoint 1](report.md), [Report V2](reportV2.md). Có thể chạy demo bằng checkpoint hiện có mà không cần tải dữ liệu gốc hoặc train lại.

Dữ liệu gốc dung lượng lớn, dependencies, cache, file môi trường cá nhân và kết quả build/test được loại khỏi Git. Xem [hướng dẫn dữ liệu gốc](datasets/README.md) nếu cần tái lập xử lý dữ liệu hoặc EDA.

---

## 🌐 Đường Dẫn Demo Trực Tuyến 24/7 (Online Domain)

- 🔗 **Web Demo Trực Tiếp**: **[https://gnurtinz-tmg301-crm-router.hf.space](https://gnurtinz-tmg301-crm-router.hf.space)**  
- 📂 **Hugging Face Space**: **[https://huggingface.co/spaces/gnurtinz/tmg301-crm-router](https://huggingface.co/spaces/gnurtinz/tmg301-crm-router)**  
*(Xem thêm thông tin chi tiết tại file [DOMAIN_LINKS.md](DOMAIN_LINKS.md))*

---

## 📊 Kết Quả Đánh Giá Trên Tập Test (5,994 Mẫu Độc Lập)

| Hạng | Mô hình Machine Learning | Test Accuracy | Macro F1-Score | Weighted F1 | Training Time | Trạng thái |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| 🥇 | **Support Vector Machine (LinearSVC)** | **97.46%** | **97.19%** | **97.47%** | 0.50s | 🏆 *Production Ready* |
| 🥈 | **Logistic Regression (Baseline)** | **97.41%** | **97.14%** | **97.42%** | 0.72s | *Baseline chuẩn* |
| 🥉 | **Naive Bayes (MultinomialNB)** | **96.83%** | **96.45%** | **96.85%** | 0.31s | *Đã đánh giá* |
| 4 | **Naive Bayes (ComplementNB)** | **96.70%** | **96.35%** | **96.72%** | 0.31s | *Đã đánh giá* |

---

## 🚀 Hướng Dẫn Chạy Nhanh Trên Máy Cá Nhân

1. **Khởi động Web Demo**: Nhấp đúp chuột vào file [`run_web_demo.bat`](run_web_demo.bat).
2. **Huấn luyện lại mô hình**: Nhấp đúp chuột vào file [`run_training.bat`](run_training.bat).
