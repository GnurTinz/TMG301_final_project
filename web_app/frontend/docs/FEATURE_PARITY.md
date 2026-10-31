# Đối chiếu chức năng Gradio → React

Nguồn đối chiếu: Gradio Blocks, `route_ticket_gradio`, `get_benchmark_df`, `get_per_class_df` trong `app.py`; model inference trong `model/router_inference.py`; API Flask trong `web_app/app.py`.

| Chức năng hiện có | Đầu vào / đầu ra | Tương đương React | Cách kiểm tra |
|---|---|---|---|
| Nhập nội dung yêu cầu | Văn bản → cùng chuỗi được trim trước khi suy luận | Textarea, đếm ký tự, xóa nội dung | Browser validation + so sánh API/direct inference |
| Email khách hàng | Email tùy chọn; mặc định `customer@example.com` | Input có label, kiểm tra định dạng khi có nhập | Browser validation + API default email test |
| Năm Gradio Examples | Năm cặp nội dung/email | Năm nút điền mẫu, giữ đúng nội dung Gradio | Test AST đối chiếu literal Examples với API; browser kiểm tra cả năm |
| Phân loại và điều hướng | Nội dung → kết quả từ checkpoint | Nút submit và Ctrl/⌘ + Enter; Fetch đến API cũ | Browser gọi mô hình thật; API/direct/Gradio parity |
| Mã ticket, phòng ban và mã phòng ban | Chuỗi kết quả từ router | Thẻ kết quả, giữ nguyên mapping | So sánh routing decision giữa API và hàm gốc |
| Chủ đề, tên tiếng Việt | Technical Issue / Payment / Return/Refund | Tên tiếng Việt và nhãn gốc | API/direct/Gradio parity |
| Điểm tin cậy và điểm ba lớp | Softmax decision scores của router | Chỉ số và progress bars có aria labels | So sánh đúng các giá trị API, không tạo score mới |
| Ưu tiên và SLA | Từ khóa khẩn cấp, threshold 60%, mapping | Badge, số giờ làm việc | So sánh API/direct; test riêng ranh giới .59/.60 và ưu tiên khẩn cấp |
| Phản hồi xác nhận | Văn bản do router tạo | Văn bản có thể chọn, nút sao chép | Browser kiểm tra nội dung API và clipboard |
| Bảng KPI Analytics | Accuracy, Macro F1, dataset size, batch inference time | Bốn thẻ lấy dữ liệu từ API | Browser + API dashboard |
| Bảng so sánh bốn mô hình | Metrics của lần đánh giá đã lưu | Bảng, xếp theo Macro F1, highlight mô hình đầu | Browser kiểm tra bốn hàng, số liệu thật |
| Bảng chỉ số từng nhóm | Precision, Recall, F1 và support | Bảng theo nhóm, chọn được cả bốn mô hình | Browser chuyển LinearSVC/ComplementNB và kiểm tra metric/matrix |
| Năm biểu đồ và phóng to | PNG đã có trong model/plots | Gallery năm mục, native dialog; Escape để đóng | API kiểm tra đủ PNG; browser kiểm tra ảnh tải và dialog |
| Nội dung giải thích hiệu năng | Bối cảnh các metric và biểu đồ | Chú thích metric, mô tả biểu đồ, ghi chú phạm vi đánh giá | Đối chiếu với JSON/metadata đã lưu |

Lịch sử localStorage, xem lại ticket, nút xóa lịch sử và dashboard chọn mô hình cũng được giữ từ demo Flask. React bổ sung trạng thái loading, ngăn gửi trùng, thông báo lỗi có thể khôi phục, retry tải dữ liệu, focus indicators, label và live status.

Các khác biệt trình bày có chủ đích:

- Giao diện khởi đầu bằng form trống để phân biệt trạng thái chưa chạy với kết quả dự đoán. Năm mẫu luôn có sẵn để điền nhanh; mặc định mẫu được điền sẵn của Gradio không ảnh hưởng pipeline.
- Điểm softmax được ghi là **điểm tin cậy ước lượng**. Thời gian **0,0496 giây** là thời gian theo lô 5.994 mẫu, không được trình bày thành độ trễ của một request web.
- Bảng React đọc JSON/API thay vì sao chép các metric hardcode trong Gradio. Không lặp lại tuyên bố “Production Ready” từ giao diện cũ khi project chưa có benchmark vận hành.
- React dùng giao diện sáng thống nhất; các đoạn CSS thích nghi với theme của Gradio vẫn được giữ trong fallback gốc.
- Không có chức năng gửi email hoặc chuyển ticket thật sang CRM trong các giao diện này. Nội dung xác nhận và thông tin phân công vẫn là output của mô hình/quy tắc như trước.

Gradio `app.py`, inference, cấu hình model, checkpoint, training scripts, datasets, `Procfile` và `run_web_demo.bat` không được chỉnh sửa.
