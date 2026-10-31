# Checkpoint 1 Report — Support Ticket Router

**Môn học:** TMG301  
**Tên dự án:** Hệ thống tự động phân loại và định tuyến yêu cầu hỗ trợ khách hàng  
**Ngày cập nhật báo cáo:** 31/10/2026

## 1. Current Project Status

Dự án hiện đã xây dựng được một nguyên mẫu hoàn chỉnh từ khâu chuẩn bị dữ liệu, trích xuất đặc trưng, huấn luyện và đánh giá mô hình đến tích hợp giao diện demo. Hệ thống tiếp nhận nội dung yêu cầu hỗ trợ do người dùng nhập, phân loại vào một trong ba nhóm **Technical Issue**, **Payment**, **Return/Refund**, sau đó tạo kết quả định tuyến gồm phòng ban phụ trách, mức độ ưu tiên, thời hạn xử lý theo cấu hình SLA và nội dung phản hồi xác nhận.

### 1.1. Completed Tasks and Milestones

**Khảo sát và phân tích dữ liệu.** Dự án đã có notebook và script phân tích khám phá dữ liệu (EDA) cho bốn nguồn: Banking77, Bitext Customer Support, Consumer Complaint Database và Twitter Customer Support. Các nội dung khảo sát gồm cấu trúc dữ liệu, giá trị thiếu, bản ghi trùng lặp, phân bố nhãn, độ dài văn bản, từ khóa và cụm từ thường gặp. Hai nguồn được sử dụng trong pipeline huấn luyện hiện tại là **Banking77** và **Bitext Customer Support**.

**Xây dựng hệ thống nhãn và xử lý dữ liệu.** Dự án đã xây dựng bảng ánh xạ 77 nhãn của Banking77 và 27 intent của Bitext về ba nhóm phục vụ định tuyến. Mỗi nguồn có file mapping JSON và tài liệu giải thích cách phân nhóm. Các script xử lý thực hiện chuẩn hóa khoảng trắng, ánh xạ nhãn, kiểm tra nhãn chưa được ánh xạ và xuất kết quả dưới dạng CSV/JSON. Dữ liệu sau xử lý được hợp nhất thành hai trường chính là `text` và `label`, với **39.955 mẫu**.

| Nhóm phân loại | Số mẫu | Tỷ lệ |
|---|---:|---:|
| Technical Issue | 22.943 | 57,42% |
| Payment | 11.010 | 27,56% |
| Return/Refund | 6.002 | 15,02% |
| **Tổng cộng** | **39.955** | **100%** |

**Hoàn thành pipeline huấn luyện và so sánh mô hình.** Dữ liệu được chia theo phương pháp stratified split để duy trì gần tương đương tỷ lệ các lớp giữa các tập, với `random_state=42`:

| Tập dữ liệu | Số mẫu | Tỷ lệ |
|---|---:|---:|
| Training | 27.967 | 70% |
| Validation | 5.994 | 15% |
| Test | 5.994 | 15% |

Văn bản được chuyển thành đặc trưng bằng **TF-IDF unigram và bigram**, kết hợp loại bỏ stopwords tiếng Anh và sử dụng sublinear term frequency. Trong bước tinh chỉnh trên tập training, bộ vector hóa tạo ra **9.899 đặc trưng**. Bốn mô hình đã được triển khai và thực nghiệm gồm Multinomial Naive Bayes, Complement Naive Bayes, Linear Support Vector Classification (LinearSVC) và Logistic Regression.

Siêu tham số được lựa chọn theo Macro F1 trên tập validation. Sau đó, từng cấu hình được huấn luyện lại trên **33.961 mẫu training + validation** để đánh giá trên tập test. Dự án đã lưu pipeline LinearSVC cùng thông tin mô hình, nhãn, cấu hình định tuyến và các chỉ số đánh giá vào file `model/saved_models/best_ticket_router_pipeline.joblib`.

**Hoàn thành các đầu ra phục vụ đánh giá và trình bày.** Pipeline đã tạo log huấn luyện, bảng so sánh chỉ số CSV, báo cáo đánh giá JSON và năm biểu đồ: phân bố dữ liệu giữa các tập, validation curves, learning curves, confusion matrices và so sánh hiệu năng mô hình. Dự án cũng đã có script chạy huấn luyện và demo trên Windows, tài liệu hướng dẫn sử dụng, ứng dụng Flask và phiên bản giao diện Gradio phục vụ triển khai trên Hugging Face Spaces.

### 1.2. Implemented Features and Functionalities

Các chức năng hiện đã được triển khai bao gồm:

- **Tiếp nhận yêu cầu hỗ trợ:** cho phép nhập nội dung tin nhắn và email khách hàng, đồng thời cung cấp các tình huống mẫu để thử nghiệm.
- **Phân loại văn bản:** sử dụng pipeline TF-IDF và mô hình đã lưu để dự đoán một trong ba nhóm yêu cầu hỗ trợ.
- **Hiển thị điểm tin cậy:** trả về điểm cho từng lớp và điểm của lớp được chọn. Với LinearSVC, điểm này được ước lượng bằng softmax từ decision scores.
- **Gán phòng ban và SLA:** ánh xạ kết quả phân loại sang phòng ban phụ trách theo cấu hình nghiệp vụ đã định nghĩa.
- **Xác định mức độ ưu tiên:** áp dụng ưu tiên mặc định theo nhóm; nhận diện từ khóa khẩn cấp như `urgent`, `fraud` hoặc `unauthorized`. Nếu không có từ khóa khẩn cấp và điểm tin cậy dưới 60%, kết quả được gắn mức `Needs Human Review`.
- **Tạo thông tin ticket và phản hồi:** sinh mã ticket, thời gian tiếp nhận và nội dung xác nhận để người dùng xem hoặc sao chép.
- **Theo dõi lịch sử demo:** giao diện Flask lưu các ticket gần đây trong localStorage của trình duyệt.
- **Dashboard phân tích mô hình:** hiển thị bảng so sánh bốn mô hình, chỉ số theo lớp, confusion matrices và các biểu đồ đánh giá.
- **Cung cấp API qua Flask:** có các endpoint phục vụ định tuyến ticket, lấy thông tin mô hình, tình huống mẫu và dữ liệu dashboard.

