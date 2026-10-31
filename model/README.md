# Công cụ Tự động Điều hướng Khiếu nại Khách hàng (Support Ticket Router)

> **Môn học**: TMG301 | **Nền tảng**: Multi-class Text Classification & Machine Learning  
> **Môi trường Conda**: `tmg_project`  
> **Định hướng sản phẩm**: Hệ thống CRM tự động đọc email/tin nhắn khiếu nại của khách hàng, phân loại chủ đề (*Lỗi kỹ thuật*, *Thanh toán*, *Đổi trả*) và chuyển tiếp đến đúng phòng ban xử lý kèm mức độ ưu tiên và thời hạn cam kết dịch vụ (SLA).

---

## 1. Cấu trúc Thư mục `model/`

```
model/
│
├── config.py                     # Cấu hình đường dẫn, tỷ lệ split, siêu tham số, mapping phòng ban CRM
├── train_ticket_router.py        # Pipeline huấn luyện, logging, tuning trên Val, learning curves và đánh giá Test
├── router_inference.py           # Module suy luận & demo hệ thống CRM tiếp nhận và định tuyến khiếu nại
│
├── saved_models/                 # Mô hình Machine Learning tốt nhất được xuất ra file
│   └── best_ticket_router_pipeline.joblib   # Pipeline gồm TF-IDF + LinearSVC + CRM Mappings
│
├── logs/                         # File nhật ký chi tiết quá trình huấn luyện
│   ├── training_latest.log       # Log của lần huấn luyện gần nhất
│   └── training_YYYYMMDD_HHMMSS.log
│
├── plots/                        # Toàn bộ biểu đồ trực quan hóa
│   ├── dataset_split_distribution.png       # Biểu đồ phân bố dữ liệu Train/Val/Test
│   ├── validation_curves.png                # Đồ thị Train vs Val khi tinh chỉnh siêu tham số
│   ├── learning_curves.png                  # Đồ thị Learning Curves (Bias - Variance)
│   ├── confusion_matrices_all_models.png    # Ma trận nhầm lẫn của tất cả các mô hình trên Test
│   └── model_comparison_metrics.png        # Biểu đồ cột so sánh Accuracy, F1, Precision, Recall
│
└── results/                      # Kết quả đánh giá dạng bảng & JSON
    ├── model_comparison_metrics.csv         # Bảng so sánh các chỉ số trên tập Test
    └── test_evaluation_summary.json         # Chi tiết kết quả kiểm thử và classification report
```

---

## 2. Dữ liệu Đầu vào & Phân chia Train / Val / Test

- **Nguồn dữ liệu**: Bộ dữ liệu hợp nhất `processed_datasets/combined_dataset.csv` (kết hợp từ Banking77 và BSCS - Bitext Customer Support) với tổng cộng **39,955 mẫu** văn bản thực tế.
- **Phương pháp phân chia**: **Stratified Split** với tỷ lệ **70% Train - 15% Validation - 15% Test**, cố định `random_state=42` để bảo đảm tỷ lệ giữa các lớp là tuyệt đối đồng đều trên cả 3 tập.

| Phân lớp (Label) | Chủ đề thực tế | Phòng ban điều hướng (CRM Department) | Train (70%) | Val (15%) | Test (15%) | Tổng cộng |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **Technical Issue** | Lỗi kỹ thuật | Phòng Hỗ trợ Kỹ thuật (`DEPT_TECH_SUPPORT`) | 16,059 | 3,442 | 3,442 | 22,943 (57.42%) |
| **Payment** | Thanh toán & Giao dịch | Phòng Kế toán & Thanh toán (`DEPT_BILLING_FINANCE`) | 7,706 | 1,652 | 1,652 | 11,010 (27.56%) |
| **Return/Refund** | Đổi trả & Hoàn tiền | Phòng CSKH & Đổi trả (`DEPT_CUSTOMER_CARE_REFUND`) | 4,202 | 900 | 900 | 6,002 (15.02%) |
| **Tổng cộng** | - | - | **27,967** | **5,994** | **5,994** | **39,955 (100%)** |

---

## 3. Quá trình Huấn luyện & Tối ưu Siêu tham số (Train & Validation)

### 3.1. Trích xuất Đặc trưng (Feature Extraction)
- Sử dụng **TF-IDF Vectorizer**:
  - `ngram_range=(1, 2)`: Khai thác cả unigram (từ đơn) và bigram (cụm 2 từ liền kề) để nắm bắt ngữ cảnh khiếu nại (ví dụ: *"wrong pin"*, *"not received"*, *"extra charge"*).
  - `sublinear_tf=True`: Áp dụng hàm logarit làm mượt tần suất từ, tránh các từ lặp lại nhiều lần lấn át đặc trưng quan trọng.
  - Kích thước từ vựng (Vocabulary size): **9,899 đặc trưng**.

