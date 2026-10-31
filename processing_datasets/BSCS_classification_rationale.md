# Phân Loại Intent theo 3 Nhóm: Technical Issue, Payment, Return/Refund

> **Nguồn dữ liệu:** Bitext_Sample_Customer_Support Dataset

---

## Tổng Quan

Dưới đây là bảng ánh xạ toàn bộ **11 Category** và **27 Intent** từ dataset vào **3 nhóm chính**:

| Nhóm | Category | Số Intent | Intent |
|------|----------|-----------|--------|
| **Technical Issue** | ACCOUNT | 6 | create_account, delete_account, edit_account, recover_password, registration_problems, switch_account |
| | CONTACT | 2 | contact_customer_service, contact_human_agent |
| | DELIVERY | 2 | delivery_options, delivery_period |
| | ORDER | 4 | cancel_order, change_order, place_order, track_order |
| | SHIPPING | 2 | change_shipping_address, set_up_shipping_address |
| | SUBSCRIPTION | 1 | newsletter_subscription |
| **Payment** | PAYMENT | 2 | check_payment_methods, payment_issue |
| | INVOICE | 2 | check_invoice, get_invoice |
| | CANCEL | 1 | check_cancellation_fee |
| **Return/Refund** | REFUND | 3 | check_refund_policy, get_refund, track_refund |
| | FEEDBACK | 2 | complaint, review |

---

## 1. Nhóm Technical Issue (Vấn Đề Kỹ Thuật)

**Số Intent: 17** | **Số Category: 6**

### Định nghĩa
Nhóm này bao gồm tất cả các intent liên quan đến **vận hành hệ thống, quản lý tài khoản, quy trình đặt hàng, giao nhận và hỗ trợ kỹ thuật**. Đây là những vấn đề mà khách hàng gặp phải trong quá trình tương tác với nền tảng/dịch vụ, không trực tiếp liên quan đến tiền bạc hay hoàn trả.

### Lý do phân loại từng Category

#### 🔹 ACCOUNT (6 intents)
| Intent | Lý do xếp vào Technical Issue |
|--------|-------------------------------|
| `create_account` | Thao tác kỹ thuật tạo tài khoản trên hệ thống |
| `delete_account` | Thao tác kỹ thuật xóa tài khoản |
| `edit_account` | Chỉnh sửa thông tin tài khoản — vấn đề quản lý dữ liệu người dùng |
| `recover_password` | Khôi phục mật khẩu — lỗi truy cập kỹ thuật phổ biến |
| `registration_problems` | Trực tiếp là vấn đề kỹ thuật khi đăng ký |
| `switch_account` | Chuyển đổi tài khoản — thao tác hệ thống |

> **Lý do chung:** Tất cả đều liên quan đến **quản lý định danh người dùng (user identity management)** — một chức năng kỹ thuật cốt lõi của bất kỳ nền tảng nào.

---

#### 🔹 CONTACT (2 intents)
| Intent | Lý do xếp vào Technical Issue |
|--------|-------------------------------|
| `contact_customer_service` | Yêu cầu hỗ trợ kỹ thuật từ hệ thống CSKH |
| `contact_human_agent` | Escalation lên agent thật khi hệ thống bot/AI không giải quyết được |

> **Lý do chung:** Đây là **cơ chế escalation kỹ thuật** — khi khách hàng không thể tự giải quyết vấn đề thông qua giao diện tự phục vụ (self-service).

---

#### 🔹 DELIVERY (2 intents)
| Intent | Lý do xếp vào Technical Issue |
|--------|-------------------------------|
| `delivery_options` | Truy vấn thông tin về phương thức giao hàng — thuộc về logistics/hệ thống |
| `delivery_period` | Hỏi về thời gian giao hàng — thông tin vận hành |

> **Lý do chung:** Delivery là **quy trình vận hành (operational process)**, không phải giao dịch tài chính. Khách hàng muốn biết "khi nào" và "bằng cách nào" hàng đến — đây là thông tin kỹ thuật/logistics.

---

#### 🔹 ORDER (4 intents)
| Intent | Lý do xếp vào Technical Issue |
|--------|-------------------------------|
| `cancel_order` | Thao tác hủy đơn hàng trên hệ thống |
| `change_order` | Sửa đổi đơn hàng — thao tác quản lý đơn |
| `place_order` | Thực hiện đặt hàng — quy trình kỹ thuật |
| `track_order` | Theo dõi trạng thái đơn hàng — truy vấn hệ thống |

