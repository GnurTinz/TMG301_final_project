# Project Progress Report V2 — Support Ticket Router

**Môn học:** TMG301  
**Tên dự án:** Hệ thống tự động phân loại và định tuyến yêu cầu hỗ trợ khách hàng  
**Ngày cập nhật:** 31/10/2026  
**Báo cáo đối chiếu:** Checkpoint 1 — `report.md`  
**Hình thức nộp:** Nhóm thống nhất cử **một đại diện** nộp báo cáo này thay mặt toàn bộ nhóm.

## 1. Current Project Status

### 1.1. Completed Tasks and Milestones

Dự án hiện đã hoàn thành nguyên mẫu tích hợp từ xử lý dữ liệu, huấn luyện mô hình đến giao diện web và kiểm thử. Hệ thống nhận nội dung yêu cầu hỗ trợ, phân loại vào ba nhóm **Technical Issue**, **Payment**, **Return/Refund**, sau đó tạo thông tin định tuyến gồm phòng ban phụ trách, mức ưu tiên, SLA và phản hồi xác nhận.

So với Checkpoint 1, cột mốc chính của phiên bản hiện tại là **hoàn thành giao diện React kết nối với mô hình thật thông qua API Flask hiện có**, đồng thời bổ sung kiểm thử tự động và tài liệu bàn giao. Các công việc đã hoàn thành bao gồm:

| Hạng mục | Kết quả hiện tại |
|---|---|
| Khảo sát dữ liệu | Có notebook và script EDA cho Banking77, Bitext Customer Support, Consumer Complaint Database và Twitter Customer Support. |
| Chuẩn bị dữ liệu huấn luyện | Ánh xạ 77 nhãn Banking77 và 27 intent Bitext về ba nhóm, hợp nhất thành **39.955 mẫu**. |
| Huấn luyện và đánh giá | Hoàn thành TF-IDF unigram/bigram, tinh chỉnh siêu tham số và so sánh bốn mô hình học máy. |
| Lưu mô hình và kết quả | Có checkpoint LinearSVC, log huấn luyện, kết quả CSV/JSON và năm biểu đồ đánh giá. |
| Hiện đại hóa giao diện | Hoàn thành React, Vite, TypeScript, Tailwind CSS và Lucide React trong `web_app/frontend`. |
| Tích hợp hệ thống | React sử dụng lại Flask API và `CRMTicketRouter`; giữ Gradio cùng demo Flask cũ làm phương án sử dụng bổ sung. |
| Kiểm thử và bàn giao | Hoàn thành kiểm thử backend, trình duyệt, đối chiếu suy luận, build production, script Windows và tài liệu hướng dẫn. |

Dữ liệu vẫn được chia theo tỷ lệ **70% training, 15% validation, 15% test**, tương ứng **27.967 / 5.994 / 5.994 mẫu**. Cách chia stratified duy trì gần tương đương tỷ lệ các lớp giữa các tập. Sau khi tinh chỉnh, các cấu hình được huấn luyện lại trên **33.961 mẫu training + validation** để đánh giá trên tập test.

Kiến trúc sử dụng hiện tại là:

```text
Người dùng → React Frontend → Flask API → CRMTicketRouter
                                         ↓
                                  TF-IDF + LinearSVC
                                         ↓
         Kết quả phân loại, điểm tin cậy, phòng ban, ưu tiên, SLA, phản hồi
```

Mô hình được nạp một lần khi backend khởi động. Giao diện và API tiếp tục sử dụng tiền xử lý, dự đoán, ánh xạ nhãn và các quy tắc nghiệp vụ đã có trong project.

### 1.2. Implemented Features and Functionalities

**Không gian điều hướng yêu cầu:** Người dùng nhập nội dung, cung cấp email nếu có hoặc chọn một trong năm mẫu gốc của Gradio. Form có đếm ký tự, xóa nội dung, kiểm tra đầu vào và phím tắt **Ctrl/⌘ + Enter**. Hệ thống hiển thị trạng thái đang phân loại và ngăn gửi trùng trong khi request đang chạy.

