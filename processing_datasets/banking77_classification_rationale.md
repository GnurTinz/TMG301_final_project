# Phân loại 77 nhãn theo 3 nhóm ngữ nghĩa

## Mục tiêu và nguyên tắc

Phân loại theo **ý định nghiệp vụ chính của khách hàng**, không chỉ dựa trên từ khóa xuất hiện trong nhãn. Mỗi nhãn được gán vào đúng một nhóm để thuận tiện cho việc xây dựng taxonomy hoặc ánh xạ nhãn trong bài toán phân loại văn bản.

## Technical Issue

Xếp các nhãn liên quan đến chức năng, cấu hình, khả năng sử dụng hoặc trạng thái kỹ thuật của thẻ/tài khoản/ứng dụng; thông tin cá nhân, xác minh danh tính và hỗ trợ. Các nhãn số dư chưa cập nhật được xếp ở đây vì trọng tâm là dữ liệu chưa phản ánh đúng sau một thao tác, thay vì yêu cầu hoàn trả tiền.

**Số nhãn:** 39

| STT | Nhãn gốc | Dịch tiếng Việt |
|---:|---|---|
| 2 | `activate_my_card` | Kích hoạt thẻ |
| 3 | `age_limit` | Giới hạn độ tuổi |
| 4 | `apple_pay_or_google_pay` | Apple Pay hoặc Google Pay |
| 5 | `atm_support` | Hỗ trợ ATM |
| 7 | `balance_not_updated_after_bank_transfer` | Số dư chưa cập nhật sau khi chuyển khoản ngân hàng |
| 8 | `balance_not_updated_after_cheque_or_cash_deposit` | Số dư chưa cập nhật sau khi nộp séc hoặc tiền mặt |
| 9 | `beneficiary_not_allowed` | Không thể thêm hoặc sử dụng người thụ hưởng |
| 11 | `card_about_to_expire` | Thẻ sắp hết hạn |
| 12 | `card_acceptance` | Nơi chấp nhận thanh toán bằng thẻ |
| 13 | `card_arrival` | Tình trạng thẻ đã đến hay chưa |
| 14 | `card_delivery_estimate` | Thời gian dự kiến giao thẻ |
| 15 | `card_linking` | Liên kết thẻ |
| 16 | `card_not_working` | Thẻ không hoạt động |
| 20 | `card_swallowed` | Thẻ bị ATM nuốt |
| 23 | `change_pin` | Đổi mã PIN |
| 24 | `compromised_card` | Thẻ bị lộ hoặc có nguy cơ bị xâm phạm |
| 25 | `contactless_not_working` | Thanh toán không tiếp xúc không hoạt động |
| 26 | `country_support` | Các quốc gia được hỗ trợ |
| 31 | `disposable_card_limits` | Hạn mức thẻ dùng một lần |
| 32 | `edit_personal_details` | Chỉnh sửa thông tin cá nhân |
| 38 | `fiat_currency_support` | Các loại tiền pháp định được hỗ trợ |
| 39 | `get_disposable_virtual_card` | Tạo thẻ ảo dùng một lần |
| 40 | `get_physical_card` | Yêu cầu cấp thẻ vật lý |
| 41 | `getting_spare_card` | Yêu cầu cấp thẻ dự phòng |
| 42 | `getting_virtual_card` | Yêu cầu cấp thẻ ảo |
| 43 | `lost_or_stolen_card` | Thẻ bị mất hoặc bị đánh cắp |
| 44 | `lost_or_stolen_phone` | Điện thoại bị mất hoặc bị đánh cắp |
| 45 | `order_physical_card` | Đặt thẻ vật lý |
| 46 | `passcode_forgotten` | Quên mật mã đăng nhập |
| 51 | `pin_blocked` | Mã PIN bị khóa |
| 55 | `supported_cards_and_currencies` | Các loại thẻ và tiền tệ được hỗ trợ |
| 56 | `terminate_account` | Đóng tài khoản |
| 69 | `unable_to_verify_identity` | Không thể xác minh danh tính |
| 70 | `verify_my_identity` | Xác minh danh tính |
| 71 | `verify_source_of_funds` | Xác minh nguồn tiền |
| 72 | `verify_top_up` | Xác minh giao dịch nạp tiền |
| 73 | `virtual_card_not_working` | Thẻ ảo không hoạt động |
| 74 | `visa_or_mastercard` | Visa hoặc Mastercard |
| 75 | `why_verify_identity` | Lý do cần xác minh danh tính |

