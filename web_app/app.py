"""
Flask Backend Web Server for Support Ticket Router.
TMG301 Demo Application.
"""

import sys
import os
import uuid
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from werkzeug.exceptions import HTTPException

# Thêm đường dẫn project vào sys.path để import model
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.append(str(project_root / "model"))

from config import SAVED_MODELS_DIR, LABEL_MAPPINGS
from router_inference import CRMTicketRouter

app = Flask(__name__, template_folder="templates", static_folder="static")
ALLOWED_ORIGINS = {
    origin.strip().rstrip("/")
    for origin in os.environ.get(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:4173,http://127.0.0.1:4173",
    ).split(",")
    if origin.strip()
}

# Khởi tạo Router
try:
    model_path = os.environ.get("MODEL_PATH")
    router = CRMTicketRouter(Path(model_path).expanduser() if model_path else None)
    print(f"[OK] Đã nạp thành công mô hình: {router.model_name}")
except Exception as e:
    print(f"[WARNING] Không thể nạp mô hình từ saved_models: {e}")
    router = None


SAMPLE_COMPLAINTS = [
    {
        "id": "sample-1",
        "sender": "david.tran@gmail.com",
        "subject": "Thẻ ATM bị nuốt và tài khoản bị khóa",
        "text": "My card is blocked after entering the wrong pin at the ATM. It swallowed my card and the screen says card blocked. Can you please unblock my card and help me retrieve it immediately?",
        "expected": "Technical Issue",
        "tag": "Thẻ / ATM"
    },
    {
        "id": "sample-2",
        "sender": "sarah.nguyen@company.com",
        "subject": "Bị trừ tiền vô lý trên sao kê tài khoản",
        "text": "Why was I charged an extra $15 transfer fee on my bank statement yesterday? I made a standard transfer within the limit and was not notified about any extra fee. Please cancel this charge and explain.",
        "expected": "Payment",
        "tag": "Phí giao dịch"
    },
    {
        "id": "sample-3",
        "sender": "michael.le@gmail.com",
        "subject": "Đã hoàn trả hàng 2 tuần nhưng chưa nhận được tiền hoàn",
        "text": "I returned the defective shoes two weeks ago via your courier service and tracking shows delivered to your warehouse, but I still have not received my refund. Where is my money? Please process my refund now.",
        "expected": "Return/Refund",
        "tag": "Hoàn tiền"
    },
    {
        "id": "sample-4",
        "sender": "anna.smith@outlook.com",
        "subject": "Ứng dụng di động liên tục bị văng khi xác thực danh tính",
        "text": "I cannot log into my online banking app. Every time I submit my photo ID for identity verification, the app freezes and crashes to the home screen.",
        "expected": "Technical Issue",
        "tag": "Lỗi phần mềm"
    },
    {
        "id": "sample-5",
        "sender": "kevin.vu@yahoo.com",
        "subject": "Giao dịch quẹt thẻ bị tính 2 lần (Double Charged)",
        "text": "I checked my balance and saw a double transaction charged for my grocery shopping this morning. The merchant said they only received one payment, so the second one must be reverted immediately.",
        "expected": "Return/Refund",
        "tag": "Tính tiền kép"
    }
]

# The exact five inputs exposed by the original Gradio Examples component.
# Keep the existing Flask examples available to the legacy interface.
GRADIO_SAMPLE_COMPLAINTS = [
    {"id": "gradio-1", "sender": "david.tran@gmail.com", "subject": "Thẻ bị khóa", "tag": "Thẻ / ATM", "text": "My card is blocked after entering the wrong pin at the ATM. Can you please unblock my card?"},
    {"id": "gradio-2", "sender": "sarah.nguyen@yahoo.com", "subject": "Phí giao dịch", "tag": "Thanh toán", "text": "Why was I charged an extra $15 transfer fee on my bank statement yesterday? That is totally unacceptable."},
    {"id": "gradio-3", "sender": "michael.le@outlook.com", "subject": "Chưa nhận hoàn tiền", "tag": "Hoàn tiền", "text": "I returned the defective shoes two weeks ago but I still have not received my refund. Where is my money?"},
    {"id": "gradio-4", "sender": "alex.pham@gmail.com", "subject": "Lỗi đăng nhập", "tag": "Kỹ thuật", "text": "I cannot log into my online banking app. The mobile app keeps crashing whenever I try to verify my identity."},
    {"id": "gradio-5", "sender": "linda.vo@company.com", "subject": "Giao dịch tính hai lần", "tag": "Giao dịch", "text": "My balance shows a double transaction charged for my grocery shopping. Please revert the second charge."},
]


from flask import Flask, render_template, request, jsonify, send_from_directory
import json


@app.after_request
def configure_api_cors(response):
    """Allow explicitly configured browser origins; no credentials are required."""
    origin = request.headers.get("Origin", "")
    if request.path.startswith(("/api/", "/plots/")):
        response.vary.add("Origin")
        if origin in ALLOWED_ORIGINS:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@app.errorhandler(HTTPException)
def handle_http_error(error):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": error.description}), error.code
    return error