**Kết quả phân loại và phân công:** Giao diện hiển thị mã ticket, nhãn tiếng Anh và tiếng Việt, điểm tin cậy, điểm của cả ba nhóm, phòng ban, mã phòng ban, ưu tiên và SLA. Quy tắc nghiệp vụ hiện tại gồm:

| Nhóm yêu cầu | Phòng ban phụ trách | Ưu tiên mặc định | SLA cấu hình |
|---|---|---|---:|
| Technical Issue | Hỗ trợ kỹ thuật | Medium | 12 giờ làm việc |
| Payment | Kế toán và thanh toán | High | 4 giờ làm việc |
| Return/Refund | Chăm sóc khách hàng và đổi trả | High | 6 giờ làm việc |

Từ khóa khẩn cấp có thể nâng ưu tiên lên `Urgent`. Nếu không có từ khóa khẩn cấp và điểm tin cậy dưới 60%, yêu cầu được gắn `Needs Human Review`. Các giá trị và ngưỡng này được giữ từ implementation gốc.

**Phản hồi và lịch sử:** Hệ thống tạo nội dung xác nhận để xem hoặc sao chép. Giao diện lưu tối đa **20 yêu cầu gần đây** trong trình duyệt, cho phép mở lại kết quả và xóa lịch sử. Nếu trình duyệt chặn lưu trữ, kết quả suy luận hiện tại vẫn được hiển thị.

**Dashboard phân tích mô hình:** Người dùng xem bảng so sánh bốn mô hình, lựa chọn mô hình để kiểm tra Precision, Recall, F1-score, số mẫu từng nhóm và confusion matrix. Thư viện gồm năm biểu đồ đánh giá đã có, hỗ trợ phóng to và mở ảnh gốc. Dashboard lấy số liệu từ API và file kết quả của project.

**Khả năng sử dụng và vận hành:** Giao diện thích nghi với desktop, tablet và mobile; có focus indicators, label, hỗ trợ bàn phím và thông báo trạng thái. API có health check, kiểm tra JSON, phản hồi lỗi rõ ràng và CORS theo danh sách origin cấu hình. Frontend và backend có thể chạy độc lập bằng script Windows mới.

Hiện tại, chức năng định tuyến tạo **thông tin phân công và nội dung phản hồi** trên giao diện/API. Project chưa tích hợp gửi email thực tế hoặc chuyển ticket sang một hệ thống CRM bên ngoài. Phiên bản React đã chạy và được kiểm tra cục bộ; chưa triển khai lên hosting public.

### 1.3. Current Results and Performance

**Kết quả mô hình.** Các số liệu dưới đây được kế thừa từ lần thực nghiệm lưu ngày **23/10/2026**, trên **5.994 mẫu test**:

| Mô hình | Accuracy | Macro F1 | Weighted F1 |
|---|---:|---:|---:|
| **LinearSVC** | **97,46%** | **97,19%** | **97,47%** |
| Logistic Regression | 97,41% | 97,14% | 97,42% |
| MultinomialNB | 96,83% | 96,45% | 96,85% |
| ComplementNB | 96,70% | 96,35% | 96,72% |

LinearSVC tiếp tục được dùng cho demo, với **5.842/5.994 mẫu phân loại đúng** và Balanced Accuracy **97,00%**. F1-score theo nhóm lần lượt là **95,73%** cho Payment, **97,58%** cho Return/Refund và **98,27%** cho Technical Issue.

Thời gian suy luận đã ghi nhận của LinearSVC là khoảng **0,0496 giây cho cả lô 5.994 mẫu**. Đây là phép đo pipeline theo lô, chưa bao gồm độ trễ giao diện, truyền tải mạng hoặc nhiều người dùng đồng thời.

**Kết quả tích hợp và kiểm thử.** Trong giai đoạn nâng cấp giao diện, nhóm không huấn luyện lại hoặc thay đổi mô hình. Vì vậy, báo cáo không ghi nhận mức tăng Accuracy hay Macro F1 mới; kết quả nổi bật là duy trì hành vi phân loại và kiểm chứng luồng sử dụng mới:

