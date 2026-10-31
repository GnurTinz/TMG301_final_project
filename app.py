"""
Hugging Face Spaces Native Gradio App for Support Ticket Router (TMG301).
Runs 24/7 on Hugging Face Spaces (Gradio SDK - 100% Free).
"""

import sys
import os
import json
from pathlib import Path
import gradio as gr
import pandas as pd

# Thêm đường dẫn model vào sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT / "model"))

from router_inference import CRMTicketRouter

# Khởi tạo router
router = CRMTicketRouter(PROJECT_ROOT / "model" / "saved_models" / "best_ticket_router_pipeline.joblib")

# Đọc dữ liệu dashboard nếu có
summary_path = PROJECT_ROOT / "model" / "results" / "test_evaluation_summary.json"
if summary_path.exists():
    with open(summary_path, "r", encoding="utf-8") as f:
        metrics_data = json.load(f)
else:
    metrics_data = {}


try:
    import spaces
    gpu_decorator = spaces.GPU
except Exception:
    def gpu_decorator(fn):
        return fn


@gpu_decorator
def route_ticket_gradio(customer_message, customer_email):
    """Xử lý điều hướng khiếu nại và trả về HTML kết quả trực quan."""
    if not customer_message or not customer_message.strip():
        return (
            "<div style='padding: 20px; text-align: center; color: #ef4444;'>Vui lòng nhập nội dung khiếu nại!</div>",
            "",
            {}
        )

    res = router.route_ticket(
        customer_message=customer_message.strip(),
        customer_email=customer_email.strip() if customer_email else "customer@example.com"
    )

    d = res["routing_decision"]
    cat = d["category"]
    cat_vi = d["category_vi"]
    dept = d["target_department"]
    dept_code = d["dept_code"]
    conf = d["confidence_score"]
    priority = d["priority_level"]
    sla = d["sla_hours"]
    ticket_id = res["ticket_id"]
    probs = d["all_class_probabilities"]

    # Xác định màu sắc viền và class theo chủ đề
    if cat == "Technical Issue":
        accent_border = "#06b6d4"
        dept_cls = "tech"
    elif cat == "Payment":
        accent_border = "#f59e0b"
        dept_cls = "payment"
    else:
        accent_border = "#10b981"
        dept_cls = "refund"

    priority_cls = "urgent" if priority in ["Urgent", "High"] else "medium"

    p_tech = probs.get("Technical Issue", 0)
    p_pay = probs.get("Payment", 0)
    p_ref = probs.get("Return/Refund", 0)

    html_result = f"""
    <div class="ticket-result-card" style="border-left: 5px solid {accent_border} !important;">
        
        <!-- Header Mã Ticket -->
        <div class="ticket-header-border" style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 12px; margin-bottom: 16px;">
            <div>
                <span class="ticket-sub-header">MÃ TICKET ĐỊNH DANH CRM</span>
                <div class="ticket-id-text">{ticket_id}</div>
            </div>
            <span class="badge-priority-{priority_cls}">
                Ưu tiên: {priority}
            </span>
        </div>

        <!-- Thẻ Phòng Ban Tiếp Nhận -->
        <div style="margin-bottom: 18px;">
            <span class="badge-dept-{dept_cls}">
                {cat} ({cat_vi})
            </span>
            <div class="ticket-dept-title">
                {dept}
            </div>
            <div class="ticket-dept-meta">
                Mã phòng ban: {dept_code} | SLA cam kết: Trong {sla} giờ làm việc
            </div>
        </div>

        <!-- Độ Tin Cậy & Phân Bổ Xác Suất -->
        <div class="ticket-prob-box">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <span class="ticket-box-title">Độ tin cậy của AI (Confidence Score)</span>
                <span class="ticket-conf-num">{conf:.1f}%</span>
            </div>

            <!-- 3 Thanh Xác Suất -->
            <div style="display: flex; flex-direction: column; gap: 8px; font-size: 12px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span class="ticket-prob-label">Lỗi kỹ thuật:</span>
                    <div class="ticket-prob-track">
                        <div style="width: {p_tech}%; background: #06b6d4; height: 100%;"></div>
                    </div>
                    <span class="ticket-prob-val">{p_tech:.1f}%</span>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span class="ticket-prob-label">Thanh toán:</span>
                    <div class="ticket-prob-track">
                        <div style="width: {p_pay}%; background: #f59e0b; height: 100%;"></div>
                    </div>
                    <span class="ticket-prob-val">{p_pay:.1f}%</span>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span class="ticket-prob-label">Đổi trả / Hoàn tiền:</span>
                    <div class="ticket-prob-track">
                        <div style="width: {p_ref}%; background: #10b981; height: 100%;"></div>
                    </div>
                    <span class="ticket-prob-val">{p_ref:.1f}%</span>
                </div>
            </div>
        </div>

    </div>
    """

    return html_result, res["automated_response"], probs