Quy tắc gán phòng ban và SLA hiện tại như sau:

| Nhóm dự đoán | Phòng ban phụ trách | Ưu tiên mặc định | SLA cấu hình |
|---|---|---|---:|
| Technical Issue | Hỗ trợ kỹ thuật | Medium | 12 giờ |
| Payment | Kế toán và thanh toán | High | 4 giờ |
| Return/Refund | Chăm sóc khách hàng và đổi trả | High | 6 giờ |

Phân loại chủ đề được thực hiện bằng mô hình học máy; phòng ban, ưu tiên và SLA được xác định bằng các quy tắc đã cấu hình. Chức năng định tuyến hiện tạo thông tin phân công trên giao diện/API, còn nội dung phản hồi được tạo dưới dạng văn bản. Project chưa có tích hợp chuyển ticket sang hệ thống CRM bên ngoài hoặc gửi email thực tế.

### 1.3. Current Results and Performance

Theo kết quả thực nghiệm được lưu ngày **23/10/2026**, hiệu năng của bốn mô hình trên **5.994 mẫu test** như sau:

| Mô hình | Accuracy | Macro F1 | Weighted F1 | Thời gian huấn luyện pipeline |
|---|---:|---:|---:|---:|
| **LinearSVC** | **97,46%** | **97,19%** | **97,47%** | **0,50 giây** |
| Logistic Regression | 97,41% | 97,14% | 97,42% | 0,72 giây |
| MultinomialNB | 96,83% | 96,45% | 96,85% | 0,31 giây |
| ComplementNB | 96,70% | 96,35% | 96,72% | 0,31 giây |

**LinearSVC đạt kết quả cao nhất trong lần thực nghiệm này** và được sử dụng cho chức năng suy luận của demo. Mô hình phân loại đúng **5.842/5.994 mẫu**, đạt Balanced Accuracy **97,00%**. Kết quả chi tiết theo nhóm như sau:

| Nhóm phân loại | Precision | Recall | F1-score | Số mẫu test |
|---|---:|---:|---:|---:|
| Payment | 95,10% | 96,37% | 95,73% | 1.652 |
| Return/Refund | 98,86% | 96,33% | 97,58% | 900 |
| Technical Issue | 98,26% | 98,29% | 98,27% | 3.442 |

Nhóm Payment có F1-score thấp nhất trong ba nhóm và là phần cần ưu tiên phân tích lỗi ở giai đoạn tiếp theo. LinearSVC chỉ cao hơn Logistic Regression khoảng **0,05 điểm phần trăm Accuracy**, vì vậy kết quả hiện tại thể hiện sự chênh lệch nhỏ giữa hai mô hình trên tập test này.

Thời gian dự đoán của pipeline LinearSVC được ghi nhận là khoảng **0,0496 giây cho toàn bộ lô 5.994 mẫu test**. Đây là thời gian suy luận theo lô trong lần chạy đã lưu; con số này chưa đo độ trễ toàn bộ ứng dụng web hoặc hiệu năng khi nhiều người dùng truy cập đồng thời. Thời gian huấn luyện trong bảng cũng chỉ tính bước fit pipeline cuối, chưa bao gồm toàn bộ quá trình tìm siêu tham số và phân tích learning curves.

Learning curves của LinearSVC cho thấy ở mức dữ liệu lớn nhất được khảo sát, Training Accuracy đạt khoảng **99,06%**, còn Cross-validation Accuracy đạt khoảng **97,45%**, với khoảng cách **1,61 điểm phần trăm**. Kết quả này cung cấp bằng chứng ban đầu về khả năng tổng quát hóa trong phạm vi dữ liệu đang sử dụng.

Ở thời điểm Checkpoint 1, dự án đã có nguyên mẫu để trình diễn luồng tiếp nhận, phân loại và tạo quyết định định tuyến. Các chỉ số trên là kết quả đánh giá nội bộ với dữ liệu tiếng Anh và hệ thống ba nhãn do dự án ánh xạ. Script hiện chọn mô hình cuối theo Macro F1 trên tập test, nên cần thêm một tập đánh giá độc lập chưa tham gia lựa chọn mô hình để xác nhận hiệu năng. Điểm tin cậy của LinearSVC cũng chưa được hiệu chỉnh xác suất; hiệu năng trên tiếng Việt và dữ liệu vận hành thực tế chưa được xác nhận trong các kết quả đã lưu.

**Tài liệu và bằng chứng trong project:**

- [Notebook và script EDA](EDA/)
- [Script xử lý và tài liệu ánh xạ nhãn](processing_datasets/)
- [Cấu hình mô hình và quy tắc định tuyến](model/config.py)
- [Pipeline huấn luyện và đánh giá](model/train_ticket_router.py)
- [Module suy luận và tạo kết quả định tuyến](model/router_inference.py)
- [Ứng dụng Flask](web_app/app.py) và [ứng dụng Gradio](app.py)
- [Kết quả đánh giá chi tiết](model/results/test_evaluation_summary.json)
- [Log huấn luyện được sử dụng trong báo cáo](model/logs/training_latest.log)
- [Các biểu đồ đánh giá mô hình](model/plots/)