| Hạng mục kiểm tra | Kết quả đã thực thi |
|---|---|
| Backend và API | **12/12 bài kiểm tra qua**. |
| Trình duyệt và tích hợp | **10/10 bài kiểm tra qua**, gồm luồng React → Flask → checkpoint thật. |
| Đối chiếu năm mẫu Gradio | **5/5 khớp** nhãn, điểm, mapping, ưu tiên và SLA giữa API, lời gọi suy luận trực tiếp và callback Gradio gốc. |
| TypeScript và production build | Hoàn thành kiểm tra kiểu dữ liệu và build Vite thành công. |
| Responsive | Kiểm tra ở độ rộng **360, 390, 768, 1024, 1440 px**; không tràn ngang trang trong các tình huống đã kiểm tra. |
| Accessibility tự động | axe-core không phát hiện vi phạm thuộc các rule WCAG 2 A/AA và WCAG 2.1 AA đã chạy trên form trống, kết quả và dashboard desktop. |

Các bài kiểm tra trình duyệt sử dụng Microsoft Edge/Chromium. Đối chiếu Gradio thực thi callback gốc với router thật, chưa khởi chạy lại toàn bộ Gradio Blocks. Kiểm tra tự động cũng chưa thay thế đánh giá bằng screen reader, thiết bị di động thật hoặc môi trường vận hành public.

## 2. Improvements Since Checkpoint 1

### 2.1. New Features and Modules Added

Thay đổi lớn nhất sau Checkpoint 1 là bổ sung **frontend React độc lập** và tổ chức giao diện thành hai màn hình rõ ràng: điều hướng yêu cầu và phân tích mô hình. Các chức năng phân loại, SLA, phản hồi và biểu đồ vốn đã có được chuyển sang trải nghiệm React, kết nối trực tiếp với backend hiện có.

Các module mới gồm:

- **Frontend theo component:** tách form, kết quả, dashboard và các thành phần dùng chung để thuận tiện bảo trì.
- **Lớp API tập trung và kiểu TypeScript:** mô tả đúng response Flask, gom xử lý Fetch, timeout 30 giây, lỗi mạng và lỗi backend.
- **Các hook quản lý trạng thái:** tải dữ liệu có thể hủy, quản lý suy luận, ngăn gửi trùng và lưu lịch sử.
- **Health check và cấu hình tích hợp:** thêm `/api/health`, CORS allowlist và tùy chọn cấu hình đường dẫn model, host, port.
- **Bộ kiểm thử tự động:** thêm unittest cho API và Playwright cho thao tác người dùng, tích hợp mô hình, responsive và accessibility.
- **Bộ tài liệu bàn giao:** bổ sung đối chiếu chức năng, tổng hợp thay đổi, báo cáo kiểm thử, ảnh giao diện, file env mẫu và script chạy Windows.

Flask API đã tồn tại từ Checkpoint 1 và được mở rộng để phục vụ React; dự án không tạo thêm backend FastAPI hoặc dịch vụ suy luận riêng.

### 2.2. Improvements to Existing Components

| Thành phần | Tại Checkpoint 1 | Sau nâng cấp |
|---|---|---|
| Giao diện sử dụng | Gradio và các trang HTML Flask phục vụ demo. | Thêm ứng dụng React với bố cục và phong cách thống nhất; giữ các giao diện cũ. |
| Luồng nhập và xem kết quả | Đã nhập nội dung, phân loại và hiển thị thông tin định tuyến. | Bổ sung trải nghiệm form trống, loading, validation, chống gửi trùng, phím tắt và phản hồi khi có lỗi. |
| Analytics | Đã có bảng chỉ số và năm biểu đồ. | Trình bày lại bằng React, lấy dữ liệu từ API, chọn mô hình kiểm tra và phóng to biểu đồ. |
| Lịch sử | Demo Flask đã lưu lịch sử bằng localStorage. | Chuyển sang React, hỗ trợ mở lại ticket và xử lý lỗi lưu trữ. |
| API | Đã có các endpoint phục vụ demo. | Bổ sung readiness, kiểm tra kiểu dữ liệu, JSON lỗi và CORS cấu hình. |
| Kiểm chứng hệ thống | Đã có kết quả đánh giá mô hình và log huấn luyện. | Bổ sung bằng chứng kiểm thử API, trình duyệt, tính nhất quán suy luận và accessibility. |
| Khởi động và bàn giao | Có script chạy training/demo và tài liệu mô hình. | Thêm script backend/frontend riêng, cấu hình env mẫu và hướng dẫn build/deployment. |