# Bảng so sánh mô hình cho Dashboard
def get_benchmark_df():
    data = [
        {"Hạng": "🥇 Quán quân", "Mô hình": "Support Vector Machine (LinearSVC)", "Test Accuracy": "97.46%", "Macro F1": "97.19%", "Weighted F1": "97.47%", "Thời gian Train": "0.50s", "Trạng thái": "🏆 Production Ready"},
        {"Hạng": "🥈 Á quân", "Mô hình": "Logistic Regression (Baseline)", "Test Accuracy": "97.41%", "Macro F1": "97.14%", "Weighted F1": "97.42%", "Thời gian Train": "0.72s", "Trạng thái": "Baseline chuẩn"},
        {"Hạng": "🥉 Hạng 3", "Mô hình": "Naive Bayes (MultinomialNB)", "Test Accuracy": "96.83%", "Macro F1": "96.45%", "Weighted F1": "96.85%", "Thời gian Train": "0.31s", "Trạng thái": "Đã đánh giá"},
        {"Hạng": "4", "Mô hình": "Naive Bayes (ComplementNB)", "Test Accuracy": "96.70%", "Macro F1": "96.35%", "Weighted F1": "96.72%", "Thời gian Train": "0.31s", "Trạng thái": "Đã đánh giá"},
    ]
    return pd.DataFrame(data)


def get_per_class_df():
    data = [
        {"Phòng ban tiếp nhận": "Phòng Hỗ trợ Kỹ thuật", "Chủ đề (Label)": "Technical Issue", "Precision": "98.26%", "Recall": "98.29%", "F1-Score": "98.27%", "Số mẫu Test": "3,442"},
        {"Phòng ban tiếp nhận": "Phòng Kế toán & Thanh toán", "Chủ đề (Label)": "Payment", "Precision": "95.10%", "Recall": "96.37%", "F1-Score": "95.73%", "Số mẫu Test": "1,652"},
        {"Phòng ban tiếp nhận": "Phòng CSKH & Đổi trả", "Chủ đề (Label)": "Return/Refund", "Precision": "98.86%", "Recall": "96.33%", "F1-Score": "97.58%", "Số mẫu Test": "900"},
    ]
    return pd.DataFrame(data)