## Payment

Xếp các nhãn có ý định chính là thực hiện, theo dõi hoặc xử lý một giao dịch tài chính: thanh toán, rút/nạp tiền, chuyển/nhận tiền, giao dịch bị từ chối/thất bại/đang chờ, phí, tỷ giá và hạn mức. Nhãn cancel_transfer được xếp vào đây vì đối tượng trực tiếp là một giao dịch chuyển tiền, dù thao tác mong muốn là hủy.

**Số nhãn:** 33

| STT | Nhãn gốc | Dịch tiếng Việt |
|---:|---|---|
| 6 | `automatic_top_up` | Nạp tiền tự động |
| 10 | `cancel_transfer` | Hủy giao dịch chuyển tiền |
| 17 | `card_payment_fee_charged` | Bị tính phí thanh toán bằng thẻ |
| 18 | `card_payment_not_recognised` | Giao dịch thanh toán thẻ không được nhận diện |
| 19 | `card_payment_wrong_exchange_rate` | Áp dụng sai tỷ giá khi thanh toán bằng thẻ |
| 21 | `cash_withdrawal_charge` | Phí rút tiền mặt |
| 22 | `cash_withdrawal_not_recognised` | Giao dịch rút tiền mặt không được nhận diện |
| 27 | `declined_card_payment` | Thanh toán bằng thẻ bị từ chối |
| 28 | `declined_cash_withdrawal` | Yêu cầu rút tiền mặt bị từ chối |
| 29 | `declined_transfer` | Giao dịch chuyển tiền bị từ chối |
| 30 | `direct_debit_payment_not_recognised` | Giao dịch trích nợ tự động không được nhận diện |
| 33 | `exchange_charge` | Phí chuyển đổi tiền tệ |
| 34 | `exchange_rate` | Tỷ giá chuyển đổi tiền tệ |
| 35 | `exchange_via_app` | Chuyển đổi tiền tệ qua ứng dụng |
| 36 | `extra_charge_on_statement` | Phát sinh khoản phí bổ sung trên sao kê |
| 37 | `failed_transfer` | Chuyển tiền thất bại |
| 47 | `pending_card_payment` | Giao dịch thanh toán thẻ đang chờ xử lý |
| 48 | `pending_cash_withdrawal` | Giao dịch rút tiền mặt đang chờ xử lý |
| 49 | `pending_top_up` | Giao dịch nạp tiền đang chờ xử lý |
| 50 | `pending_transfer` | Giao dịch chuyển tiền đang chờ xử lý |
| 52 | `receiving_money` | Nhận tiền |
| 57 | `top_up_by_bank_transfer_charge` | Phí nạp tiền bằng chuyển khoản ngân hàng |
| 58 | `top_up_by_card_charge` | Phí nạp tiền bằng thẻ |
| 59 | `top_up_by_cash_or_cheque` | Nạp tiền bằng tiền mặt hoặc séc |
| 60 | `top_up_failed` | Nạp tiền thất bại |
| 61 | `top_up_limits` | Hạn mức nạp tiền |
| 63 | `topping_up_by_card` | Nạp tiền bằng thẻ |
| 65 | `transfer_fee_charged` | Bị tính phí chuyển tiền |
| 66 | `transfer_into_account` | Chuyển tiền vào tài khoản |
| 67 | `transfer_not_received_by_recipient` | Người nhận chưa nhận được tiền chuyển |
| 68 | `transfer_timing` | Thời gian xử lý chuyển tiền |
| 76 | `wrong_amount_of_cash_received` | Nhận sai số tiền mặt |
| 77 | `wrong_exchange_rate_for_cash_withdrawal` | Áp dụng sai tỷ giá khi rút tiền mặt |

