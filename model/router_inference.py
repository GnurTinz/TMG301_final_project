"""
Hệ thống CRM Tự động Điều hướng Khiếu nại Khách hàng (Support Ticket Router).
TMG301 - Inference & Deployment Module.

Chức năng:
1. Đọc email / tin nhắn khiếu nại của khách hàng.
2. Nạp mô hình Machine Learning đã được huấn luyện tốt nhất (best_ticket_router_pipeline.joblib).
3. Dự đoán chủ đề khiếu nại (Lỗi kỹ thuật / Thanh toán / Đổi trả).
4. Tính toán độ tin cậy (Confidence Score).
5. Tự động điều hướng đến đúng phòng ban chức năng kèm SLA và độ ưu tiên.
6. Tự động tạo email phản hồi xác nhận cho khách hàng.
"""

import sys
import uuid
from datetime import datetime
from pathlib import Path
import numpy as np
import joblib

from config import SAVED_MODELS_DIR, LABEL_MAPPINGS


class CRMTicketRouter:
    """Hệ thống CRM Router điều hướng khiếu nại thông minh."""

    def __init__(self, model_path=None):
        if model_path is None:
            model_path = SAVED_MODELS_DIR / "best_ticket_router_pipeline.joblib"

        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Không tìm thấy mô hình đã lưu tại: {self.model_path.resolve()}.\n"
                f"Vui lòng chạy 'python train_ticket_router.py' trước để huấn luyện mô hình!"
            )

        # Nạp pipeline và metadata
        checkpoint = joblib.load(self.model_path)
        self.pipeline = checkpoint["pipeline"]
        self.model_name = checkpoint.get("model_name", "Unknown Model")
        self.classes = checkpoint.get("classes", list(LABEL_MAPPINGS.keys()))
        self.label_mappings = checkpoint.get("label_mappings", LABEL_MAPPINGS)
        self.metrics = checkpoint.get("metrics", {})

    def _calculate_confidence(self, text):
        """Tính toán xác suất hoặc độ tin cậy dựa trên mô hình."""
        clf = self.pipeline.named_steps["clf"]
        tfidf = self.pipeline.named_steps["tfidf"]
        vec = tfidf.transform([text])

        if hasattr(clf, "predict_proba"):
            probs = clf.predict_proba(vec)[0]
            best_idx = np.argmax(probs)
            pred_label = clf.classes_[best_idx]
            confidence = float(probs[best_idx])
            all_scores = {cls: float(prob) for cls, prob in zip(clf.classes_, probs)}
        elif hasattr(clf, "decision_function"):
            decision = clf.decision_function(vec)[0]
            # Softmax trên decision scores để ước lượng confidence
            exp_scores = np.exp(decision - np.max(decision))
            probs = exp_scores / np.sum(exp_scores)
            best_idx = np.argmax(probs)
            pred_label = clf.classes_[best_idx]
            confidence = float(probs[best_idx])
            all_scores = {cls: float(prob) for cls, prob in zip(clf.classes_, probs)}
        else:
            pred_label = self.pipeline.predict([text])[0]
            confidence = 1.0
            all_scores = {pred_label: 1.0}

        return pred_label, confidence, all_scores

    def _determine_priority(self, label, text, confidence):
        """Xác định mức độ ưu tiên dựa trên chủ đề và từ khóa khẩn cấp."""
        urgent_keywords = ["urgent", "immediately", "khẩn cấp", "ngay lập tức", "stolen", "bị mất", "fraud", "lừa đảo", "unauthorized"]
        text_lower = text.lower()

        if any(kw in text_lower for kw in urgent_keywords):
            return "Urgent"

        default_priority = self.label_mappings.get(label, {}).get("default_priority", "Medium")
        if confidence < 0.60:
            return "Needs Human Review"
        return default_priority

    def route_ticket(self, customer_message, customer_email="customer@example.com", ticket_id=None):
        """Điều hướng một ticket khiếu nại cụ thể."""
        if not ticket_id:
            ticket_id = f"TCK-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"

        pred_label, confidence, all_scores = self._calculate_confidence(customer_message)
        dept_info = self.label_mappings.get(pred_label, {
            "vi_name": pred_label,
            "department": "Phòng Hỗ trợ Chung",
            "dept_code": "DEPT_GENERAL",
            "sla_hours": 24,
        })

        priority = self._determine_priority(pred_label, customer_message, confidence)

        routing_result = {
            "ticket_id": ticket_id,
            "timestamp": datetime.now().isoformat(),
            "customer_email": customer_email,
            "customer_message": customer_message,
            "routing_decision": {
                "category": pred_label,
                "category_vi": dept_info["vi_name"],
                "target_department": dept_info["department"],
                "dept_code": dept_info["dept_code"],
                "confidence_score": round(confidence * 100, 2),
                "all_class_probabilities": {k: round(v * 100, 2) for k, v in all_scores.items()},
                "priority_level": priority,
                "sla_hours": dept_info["sla_hours"],
            },
            "automated_response": (
                f"Kính gửi Quý khách,\n\n"
                f"Hệ thống CRM đã tiếp nhận khiếu nại [{ticket_id}] của Quý khách về vấn đề: "
                f"'{dept_info['vi_name']}'.\n"
                f"Yêu cầu đã được tự động điều hướng đến '{dept_info['department']}' với mức độ ưu tiên: {priority}.\n"
                f"Chuyên viên của chúng tôi sẽ liên hệ xử lý trong vòng {dept_info['sla_hours']} giờ làm việc.\n\n"
                f"Trân trọng cảm ơn,\nĐội ngũ CSKH."
            )
        }
        return routing_result


