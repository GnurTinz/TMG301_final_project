"""Real-checkpoint API and Gradio parity tests. Run from the project root."""

import ast
from pathlib import Path
import unittest
from unittest.mock import patch

from web_app import app as backend


class TicketApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if backend.router is None:
            raise RuntimeError("The existing model must load for integration tests.")
        cls.client = backend.app.test_client()
        source = Path("app.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "route_ticket_gradio")
        function.decorator_list = []
        namespace = {"router": backend.router}
        exec(compile(ast.Module(body=[function], type_ignores=[]), "app.py", "exec"), namespace)
        cls.gradio_function = staticmethod(namespace["route_ticket_gradio"])
        examples_call = next(node for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "Examples")
        cls.gradio_examples = ast.literal_eval(next(keyword.value for keyword in examples_call.keywords if keyword.arg == "examples"))

    def test_health_and_startup_model_reuse(self):
        loaded = backend.router
        for _ in range(2):
            response = self.client.get("/api/health")
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json["model_ready"])
            self.assertIs(backend.router, loaded)

    def test_original_five_gradio_samples_are_preserved(self):
        response = self.client.get("/api/samples?source=gradio")
        self.assertEqual([[sample["text"], sample["sender"]] for sample in response.json["samples"]], self.gradio_examples)
        self.assertEqual(len(self.client.get("/api/samples").json["samples"]), 5)

    def test_real_predictions_match_original_gradio_and_direct_inference(self):
        for message, email in self.gradio_examples:
            with self.subTest(message=message):
                response = self.client.post("/api/route-ticket", json={"message": f"  {message}  ", "customer_email": f" {email} ", "ticket_id": "PARITY-CHECK"})
                self.assertEqual(response.status_code, 200)
                actual = response.json["data"]
                direct = backend.router.route_ticket(message, email, "PARITY-CHECK")
                self.assertEqual(actual["routing_decision"], direct["routing_decision"])
                self.assertEqual(actual["automated_response"], direct["automated_response"])
                self.assertEqual(actual["customer_message"], message)
                self.assertEqual(actual["customer_email"], email)
                html, acknowledgement, scores = self.gradio_function(message, email)
                decision = actual["routing_decision"]
                self.assertEqual(scores, decision["all_class_probabilities"])
                for field in ("category", "category_vi", "target_department", "dept_code", "priority_level"):
                    self.assertIn(decision[field], html)
                self.assertIn(f"{decision['confidence_score']:.1f}%", html)
                self.assertIn(decision["target_department"], acknowledgement)

    def test_urgent_and_human_review_rules_match_inference(self):
        for message in ("urgent unauthorized card payment fraud", "zxqvzxqv"):
            with self.subTest(message=message):
                actual = self.client.post("/api/route-ticket", json={"message": message}).json["data"]
                self.assertEqual(actual["routing_decision"], backend.router.route_ticket(message)["routing_decision"])
        self.assertEqual(backend.router._determine_priority("Payment", "urgent please", .2), "Urgent")
        self.assertEqual(backend.router._determine_priority("Payment", "please help", .59), "Needs Human Review")
        self.assertEqual(backend.router._determine_priority("Payment", "please help", .60), "High")

    def test_empty_messages_rejected(self):
        for payload in ({}, {"message": ""}, {"message": "   "}):
            with self.subTest(payload=payload):
                self.assertEqual(self.client.post("/api/route-ticket", json=payload).status_code, 400)

    def test_invalid_json_and_field_types_rejected(self):
        invalid = [[], "text", 42, {"message": 5}, {"message": []}, {"message": "test", "customer_email": None}, {"message": "test", "ticket_id": {}}]
        for payload in invalid:
            with self.subTest(payload=payload):
                response = self.client.post("/api/route-ticket", json=payload)
                self.assertEqual(response.status_code, 400)
                self.assertFalse(response.json["success"])
        response = self.client.post("/api/route-ticket", data="{bad json", content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_default_email_is_unchanged(self):
        response = self.client.post("/api/route-ticket", json={"message": "Please refund my order", "customer_email": " "})
        self.assertEqual(response.json["data"]["customer_email"], "customer@example.com")

    def test_model_unavailable_returns_service_error(self):
        with patch.object(backend, "router", None):
            for path in ("/api/health", "/api/model-info"):
                self.assertEqual(self.client.get(path).status_code, 503)
            self.assertEqual(self.client.post("/api/route-ticket", json={"message": "test"}).status_code, 503)

    def test_cors_preflight_and_errors(self):
        origin = "http://localhost:5173"
        response = self.client.options("/api/route-ticket", headers={"Origin": origin, "Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "Content-Type"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), origin)
        self.assertIn("POST", response.headers["Access-Control-Allow-Methods"])
        response = self.client.post("/api/route-ticket", json={}, headers={"Origin": origin})
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), origin)
        denied = self.client.get("/api/health", headers={"Origin": "https://unconfigured.example"})
        self.assertNotIn("Access-Control-Allow-Origin", denied.headers)

    def test_dashboard_and_all_plots(self):
        response = self.client.get("/api/dashboard-data")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json["models_summary"]), 4)
        self.assertEqual(response.json["dataset_stats"]["test_samples"], 5994)
        for plot in response.json["plots"]:
            with self.client.get(f"/plots/{plot['filename']}") as image:
                self.assertEqual(image.status_code, 200)
                self.assertEqual(image.mimetype, "image/png")

    def test_model_info_and_legacy_pages_remain_available(self):
        self.assertEqual(self.client.get("/api/model-info").json["model_name"], backend.router.model_name)
        for path in ("/", "/dashboard"):
            self.assertEqual(self.client.get(path).status_code, 200)

    def test_api_http_errors_are_json(self):
        for response in (self.client.get("/api/missing"), self.client.get("/api/route-ticket")):
            self.assertIn(response.status_code, (404, 405))
            self.assertFalse(response.json["success"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