### 2.3. Fixed Issues and Resolved Challenges

Trong quá trình tích hợp và kiểm thử, nhóm đã xử lý các vấn đề sau:

| Vấn đề | Cách xử lý và kết quả |
|---|---|
| Phiên bản thư viện chưa tương thích checkpoint | Môi trường `pyenv` ban đầu dùng scikit-learn 1.9.0 trong khi checkpoint lưu bằng 1.7.2. Đã đồng bộ về **1.7.2** theo dependency của project trước khi kiểm tra chính thức. |
| Dependency backend chưa đầy đủ | Bổ sung Flask vào `requirements.txt` để việc cài đặt phản ánh đúng backend đang sử dụng. |
| JSON hoặc field sai kiểu có thể làm endpoint xử lý không phù hợp | Kiểm tra body phải là object và các field phải là chuỗi; trả HTTP 400 cho dữ liệu không hợp lệ, 503 khi model chưa sẵn sàng. |
| Tương tác thiếu phản hồi khi request chậm hoặc thất bại | Hiển thị loading, khóa gửi trùng, phân biệt lỗi mạng/backend, đặt timeout và cung cấp retry cho dữ liệu có thể tải lại. |
| Bảng lịch sử gây tràn ngang sau khi đổi viewport | Điều chỉnh vùng chứa và cuộn của bảng; kiểm tra lại trên mobile sau khi đã có lịch sử. |
| Chữ dashboard thiếu tương phản và ARIA chưa phù hợp | Tăng cỡ chữ, điều chỉnh màu và sửa role/label theo kết quả axe-core. Bộ kiểm tra accessibility cuối đã qua. |
| Lưu trữ trình duyệt bị hỏng hoặc bị chặn | Kiểm tra dữ liệu lịch sử và bắt lỗi storage; kết quả suy luận vẫn hiển thị được. |
| Clipboard Windows chuẩn hóa xuống dòng | Điều chỉnh phép so sánh CRLF/LF trong kiểm thử để kiểm tra đúng nội dung sao chép, giữ nguyên văn bản phản hồi của mô hình. |

### 2.4. Enhancements in Overall Project Quality

Phiên bản hiện tại cải thiện chủ yếu ở **khả năng sử dụng, độ tin cậy của tích hợp và khả năng bảo trì**. Người dùng có luồng thao tác rõ hơn, đọc kết quả thuận tiện hơn trên nhiều kích thước màn hình và nhận được hướng dẫn xử lý khi thao tác thất bại. Kiến trúc frontend tách khỏi AI giúp có thể điều chỉnh giao diện mà không phải thay đổi pipeline suy luận.

Về chất lượng kỹ thuật, TypeScript giúp kiểm tra các kiểu dữ liệu trong frontend; bộ test tạo bằng chứng cho các tình huống sử dụng chính và khả năng giữ nguyên đầu ra mô hình. Dashboard cũng trình bày rõ điểm tin cậy là giá trị ước lượng và thời gian suy luận là phép đo theo lô. Chưa có benchmark chứng minh ứng dụng web nhanh hơn phiên bản cũ hoặc mô hình chính xác hơn sau nâng cấp.

## 3. Next Steps

### 3.1. Remaining Tasks

Các công việc cần ưu tiên trước khi bàn giao cuối gồm:

1. **Kiểm chứng thêm chất lượng phân loại:** phân tích lỗi ở nhóm Payment, rà soát trùng lặp giữa các tập và chuẩn bị dữ liệu đánh giá bổ sung chưa tham gia lựa chọn mô hình. Script hiện chọn mô hình cuối theo Macro F1 trên tập test nên cần thêm bằng chứng độc lập về khả năng tổng quát hóa.
2. **Mở rộng kiểm thử sử dụng:** kiểm tra Firefox, Safari, thiết bị di động thật và thao tác với screen reader; lấy phản hồi từ người dùng thử.
3. **Đánh giá môi trường chạy cuối:** kiểm tra bản build production trên môi trường thử nghiệm, đo độ trễ toàn bộ request, RAM và tải đồng thời; xác minh CORS cùng cấu hình frontend/backend.
4. **Hoàn thiện bàn giao:** cập nhật báo cáo cuối, slide, kịch bản demo và hướng dẫn tái lập; thống nhất đại diện nộp bài và kiểm tra toàn bộ tài liệu.