# Xây dựng giao diện Gradio Blocks với Adaptive CSS (Tự động thích ứng cả Light Mode & Dark Mode)
custom_css = """
body, .gradio-container {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

:root {
    --card-outer-bg: #ffffff;
    --card-outer-border: #cbd5e1;
    --card-outer-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
    --card-title-color: #0f172a;
    --card-meta-color: #475569;
    --card-sub-header: #64748b;
    --card-ticket-id: #0284c7;
    --card-box-bg: #f8fafc;
    --card-box-border: #e2e8f0;
    --card-box-title: #334155;
    --card-box-label: #1e293b;
    --card-bar-track: #e2e8f0;
    --card-val-text: #0f172a;
    --card-conf-num: #0284c7;
}

.dark {
    --card-outer-bg: #111827;
    --card-outer-border: #374151;
    --card-outer-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    --card-title-color: #f8fafc;
    --card-meta-color: #94a3b8;
    --card-sub-header: #94a3b8;
    --card-ticket-id: #38bdf8;
    --card-box-bg: rgba(15, 23, 42, 0.65);
    --card-box-border: rgba(255, 255, 255, 0.1);
    --card-box-title: #cbd5e1;
    --card-box-label: #e2e8f0;
    --card-bar-track: rgba(255, 255, 255, 0.12);
    --card-val-text: #ffffff;
    --card-conf-num: #38bdf8;
}

.ticket-result-card {
    background: var(--card-outer-bg) !important;
    border: 1px solid var(--card-outer-border) !important;
    border-radius: 14px;
    padding: 22px;
    box-shadow: var(--card-outer-shadow);
    transition: all 0.25s ease;
}

.ticket-header-border {
    border-bottom: 1px solid var(--card-box-border);
}

.ticket-sub-header {
    font-size: 11px;
    text-transform: uppercase;
    color: var(--card-sub-header) !important;
    font-weight: 700;
    letter-spacing: 0.05em;
}

.ticket-id-text {
    font-family: monospace;
    font-size: 16px;
    font-weight: 700;
    color: var(--card-ticket-id) !important;
}

.ticket-dept-title {
    font-size: 20px;
    font-weight: 800;
    color: var(--card-title-color) !important;
    margin-top: 6px;
    line-height: 1.3;
}

.ticket-dept-meta {
    font-size: 12px;
    color: var(--card-meta-color) !important;
    font-family: monospace;
    margin-top: 4px;
}

.ticket-prob-box {
    background: var(--card-box-bg) !important;
    border: 1px solid var(--card-box-border) !important;
    border-radius: 10px;
    padding: 14px;
    margin-top: 14px;
}

.ticket-box-title {
    font-size: 13px;
    font-weight: 600;
    color: var(--card-box-title) !important;
}

.ticket-conf-num {
    font-size: 18px;
    font-weight: 800;
    color: var(--card-conf-num) !important;
}

.ticket-prob-label {
    width: 125px;
    color: var(--card-box-label) !important;
    font-weight: 600;
}

.ticket-prob-track {
    flex: 1;
    background: var(--card-bar-track) !important;
    height: 8px;
    border-radius: 4px;
    overflow: hidden;
}

.ticket-prob-val {
    width: 45px;
    text-align: right;
    font-weight: 700;
    color: var(--card-val-text) !important;
}

.badge-priority-urgent, .badge-priority-high {
    background: rgba(239, 68, 68, 0.15);
    color: #b91c1c;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
}
.dark .badge-priority-urgent, .dark .badge-priority-high {
    color: #f87171;
}

.badge-priority-medium {
    background: rgba(59, 130, 246, 0.15);
    color: #1d4ed8;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
}
.dark .badge-priority-medium {
    color: #60a5fa;
}

.badge-dept-tech {
    background: rgba(6, 182, 212, 0.15);
    color: #0369a1;
    font-size: 11px;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 4px;
    text-transform: uppercase;
}
.dark .badge-dept-tech {
    color: #22d3ee;
}

.badge-dept-payment {
    background: rgba(245, 158, 11, 0.15);
    color: #b45309;
    font-size: 11px;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 4px;
    text-transform: uppercase;
}
.dark .badge-dept-payment {
    color: #fbbf24;
}

.badge-dept-refund {
    background: rgba(16, 185, 129, 0.15);
    color: #047857;
    font-size: 11px;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 4px;
    text-transform: uppercase;
}
.dark .badge-dept-refund {
    color: #34d399;
}

.kpi-box {
    background: var(--card-box-bg) !important;
    border: 1px solid var(--card-box-border) !important;
    border-radius: 12px;
    padding: 16px;
    text-align: center;
    box-shadow: var(--card-outer-shadow);
}
"""

