# Báo cáo kiểm tra migration React

Ngày kiểm tra: **31/10/2026**. Đây là kết quả thực thi cục bộ, sử dụng checkpoint hiện có. Không huấn luyện lại và chưa deploy.

## Kết quả

| Hạng mục | Lệnh / cách kiểm tra | Kết quả |
|---|---|---|
| TypeScript | `npm.cmd run build` chạy `tsc --noEmit` trước build | Qua, không có lỗi kiểu dữ liệu |
| Production build | `npm.cmd run build` | Qua, Vite 7.3.7 sinh `dist/` |
| Backend | Python `-m unittest discover -s web_app/tests -v` | **12/12 bài kiểm tra qua** |
| Trình duyệt | `npm.cmd run test:e2e` | **10/10 bài kiểm tra qua**; lần cuối 12,9 giây |
| Tính nhất quán suy luận | API vs direct inference vs callback Gradio với năm mẫu gốc | **5/5 khớp** nhãn, điểm, mapping, ưu tiên và SLA |
| Accessibility | axe-core, các rule `wcag2a`, `wcag2aa`, `wcag21aa` | Không phát hiện vi phạm ở trạng thái form trống, kết quả và dashboard desktop |
| Responsive | Kiểm tra ở độ rộng 360, 390, 768, 1024, 1440 px | Không tràn ngang trang; bảng rộng cuộn trong khung |
| Ảnh giao diện | Ảnh chụp bằng browser thật; xem lại desktop và mobile | Đã tạo bốn ảnh trong `docs/screenshots/` |

Bundle production cuối có JavaScript khoảng **269,00 kB / gzip 83,13 kB**, CSS khoảng **35,79 kB / gzip 8,47 kB**. Đây là kích thước build, không phải đo hiệu năng mạng hoặc tốc độ tải thực tế.

Môi trường thực thi: Windows, Node.js 24.18.0, React 19.3.1, TypeScript 5.9.3, Tailwind 4.3.3, Playwright 1.64.1 và Microsoft Edge được cài trên máy. Python chạy bằng Conda `pyenv`; Flask 3.1.3, scikit-learn **1.7.2**. Môi trường ban đầu có scikit-learn 1.9.0; đã cài đúng 1.7.2 theo `requirements.txt` trước khi kiểm tra chính thức.

## Phạm vi backend

Bộ unittest đã thực thi các kiểm tra sau:

- Checkpoint nạp thành công; request dùng lại instance router đã nạp khi khởi động.
- Health check, model info, dashboard JSON và đủ năm PNG trả response thành công.
- `/` và `/dashboard` của demo Flask cũ tiếp tục trả HTTP 200.
- Nội dung năm mẫu từ API đúng với literal `gr.Examples` trong `app.py`.
- Với từng mẫu, API trả `routing_decision` giống hoàn toàn direct inference. Các score đã làm tròn khớp chính xác, không dùng tolerance hoặc score giả.
- Callback `route_ticket_gradio` gốc trả cùng điểm từng lớp; HTML chứa cùng category, tên tiếng Việt, phòng ban, mã phòng ban, priority và confidence đã định dạng.
- Phản hồi API khớp direct inference khi cố định mã ticket; nội dung phòng ban khớp callback Gradio.
- Input trống, JSON sai, body không phải object và field sai kiểu được trả 400.
- Email mặc định, trim khoảng trắng, ngưỡng .59/.60 và ưu tiên khẩn cấp giữ đúng hành vi inference.
- Health/model info/prediction trả 503 khi mô hình không sẵn sàng.
- CORS preflight, CORS trên response lỗi, origin ngoài allowlist, API 404/405 dạng JSON được kiểm tra.

Để kiểm tra callback Gradio mà không dựng toàn bộ UI/GPU decorator, unittest trích đúng FunctionDef của `route_ticket_gradio` từ AST của `app.py`, bỏ decorator và thực thi với router thật. Bộ test không khởi động Gradio Blocks hoặc môi trường Hugging Face. Source Gradio được giữ nguyên.

## Phạm vi trình duyệt

Các test thành công sử dụng **React → HTTP API Flask → checkpoint thật**. Chỉ các test lỗi mạng/máy chủ tạo response lỗi cô lập bằng Playwright interception.

- Form trống, required validation, email sai định dạng và chọn đủ năm mẫu.
- Kết quả phân loại thật, đúng score trên progress bar, phòng ban và nội dung phản hồi theo response HTTP.
- Clipboard thực tế, nội dung xuống dòng và xác nhận sao chép. Test chuẩn hóa CRLF/LF để tính đến clipboard Windows.
- Lưu lịch sử, reload trang, mở lại ticket, xóa form và xóa lịch sử.
- Loading state, vô hiệu hóa input/nút khi đang chạy, chống gửi trùng và Ctrl + Enter.
- Lỗi API 503, lỗi mạng và khôi phục bằng request thật.
- Bảng bốn mô hình, đổi mô hình kiểm tra, metric theo lớp và confusion matrix.
- Tải được năm ảnh biểu đồ, mở dialog, đóng bằng Escape.
- Lỗi dashboard và nút retry.
- Luồng phân loại trên mobile; kiểm tra lại trang sau khi có lịch sử và đổi màn hình.
- localStorage có JSON hỏng hoặc bị chặn không làm hỏng quá trình suy luận.
- Dialog hướng dẫn sử dụng, ảnh chụp và không có `pageerror` ngoài dự kiến trong luồng chụp.
- Kiểm tra axe-core trên ba trạng thái chính; đã sửa các vấn đề tương phản chữ và ARIA được phát hiện trong quá trình thực hiện.

Lỗi tràn ngang từng xuất hiện ở label ẩn của bảng lịch sử sau khi đổi viewport. Đã đặt containing block cho vùng cuộn bảng; lần kiểm tra cuối và ảnh mobile xác nhận trang không còn tràn ngang.

## Ảnh chụp

- [Workspace desktop](screenshots/router-desktop.png)
- [Kết quả thật](screenshots/router-result.png)
- [Dashboard desktop](screenshots/analytics-desktop.png)
- [Workspace mobile](screenshots/router-mobile.png)

## Giới hạn kiểm tra

- Bộ trình duyệt đã chạy trên Microsoft Edge/Chromium; chưa thực thi Firefox, Safari hoặc trên thiết bị di động thật.
- Kiểm tra accessibility tự động không thay thế đánh giá bằng screen reader và người dùng thực tế.
- Build production đã thành công; các E2E chạy với Vite development server. Chưa kiểm tra một môi trường hosting public.
- Chưa chạy lại toàn bộ Gradio UI, chưa kiểm thử tải đồng thời hoặc benchmark RAM trên hosting.
- Cách tính confidence, dữ liệu tiếng Anh, hệ thống ba nhãn và giới hạn tổng quát hóa của mô hình được giữ như project gốc.
- Giao diện React hiện dùng theme sáng. Gradio fallback vẫn giữ CSS thích nghi theme gốc.

Không còn bài kiểm tra tự động thất bại trong bộ kiểm tra cuối. Các server do Playwright khởi tạo đã được dừng sau khi hoàn tất.
