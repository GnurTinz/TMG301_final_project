# Tổng hợp thay đổi

## File đã chỉnh sửa

| File tính từ project root | Thay đổi |
|---|---|
| `web_app/app.py` | Tái sử dụng Flask API: thêm health check, CORS allowlist, JSON validation, HTTP error JSON, tùy chọn `MODEL_PATH`/`HOST` và năm mẫu Gradio qua query parameter. Giữ các route HTML và mẫu Flask cũ. |
| `requirements.txt` | Bổ sung dependency Flask, vốn đã được backend sử dụng nhưng chưa có trong danh sách dependency. Giữ pin scikit-learn 1.7.2. |
| `README.md` | Bổ sung đường dẫn giao diện React và hướng dẫn chạy cục bộ. |

## File được tạo

```text
project/
├── run_backend_api.bat
├── run_frontend_dev.bat
└── web_app/
    ├── .env.example
    ├── tests/
    │   └── test_api.py
    └── frontend/
        ├── .env.example
        ├── .gitignore
        ├── README.md
        ├── index.html
        ├── package.json
        ├── package-lock.json
        ├── tsconfig.json
        ├── vite.config.ts
        ├── playwright.config.ts
        ├── public/
        │   └── favicon.svg
        ├── src/
        │   ├── App.tsx
        │   ├── main.tsx
        │   ├── components/
        │   │   ├── PredictionResult.tsx
        │   │   └── ui.tsx
        │   ├── hooks/
        │   │   ├── useHistory.ts
        │   │   ├── usePrediction.ts
        │   │   └── useResource.ts
        │   ├── pages/
        │   │   ├── AnalyticsPage.tsx
        │   │   └── RouterPage.tsx
        │   ├── services/
        │   │   └── predictionApi.ts
        │   ├── styles/
        │   │   └── index.css
        │   └── types/
        │       └── prediction.ts
        ├── tests/
        │   └── workspace.spec.ts
        └── docs/
            ├── IMPLEMENTATION.md
            ├── FEATURE_PARITY.md
            ├── VALIDATION.md
            └── screenshots/
                ├── router-desktop.png
                ├── router-result.png
                ├── analytics-desktop.png
                └── router-mobile.png
```

`node_modules/`, `dist/`, `test-results/` và Python bytecode là đầu ra cài đặt/build/test, không phải source cần commit. Các thư mục sinh bởi npm/Playwright được khai báo trong `.gitignore` của frontend.

## Cải thiện UI/UX

- Bố cục sáng, sidebar xanh lục đậm, typography và spacing thống nhất.
- Tách vùng nhập yêu cầu khỏi kết quả, có trạng thái chưa gửi, đang phân loại và đã phân loại.
- Dữ liệu thật từ API cho thẻ kết quả, dashboard và các biểu đồ.
- Form có label, validation, đếm ký tự, xóa nội dung và phím tắt.
- Khóa gửi trùng và hủy request khi component đóng/reset.
- Phân biệt lỗi mạng, timeout và lỗi backend; tải dữ liệu có thể retry.
- Score bars có label hỗ trợ accessibility, nội dung phản hồi có thể chọn/sao chép.
- Lịch sử trong trình duyệt, xem lại ticket, xóa lịch sử và xử lý lỗi storage.
- Bảng so sánh, chọn mô hình để xem chi tiết, gallery năm biểu đồ và dialog phóng to hỗ trợ Escape.
- Layout thích nghi desktop/tablet/mobile; bảng rộng cuộn riêng; mobile tự đưa vùng kết quả vào tầm nhìn sau khi phân loại.
- Skip link, focus indicators, semantic controls, trạng thái có thể đọc bởi công nghệ hỗ trợ và tôn trọng reduced motion.

## Phần được bảo toàn

Không chỉnh sửa `app.py` của Gradio, `model/`, dữ liệu, script training, ánh xạ nhãn, ngưỡng phân loại, checkpoint, `Procfile`, `run_web_demo.bat`, các template/static Flask cũ hoặc `report.md`. Không bổ sung database, authentication hoặc dịch vụ backend dư thừa.

Xem [README](../README.md) để biết kiến trúc, lệnh chạy chính xác và phương án triển khai sau này; xem [feature parity](FEATURE_PARITY.md) và [validation](VALIDATION.md) để đánh giá phạm vi và bằng chứng kiểm tra.