# Đảm bảo mã hóa an toàn trên Windows terminal
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def run_demo():
    """Chạy thử nghiệm hệ thống điều hướng trên các email khiếu nại mẫu."""
    print("=" * 80)
    print(" [CRM] HE THONG CRM TU DONG DIEU HUONG KHIEU NAI (SUPPORT TICKET ROUTER)")
    print("=" * 80)

    try:
        router = CRMTicketRouter()
        print(f"[OK] Da nap mo hinh: {router.model_name}")
        if "accuracy" in router.metrics:
            print(f"[METRIC] Do chinh xac mo hinh tren tap Test: {router.metrics['accuracy']*100:.2f}%\n")
    except Exception as e:
        print(f"[ERROR] Loi nap mo hinh: {e}")
        return

    sample_complaints = [
        {
            "sender": "david.tran@gmail.com",
            "text": "My card is blocked after entering the wrong pin at the ATM. Can you unblock my card please?",
            "expected": "Technical Issue",
        },
        {
            "sender": "sarah.nguyen@yahoo.com",
            "text": "Why was I charged an extra $15 transfer fee on my bank statement yesterday? That is totally unacceptable.",
            "expected": "Payment",
        },
        {
            "sender": "michael.le@outlook.com",
            "text": "I returned the defective shoes two weeks ago but I still have not received my refund. Where is my money?",
            "expected": "Return/Refund",
        },
        {
            "sender": "alex.pham@gmail.com",
            "text": "I can not log into my online banking account, the mobile app keeps crashing whenever I try to verify my identity.",
            "expected": "Technical Issue",
        },
        {
            "sender": "linda.vo@company.com",
            "text": "My double transaction refund is missing. The merchant said they reverted it, but my balance has not updated.",
            "expected": "Return/Refund",
        },
    ]

    for idx, sample in enumerate(sample_complaints, start=1):
        res = router.route_ticket(sample["text"], customer_email=sample["sender"])
        d = res["routing_decision"]

        print(f"[Email #{idx}] Tu: {sample['sender']}")
        print(f"   Noi dung: \"{sample['text']}\"")
        print(f"   -> Du doan:     {d['category']} ({d['category_vi']})")
        print(f"   -> Do tin cay:   {d['confidence_score']:.1f}%")
        print(f"   -> Chuyen den:   {d['target_department']} [{d['dept_code']}]")
        print(f"   -> Muc uu tien:  {d['priority_level']} (SLA: {d['sla_hours']}h)")
        print(f"   -> Xac suat cac lop: {d['all_class_probabilities']}")
        print("-" * 80)


if __name__ == "__main__":
    run_demo()