### 3.2. Tinh chỉnh Siêu tham số trên tập Validation
Hệ thống thử nghiệm tìm kiếm siêu tham số tối ưu dựa trên điểm số **Macro F1-Score** trên tập Validation:
1. **MultinomialNB**: Thử nghiệm $\alpha \in [0.001, 0.01, 0.05, 0.1, 0.5, 1.0, 2.0]$.  
   $\rightarrow$ Tối ưu nhất tại $\alpha = 0.01$ (Val Acc: **97.08%**, Val Macro-F1: **96.79%**).
2. **ComplementNB**: Thử nghiệm $\alpha \in [0.001, 0.01, 0.05, 0.1, 0.5, 1.0, 2.0]$ (mô hình tối ưu hóa cho bài toán phân bố mất cân bằng).  
   $\rightarrow$ Tối ưu nhất tại $\alpha = 0.01$ (Val Acc: **97.21%**, Val Macro-F1: **96.94%**).
3. **LinearSVC (Support Vector Machine)**: Thử nghiệm tham số điều chuẩn $C \in [0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]$.  
   $\rightarrow$ Tối ưu nhất tại $C = 0.5$ (Val Acc: **97.56%**, Val Macro-F1: **97.37%**).
4. **Logistic Regression (Baseline)**: Thử nghiệm $C \in [0.01, 0.1, 0.5, 1.0, 5.0, 10.0]$.  
   $\rightarrow$ Tối ưu nhất tại $C = 5.0$ (Val Acc: **97.55%**, Val Macro-F1: **97.32%**).

### 3.3. Đồ thị Phân tích Learning Curves
Đồ thị `learning_curves.png` được vẽ qua 5 mức kích thước mẫu huấn luyện (từ 10% đến 100% tập Train):
- Khoảng cách giữa **Train Score** và **Validation Score** thu hẹp dần (từ 3.8% xuống còn ~1.6%).
- Cả hai đường hội tụ ở mức cao (>97%), chứng minh mô hình **không bị Overfitting** (High Variance) và **không bị Underfitting** (High Bias), có khả năng tổng quát hóa rất cao trên dữ liệu mới.

---

## 4. Kết quả Đánh giá trên Tập Test Độc Lập (5,994 mẫu unseen)

| Thứ hạng | Mô hình Machine Learning | Test Accuracy | Balanced Acc | Macro F1-Score | Weighted F1 | Macro Precision | Macro Recall | Thời gian Train |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 🥇 | **Support Vector Machine (LinearSVC)** | **97.46%** | **97.00%** | **97.19%** | **97.47%** | **97.41%** | **97.00%** | 0.50s |
| 🥈 | **Logistic Regression (Baseline)** | **97.41%** | **96.94%** | **97.14%** | **97.42%** | **97.36%** | **96.94%** | 0.72s |
| 🥉 | **Naive Bayes (MultinomialNB)** | **96.83%** | **96.33%** | **96.45%** | **96.85%** | **96.65%** | **96.33%** | 0.31s |
| 4 | **Naive Bayes (ComplementNB)** | **96.70%** | **96.57%** | **96.35%** | **96.72%** | **96.22%** | **96.57%** | 0.31s |

### Chi tiết Phân loại theo từng Phòng ban (Mô hình tốt nhất: LinearSVC)

- **Phòng Kế toán & Thanh toán (`Payment`)**:
  - Precision: **95.10%** | Recall: **96.37%** | F1-Score: **95.73%** | Support: 1,652 mẫu.
- **Phòng CSKH & Đổi trả (`Return/Refund`)**:
  - Precision: **98.86%** | Recall: **96.33%** | F1-Score: **97.58%** | Support: 900 mẫu.
- **Phòng Hỗ trợ Kỹ thuật (`Technical Issue`)**:
  - Precision: **98.26%** | Recall: **98.29%** | F1-Score: **98.27%** | Support: 3,442 mẫu.

---

## 5. Hướng dẫn Chạy & Thử nghiệm

### 1. Kích hoạt môi trường Conda
```bash
conda activate tmg_project
```

### 2. Chạy Huấn luyện & Đánh giá Toàn bộ Pipeline
```bash
python model/train_ticket_router.py
```
*Script sẽ tự động đọc dữ liệu, chia tập, tinh chỉnh siêu tham số trên Val, tính learning curves, đánh giá trên Test, xuất toàn bộ biểu đồ vào `model/plots/` và lưu mô hình vào `model/saved_models/`.*

### 3. Thử nghiệm Hệ thống CRM Điều hướng Khiếu nại Tự động (Inference Demo)
```bash
python model/router_inference.py
```
*Hệ thống sẽ chạy thử trên 5 email khiếu nại mẫu đại diện, tự động phân tích độ tin cậy, xác định phòng ban, mức độ ưu tiên và tạo mẫu phản hồi xác nhận cho khách hàng.*