with gr.Blocks(title="CRM Support Ticket Router - TMG301") as demo:
    
    gr.HTML("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h1 style="font-size: 28px; font-weight: 800; margin-bottom: 6px; background: linear-gradient(120deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            CRM Support Ticket Router
        </h1>
        <p style="color: #94a3b8; font-size: 15px; max-width: 700px; margin: 0 auto;">
            Hệ thống Tự động Đọc email/tin nhắn khiếu nại, phân loại chủ đề (Lỗi kỹ thuật, Thanh toán, Đổi trả) và chuyển tiếp đến đúng phòng ban xử lý (TMG301).
        </p>
    </div>
    """)

    with gr.Tabs():
        
        # TAB 1: LIVE TICKET ROUTER
        with gr.TabItem("🎫 Điều Hướng Khiếu Nại (Live Router)"):
            with gr.Row():
                with gr.Column(scale=5):
                    gr.Markdown("### ✉️ Nhập Nội Dung Khiếu Nại")
                    input_message = gr.Textbox(
                        label="Email / Tin nhắn của khách hàng:",
                        placeholder="Nhập nội dung khiếu nại của khách hàng (tiếng Anh hoặc tiếng Việt)...",
                        lines=5,
                        value="My card is blocked after entering the wrong pin at the ATM. It swallowed my card and says card blocked. Can you please unblock my card and help me retrieve it immediately?"
                    )
                    input_email = gr.Textbox(
                        label="Email khách hàng:",
                        value="david.tran@gmail.com",
                        placeholder="customer@example.com"
                    )
                    btn_route = gr.Button("🚀 Phân Loại & Điều Hướng CRM", variant="primary", size="lg")

                    gr.Markdown("#### 💡 Thử nghiệm nhanh các kịch bản mẫu:")
                    gr.Examples(
                        examples=[
                            ["My card is blocked after entering the wrong pin at the ATM. Can you please unblock my card?", "david.tran@gmail.com"],
                            ["Why was I charged an extra $15 transfer fee on my bank statement yesterday? That is totally unacceptable.", "sarah.nguyen@yahoo.com"],
                            ["I returned the defective shoes two weeks ago but I still have not received my refund. Where is my money?", "michael.le@outlook.com"],
                            ["I cannot log into my online banking app. The mobile app keeps crashing whenever I try to verify my identity.", "alex.pham@gmail.com"],
                            ["My balance shows a double transaction charged for my grocery shopping. Please revert the second charge.", "linda.vo@company.com"],
                        ],
                        inputs=[input_message, input_email],
                        label="Click chọn mẫu khiếu nại thực tế:"
                    )

                with gr.Column(scale=6):
                    gr.Markdown("### 🎯 Kết Quả Phân Bổ Phòng Ban CRM")
                    output_html = gr.HTML(
                        label="Kết quả điều hướng",
                        value="<div style='padding: 40px; text-align: center; color: #94a3b8; border: 1px dashed rgba(255,255,255,0.15); border-radius: 12px;'>Nhập khiếu nại và nhấn 'Phân Loại & Điều Hướng CRM' để xem kết quả.</div>"
                    )
                    output_email = gr.Textbox(
                        label="📧 Mẫu Email Tự Động Soạn Gửi Khách Hàng:",
                        lines=5,
                        interactive=False
                    )

            btn_route.click(
                fn=route_ticket_gradio,
                inputs=[input_message, input_email],
                outputs=[output_html, output_email]
            )

        # TAB 2: MODEL ANALYTICS DASHBOARD
        with gr.TabItem("📊 Model Analytics Dashboard (Bảng Điều Khiển)"):
            
            # 4 Thẻ KPI
            with gr.Row():
                with gr.Column(scale=1):
                    gr.HTML("<div class='kpi-box'><div style='font-size: 11px; color: #94a3b8; font-weight: 700;'>MÔ HÌNH QUÁN QUÂN 🏆</div><div style='font-size: 24px; font-weight: 800; color: #38bdf8;'>97.46%</div><div style='font-size: 11px; color: #34d399;'>LinearSVC (SVM)</div></div>")
                with gr.Column(scale=1):
                    gr.HTML("<div class='kpi-box'><div style='font-size: 11px; color: #94a3b8; font-weight: 700;'>MACRO F1-SCORE 🎯</div><div style='font-size: 24px; font-weight: 800; color: #34d399;'>97.19%</div><div style='font-size: 11px; color: #cbd5e1;'>Cân bằng 3 phòng ban</div></div>")
                with gr.Column(scale=1):
                    gr.HTML("<div class='kpi-box'><div style='font-size: 11px; color: #94a3b8; font-weight: 700;'>QUY MÔ DATASET 📂</div><div style='font-size: 24px; font-weight: 800; color: #f59e0b;'>39,955</div><div style='font-size: 11px; color: #cbd5e1;'>Banking77 + BSCS</div></div>")
                with gr.Column(scale=1):
                    gr.HTML("<div class='kpi-box'><div style='font-size: 11px; color: #94a3b8; font-weight: 700;'>TỐC ĐỘ INFERENCE ⚡</div><div style='font-size: 24px; font-weight: 800; color: #ec4899;'>&lt; 0.05s</div><div style='font-size: 11px; color: #cbd5e1;'>5,994 mẫu Test</div></div>")

            gr.Markdown("### 📋 Bảng So Sánh Hiệu Năng Các Mô Hình Machine Learning (Tập Test Độc Lập)")
            benchmark_table = gr.Dataframe(
                value=get_benchmark_df(),
                interactive=False
            )

            gr.Markdown("### 🎯 Chi Tiết Hiệu Năng Từng Phòng Ban (Mô Hình Tối Ưu: LinearSVC)")
            per_class_table = gr.Dataframe(
                value=get_per_class_df(),
                interactive=False
            )

            gr.Markdown("### 📈 Thư Viện Đồ Thị Nghiên Cứu & Đánh Giá Khoa Học")
            plot_paths = [
                str(PROJECT_ROOT / "model" / "plots" / "model_comparison_metrics.png"),
                str(PROJECT_ROOT / "model" / "plots" / "confusion_matrices_all_models.png"),
                str(PROJECT_ROOT / "model" / "plots" / "learning_curves.png"),
                str(PROJECT_ROOT / "model" / "plots" / "validation_curves.png"),
                str(PROJECT_ROOT / "model" / "plots" / "dataset_split_distribution.png"),
            ]
            valid_plots = [p for p in plot_paths if Path(p).exists()]
            if valid_plots:
                gr.Gallery(
                    value=valid_plots,
                    label="Đồ thị đánh giá mô hình (Click vào ảnh để phóng to)",
                    columns=2,
                    height="auto"
                )

            gr.Markdown("""
            ### 💡 Kết Luận Khoa Học & Ứng Dụng Thực Tế CRM:
            1. **Tại sao LinearSVC đạt hiệu năng cao nhất (97.46%)?**: Không gian đặc trưng TF-IDF unigram + bigram có số chiều cao (9,899 đặc trưng) và thưa (sparse). Thuật toán SVM với siêu phẳng phân chia tối đa hóa lề (maximum margin hyperplane) tối ưu hóa ranh giới quyết định cực kỳ hiệu quả, vượt trội hơn mô hình xác suất Naive Bayes.
            2. **Độ ổn định & Không Overfitting**: Đồ thị Learning Curves cho thấy khoảng cách giữa Train Accuracy (khoảng 99.0%) và Cross-Validation Accuracy (khoảng 97.4%) chỉ chênh lệch 1.6%, chứng minh mô hình có khả năng tổng quát hóa rất cao trên dữ liệu mới.
            3. **Ứng dụng CRM thực tế**: Với tốc độ phản hồi dưới 0.05 giây và độ chính xác 97.46%, hệ thống hoàn toàn sẵn sàng tích hợp làm bộ định tuyến tự động cho phòng CSKH doanh nghiệp.
            """)

if __name__ == "__main__":
    demo.launch(
        theme=gr.themes.Soft(primary_hue="blue"),
        css=custom_css,
        ssr_mode=False
    )