> **Lý do chung:** Order management là **vòng đời đơn hàng (order lifecycle)** — một quy trình kỹ thuật từ khi tạo đến khi hoàn tất. Không liên quan trực tiếp đến thanh toán hay hoàn tiền.

---

#### 🔹 SHIPPING (2 intents)
| Intent | Lý do xếp vào Technical Issue |
|--------|-------------------------------|
| `change_shipping_address` | Thay đổi địa chỉ giao hàng — cập nhật thông tin logistics |
| `set_up_shipping_address` | Thiết lập địa chỉ giao hàng — cấu hình hệ thống |

> **Lý do chung:** Shipping address là **dữ liệu cấu hình (configuration data)** trong hệ thống. Việc thay đổi/thiết lập là thao tác kỹ thuật trên profile người dùng.

---

#### 🔹 SUBSCRIPTION (1 intent)
| Intent | Lý do xếp vào Technical Issue |
|--------|-------------------------------|
| `newsletter_subscription` | Đăng ký nhận bản tin — thao tác kỹ thuật trên hệ thống marketing |

> **Lý do chung:** Subscription là **cài đặt tùy chọn (preference setting)** — không liên quan thanh toán hay hoàn trả.

---

## 2. Nhóm Payment (Thanh Toán)

**Số Intent: 5** | **Số Category: 3**

### Định nghĩa
Nhóm này bao gồm tất cả các intent liên quan trực tiếp đến **dòng tiền (money flow)**: phương thức thanh toán, hóa đơn, phí và các vấn đề phát sinh trong quá trình giao dịch tài chính.

### Lý do phân loại từng Category

#### 🔹 PAYMENT (2 intents)
| Intent | Lý do xếp vào Payment |
|--------|----------------------|
| `check_payment_methods` | Truy vấn các phương thức thanh toán khả dụng — trực tiếp liên quan đến giao dịch tài chính |
| `payment_issue` | Vấn đề phát sinh khi thanh toán (thất bại, lỗi, từ chối) — sự cố tài chính |

> **Lý do chung:** Đây là **core payment intents** — trực tiếp nhất về dòng tiền. `payment_issue` đặc biệt quan trọng vì nó ảnh hưởng đến việc hoàn tất giao dịch.

---

#### 🔹 INVOICE (2 intents)
| Intent | Lý do xếp vào Payment |
|--------|----------------------|
| `check_invoice` | Kiểm tra hóa đơn — xác minh thông tin thanh toán |
| `get_invoice` | Yêu cầu lấy hóa đơn — chứng từ tài chính |

> **Lý do chung:** Invoice là **chứng từ thanh toán (payment documentation)**. Hóa đơn luôn gắn liền với giao dịch tài chính và là bằng chứng của việc đã thanh toán.

---

#### 🔹 CANCEL (1 intent)
| Intent | Lý do xếp vào Payment |
|--------|----------------------|
| `check_cancellation_fee` | Kiểm tra phí hủy — liên quan đến chi phí tài chính khi hủy dịch vụ |

> **Lý do chung:** Mặc dù "cancel" nghe có vẻ thuộc về order management, nhưng `check_cancellation_fee` cụ thể hỏi về **phí (fee)** — một khoản charge tài chính. Đây khác với `cancel_order` (thuộc Technical Issue) vì trọng tâm là **số tiền phải trả khi hủy**, không phải thao tác hủy đơn.

---

## 3. Nhóm Return/Refund (Hoàn Trả/Hoàn Tiền)

**Số Intent: 5** | **Số Category: 2**

### Định nghĩa
Nhóm này bao gồm các intent liên quan đến **quy trình hoàn tiền, chính sách đổi trả và phản hồi tiêu cực** từ khách hàng — thường là hậu quả của một giao dịch không như mong đợi.

### Lý do phân loại từng Category

#### 🔹 REFUND (3 intents)
| Intent | Lý do xếp vào Return/Refund |
|--------|---------------------------|
| `check_refund_policy` | Tìm hiểu chính sách hoàn tiền — bước đầu tiên trong quy trình return/refund |
| `get_refund` | Yêu cầu hoàn tiền trực tiếp — hành động core của nhóm |
| `track_refund` | Theo dõi trạng thái hoàn tiền — giám sát quy trình return |

