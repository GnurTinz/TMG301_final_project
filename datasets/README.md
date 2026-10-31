# Dữ liệu gốc

Repository không chứa các file dữ liệu gốc trong thư mục này do tổng dung lượng trên máy phát triển khoảng **6,3 GB**. Các file vẫn được giữ trên máy; `.gitignore` chỉ loại chúng khỏi Git.

Source xử lý dữ liệu nằm trong `processing_datasets/`; các notebook và script khảo sát nằm trong `EDA/`. Dữ liệu đã xử lý trong `processed_datasets/`, checkpoint và kết quả đánh giá trong `model/` được đưa vào repository để chạy huấn luyện từ dữ liệu hợp nhất hoặc chạy demo với checkpoint hiện có.

## Chạy demo từ repository

Không cần tải dữ liệu gốc để chạy Flask API, React frontend hoặc Gradio với checkpoint đã lưu. Xem [README chính](../README.md) và [hướng dẫn frontend/backend](../web_app/frontend/README.md).

## Tái lập bước chuẩn bị dữ liệu và EDA

Banking77 có thể tải bằng script của project, chạy từ thư mục gốc:

```powershell
& 'D:\InstalledApps\MiniConda\envs\pyenv\python.exe' download_banking77.py
```

Script lấy dữ liệu từ [PolyAI task-specific-datasets](https://github.com/PolyAI-LDN/task-specific-datasets/tree/master/banking_data) và tạo:

```text
datasets/banking77/banking77_train.csv
datasets/banking77/banking77_test.csv
```

Để chạy lại các bước xử lý Bitext hoặc EDA trên các nguồn khác, cần cung cấp bộ dữ liệu tương ứng theo đường dẫn được khai báo trong `processing_datasets/process_bscs.py` và các script `EDA/run_eda_*.py`. Các nguồn đã khảo sát gồm Bitext Customer Support, Consumer Complaint Database và Twitter Customer Support. Kiểm tra điều kiện sử dụng của nguồn dữ liệu trước khi phân phối lại.