@app.route("/api/health", methods=["GET"])
def health():
    ready = router is not None
    return jsonify({
        "success": ready,
        "status": "ready" if ready else "unavailable",
        "model_ready": ready,
        "model_name": router.model_name if ready else None,
    }), 200 if ready else 503

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/plots/<path:filename>")
def serve_plot(filename):
    plots_dir = project_root / "model" / "plots"
    return send_from_directory(str(plots_dir), filename)


@app.route("/api/dashboard-data", methods=["GET"])
def get_dashboard_data():
    summary_path = project_root / "model" / "results" / "test_evaluation_summary.json"
    if not summary_path.exists():
        return jsonify({"success": False, "error": "Chưa có dữ liệu đánh giá"}), 404

    try:
        with open(summary_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        plots = [
            {
                "id": "model_compare",
                "title": "So sánh Hiệu năng Các Mô hình",
                "filename": "model_comparison_metrics.png",
                "description": "Biểu đồ cột so sánh Accuracy, Macro F1, Weighted F1, Macro Precision và Recall trên tập Test."
            },
            {
                "id": "confusion_matrices",
                "title": "Ma trận Nhầm lẫn (Confusion Matrices)",
                "filename": "confusion_matrices_all_models.png",
                "description": "Heatmap phân bố số lượng và tỷ lệ % phân loại đúng / sai giữa 3 phòng ban trên tập Test."
            },
            {
                "id": "learning_curves",
                "title": "Đường cong Học tập (Learning Curves)",
                "filename": "learning_curves.png",
                "description": "Đánh giá mức độ hội tụ, Bias và Variance khi tăng dần kích thước mẫu từ 10% đến 100% tập dữ liệu."
            },
            {
                "id": "validation_curves",
                "title": "Đường cong Tinh chỉnh Siêu tham số",
                "filename": "validation_curves.png",
                "description": "Hiệu năng Train vs Validation khi thay đổi tham số alpha (Naive Bayes) và C (LinearSVC, Logistic Regression)."
            },
            {
                "id": "data_distribution",
                "title": "Phân bố Tập Dữ liệu Train - Val - Test",
                "filename": "dataset_split_distribution.png",
                "description": "Phân chia Stratified Split bảo đảm tỷ lệ giữa 3 lớp nhãn hoàn toàn cân bằng trên cả 3 tập."
            }
        ]

        dataset_stats = {
            "total_samples": 39955,
            "train_samples": 27967,
            "val_samples": 5994,
            "test_samples": 5994,
            "classes": {
                "Technical Issue": {"count": 22943, "percentage": 57.42, "vi_name": "Lỗi kỹ thuật", "dept": "Phòng Hỗ trợ Kỹ thuật"},
                "Payment": {"count": 11010, "percentage": 27.56, "vi_name": "Thanh toán & Giao dịch", "dept": "Phòng Kế toán & Thanh toán"},
                "Return/Refund": {"count": 6002, "percentage": 15.02, "vi_name": "Đổi trả & Hoàn tiền", "dept": "Phòng CSKH & Đổi trả"}
            }
        }

        return jsonify({
            "success": True,
            "models_summary": data,
            "plots": plots,
            "dataset_stats": dataset_stats
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/samples", methods=["GET"])
def get_samples():
    samples = GRADIO_SAMPLE_COMPLAINTS if request.args.get("source") == "gradio" else SAMPLE_COMPLAINTS
    return jsonify({"success": True, "samples": samples})


@app.route("/api/model-info", methods=["GET"])
def get_model_info():
    if not router:
        return jsonify({"success": False, "error": "Mô hình chưa sẵn sàng"}), 503

    return jsonify({
        "success": True,
        "model_name": router.model_name,
        "classes": router.classes,
        "label_mappings": router.label_mappings,
        "metrics": {
            "accuracy": round(router.metrics.get("accuracy", 0.9746) * 100, 2),
            "macro_f1": round(router.metrics.get("macro_f1", 0.9719) * 100, 2),
            "test_samples": 5994,
            "train_samples": 33961,
        }
    })


@app.route("/api/route-ticket", methods=["POST"])
def route_ticket():
    if not router:
        return jsonify({"success": False, "error": "Mô hình chưa được nạp"}), 503

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"success": False, "error": "Dữ liệu phải là một JSON object hợp lệ"}), 400
    for field in ("message", "customer_email", "ticket_id"):
        if field in data and not isinstance(data[field], str):
            return jsonify({"success": False, "error": f"Trường {field} phải là chuỗi văn bản"}), 400
    message = data.get("message", "").strip()
    customer_email = data.get("customer_email", "").strip() or "customer@example.com"
    ticket_id = data.get("ticket_id", "").strip()

    if not message:
        return jsonify({"success": False, "error": "Vui lòng nhập nội dung khiếu nại"}), 400

    try:
        routing_result = router.route_ticket(
            customer_message=message,
            customer_email=customer_email,
            ticket_id=ticket_id or None
        )
        return jsonify({"success": True, "data": routing_result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    # Đảm bảo mã hóa an toàn
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    port = int(os.environ.get("PORT", 5050))
    host = os.environ.get("HOST", "0.0.0.0")
    print(f"\n========================================================")
    print(f" [WEB DEMO] SUPPORT TICKET ROUTER DANG CHAY TAI:")
    print(f" -> http://127.0.0.1:{port}")
    print(f"========================================================\n")
    app.run(host=host, port=port, debug=False)