> **Lý do chung:** Đây là **trực tiếp nhất** — cả 3 intent đều chứa từ khóa "refund" và đại diện cho **3 giai đoạn của quy trình hoàn tiền**: tìm hiểu chính sách → yêu cầu → theo dõi.

---

#### 🔹 FEEDBACK (2 intents)
| Intent | Lý do xếp vào Return/Refund |
|--------|---------------------------|
| `complaint` | Khiếu nại — thường là bước trước hoặc đi kèm với yêu cầu hoàn tiền/đổi trả |
| `review` | Đánh giá — phản hồi về sản phẩm/dịch vụ, thường phản ánh lý do muốn hoàn trả |

> **Lý do chung:** Feedback (đặc biệt là complaint) trong bối cảnh customer support **thường là nguyên nhân gốc rễ (root cause)** dẫn đến yêu cầu return/refund. Khi khách hàng complaint, mục đích cuối cùng thường là:
> - Được hoàn tiền 💰
> - Được đổi sản phẩm 🔄
> - Được bồi thường 
>
> Do đó, complaint và review được xếp vào nhóm Return/Refund vì chúng **nằm trong cùng một customer journey** — hành trình từ khi không hài lòng → khiếu nại → yêu cầu hoàn trả.

---

## Sơ Đồ Tổng Quan

```
─────────────────────────────────────────────────────────────────┐
│                    BITEXT CUSTOMER SUPPORT INTENTS              │
└─────────────────────────┬───────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
┌───────────────── ┌─────────────┐ ┌──────────────────┐
│  TECHNICAL      │ │   PAYMENT   │ │  RETURN/REFUND   │
│    ISSUE        │ │             │ │                  │
│  (17 intents)   │ │ (5 intents) │ │  (5 intents)     │
├─────────────────┤ ├─────────────┤ ├──────────────────┤
│ • ACCOUNT (6)   │ │ • PAYMENT(2)│ │ • REFUND (3)     │
│ • CONTACT (2)   │ │ • INVOICE(2)│ │ • FEEDBACK (2)   │
│ • DELIVERY (2)  │ │ • CANCEL (1)│ │                  │
│ • ORDER (4)     │ │             │ │                  │
│ • SHIPPING (2)  │ │             │ │                  │
│ • SUBSCRIPTION(1)││            │ │                  │
└─────────────────┘ └─────────────┘ ──────────────────┘
          │               │               │
          ▼               ▼               ▼
   "How do I use     "How do I pay/   "I want my
    the system?"      get billed?"     money back"
```

---

## Nguyên Tắc Phân Loại

| Tiêu chí | Technical Issue | Payment | Return/Refund |
|----------|----------------|---------|---------------|
| **Trọng tâm** | Vận hành hệ thống & quy trình | Dòng tiền & giao dịch tài chính | Hoàn trả & bồi thường |
| **Câu hỏi điển hình** | "Làm thế nào để...?" | "Tôi phải trả bao nhiêu?" | "Tôi muốn hoàn tiền" |
| **Giai đoạn customer journey** | Trước & trong giao dịch | Trong giao dịch | Sau giao dịch |
| **Mức độ khẩn cấp** | Trung bình | Cao | Rất cao |
| **Tác động doanh thu** | Gián tiếp | Trực tiếp | Tiêu cực (mất doanh thu) |

---

## Kết Luận

Việc phân loại 27 intent vào 3 nhóm **Technical Issue**, **Payment**, và **Return/Refund** dựa trên **bản chất nghiệp vụ (business nature)** của từng intent:

1. **Technical Issue** — Chiếm tỷ lệ lớn nhất (17/27 = 63%) vì đa số tương tác của khách hàng là về **sử dụng hệ thống và quy trình**.
2. **Payment** — Nhóm quan trọng về doanh thu (5/27 = 18.5%), liên quan trực tiếp đến **dòng tiền vào**.
3. **Return/Refund** — Nhóm nhạy cảm nhất (5/27 = 18.5%), liên quan đến **dòng tiền ra** và **sự hài lòng của khách hàng**.

>  **Lưu ý:** Một số intent có thể thuộc về nhiều nhóm tùy ngữ cảnh. Ví dụ: `cancel_order` được xếp vào Technical Issue vì trọng tâm là thao tác hủy, trong khi `check_cancellation_fee` được xếp vào Payment vì trọng tâm là chi phí tài chính.