### 3.2. Planned Improvements

Nhóm dự kiến tinh chỉnh giao diện và thông báo lỗi theo phản hồi sử dụng, bổ sung tình huống kiểm thử khó và cải thiện hướng dẫn xử lý các ticket có điểm thấp. Phần mô hình sẽ được ưu tiên đánh giá thêm trước khi quyết định có cần thay đổi hoặc hiệu chỉnh confidence. Hiện chưa có bằng chứng xác nhận chất lượng trên văn bản tiếng Việt hay dữ liệu vận hành thực tế.

Đối với deployment, frontend đã có thể build thành các file tĩnh và backend có thể chạy độc lập. Bước tiếp theo là kiểm tra cấu hình trên môi trường phù hợp; việc triển khai public chỉ thực hiện khi nhóm thống nhất và có đủ điều kiện. Gửi email thật hoặc tích hợp CRM bên ngoài là hướng mở rộng, chưa phải chức năng đã hoàn thành của phiên bản hiện tại.

### 3.3. Proposed Timeline for Final Completion

Do chưa có ngày nộp cuối chính thức trong yêu cầu, bảng dưới đây là **kế hoạch đề xuất trong hai tuần**, tính sau ngày lập báo cáo. Nhóm cần điều chỉnh theo lịch của giảng viên và nguồn lực thực tế.

| Thời gian dự kiến | Công việc trọng tâm | Đầu ra mong đợi |
|---|---|---|
| **01–03/11/2026** | Rà soát lỗi phân loại, dữ liệu trùng lặp và chuẩn bị các mẫu đánh giá bổ sung. | Danh sách lỗi, bộ tình huống kiểm tra và nhận xét về giới hạn mô hình. |
| **04–07/11/2026** | Kiểm tra thêm trình duyệt/thiết bị, khả năng tiếp cận; thu thập phản hồi và sửa lỗi ưu tiên. | Giao diện ổn định hơn và báo cáo kiểm thử cập nhật. |
| **08–10/11/2026** | Kiểm tra bản build production, cấu hình môi trường chạy, đo độ trễ và tài nguyên. | Cấu hình tái lập được cùng kết quả đo trên môi trường thử nghiệm. |
| **11–14/11/2026** | Hoàn thiện tài liệu, slide, kịch bản demo; kiểm tra hồi quy và chuẩn bị nộp bài. | Gói bàn giao cuối, phần demo và báo cáo do một đại diện nhóm nộp. |

Điều kiện hoàn thành dự kiến là: luồng phân loại thật hoạt động ổn định, kết quả nhất quán với pipeline gốc, các kiểm tra bắt buộc đạt yêu cầu, tài liệu chạy lại đầy đủ và các giới hạn còn lại được mô tả rõ trong báo cáo cuối.

## Tài liệu và bằng chứng trong project

- [Báo cáo Checkpoint 1](report.md)
- [Kết quả đánh giá mô hình](model/results/test_evaluation_summary.json)
- [Log huấn luyện](model/logs/training_latest.log)
- [Tổng hợp thay đổi triển khai](web_app/frontend/docs/IMPLEMENTATION.md)
- [Đối chiếu chức năng Gradio và React](web_app/frontend/docs/FEATURE_PARITY.md)
- [Báo cáo kiểm thử và giới hạn kiểm tra](web_app/frontend/docs/VALIDATION.md)
- [Kiến trúc, hướng dẫn chạy và chuẩn bị deployment](web_app/frontend/README.md)
- [Ảnh giao diện desktop](web_app/frontend/docs/screenshots/router-desktop.png), [kết quả phân loại](web_app/frontend/docs/screenshots/router-result.png), [dashboard](web_app/frontend/docs/screenshots/analytics-desktop.png) và [mobile](web_app/frontend/docs/screenshots/router-mobile.png)