## Return/Refund

Xếp các nhãn nói trực tiếp về yêu cầu hoàn tiền, khoản hoàn tiền chưa về hoặc giao dịch bị đảo ngược. transaction_charged_twice được xếp vào đây theo hướng xử lý thường gặp là yêu cầu hoàn lại khoản bị tính trùng. Trong một hệ thống khác, nhãn này cũng có thể được xếp vào Payment nếu quy tắc ưu tiên loại giao dịch thay vì hướng xử lý.

**Số nhãn:** 5

| STT | Nhãn gốc | Dịch tiếng Việt |
|---:|---|---|
| 1 | `Refund_not_showing_up` | Khoản hoàn tiền chưa xuất hiện |
| 53 | `request_refund` | Yêu cầu hoàn tiền |
| 54 | `reverted_card_payment?` | Giao dịch thanh toán bằng thẻ bị đảo ngược |
| 62 | `top_up_reverted` | Giao dịch nạp tiền bị đảo ngược |
| 64 | `transaction_charged_twice` | Giao dịch bị tính tiền hai lần |

## Các trường hợp ranh giới cần lưu ý

Một số nhãn có thể được xếp khác nhau tùy mục tiêu của hệ thống. Quy tắc dưới đây được chọn để ưu tiên ý định/hướng xử lý chính:

| Nhãn | Nhóm được chọn | Lý do |
|---|---|---|
| `balance_not_updated_after_bank_transfer` | **Technical Issue** | Vấn đề là số dư chưa được cập nhật, dù nguyên nhân bắt đầu từ một giao dịch chuyển khoản. |
| `card_payment_not_recognised` | **Payment** | Nhãn xoay quanh một giao dịch thanh toán cụ thể không được nhận diện; không nhất thiết hàm ý lỗi phần cứng/thẻ. |
| `verify_top_up` | **Technical Issue** | Trọng tâm là quy trình xác minh/kiểm tra giao dịch nạp tiền, không phải thao tác nạp tiền thông thường. |
| `cancel_transfer` | **Payment** | Ý định là hủy một giao dịch chuyển tiền; vẫn thuộc vòng đời xử lý giao dịch. |
| `top_up_reverted` | **Return/Refund** | Giao dịch nạp tiền đã bị đảo ngược, nên kết quả cần quan tâm là tiền bị trả ngược/không còn ở trạng thái nạp thành công. |
| `transaction_charged_twice` | **Return/Refund** | Phân loại theo hướng xử lý thường gặp là hoàn lại khoản bị tính trùng; có thể đổi sang Payment nếu taxonomy ưu tiên loại giao dịch. |
| `request_refund` | **Return/Refund** | Ý định hoàn tiền được nêu trực tiếp. |

## Khuyến nghị khi sử dụng cho Machine Learning

1. Giữ nguyên nhãn gốc làm khóa (`label`) và lưu nhóm cấp cao làm giá trị (`group`); bản dịch tiếng Việt chỉ dùng để diễn giải.
2. Mỗi nhãn chỉ thuộc một nhóm trong taxonomy hiện tại, tránh một nhãn xuất hiện ở nhiều lớp nếu bài toán yêu cầu phân loại đơn nhãn.
3. Nếu mục tiêu là phân loại theo **loại giao dịch**, cân nhắc chuyển `transaction_charged_twice` sang `Payment`. Nếu mục tiêu là phân loại theo **hướng giải quyết yêu cầu**, giữ trong `Return/Refund` hợp lý hơn.
4. `Technical Issue` ở đây được hiểu rộng là vấn đề chức năng, tài khoản, thẻ, xác minh hoặc trạng thái dữ liệu; không chỉ giới hạn ở lỗi phần mềm thuần túy.

## Cấu trúc dữ liệu

Tệp JSON có cấu trúc `group -> list[dict]`, mỗi phần tử gồm `id`, `label`, `vi`. Tệp Python chứa cùng dữ liệu trong biến `LABEL_GROUPS` để có thể import trực tiếp.
