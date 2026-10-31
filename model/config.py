"""
Configuration module for Customer Support Ticket Router (TMG301 Project).
Defines paths, hyperparameters, department mappings, and plotting settings.
"""

from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_DIR = Path(__file__).resolve().parent

DATA_FILE = PROJECT_ROOT / "processed_datasets" / "combined_dataset.csv"
SAVED_MODELS_DIR = MODEL_DIR / "saved_models"
LOGS_DIR = MODEL_DIR / "logs"
PLOTS_DIR = MODEL_DIR / "plots"
RESULTS_DIR = MODEL_DIR / "results"

# Ensure necessary directories exist
for directory in [SAVED_MODELS_DIR, LOGS_DIR, PLOTS_DIR, RESULTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Data Splitting Configurations
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15
RANDOM_STATE = 42

# Label Definitions and CRM Department Routing Mappings
LABEL_MAPPINGS = {
    "Technical Issue": {
        "vi_name": "Lỗi kỹ thuật",
        "department": "Phòng Hỗ trợ Kỹ thuật (Technical Support Dept)",
        "dept_code": "DEPT_TECH_SUPPORT",
        "default_priority": "Medium",
        "sla_hours": 12,
    },
    "Payment": {
        "vi_name": "Thanh toán & Giao dịch",
        "department": "Phòng Kế toán & Thanh toán (Billing & Finance Dept)",
        "dept_code": "DEPT_BILLING_FINANCE",
        "default_priority": "High",
        "sla_hours": 4,
    },
    "Return/Refund": {
        "vi_name": "Đổi trả & Hoàn tiền",
        "department": "Phòng CSKH & Đổi trả (Customer Care & Refund Dept)",
        "dept_code": "DEPT_CUSTOMER_CARE_REFUND",
        "default_priority": "High",
        "sla_hours": 6,
    },
}

# TF-IDF Feature Extraction Hyperparameters
TFIDF_CONFIG = {
    "ngram_range": (1, 2),
    "max_features": 12000,
    "min_df": 2,
    "max_df": 0.95,
    "sublinear_tf": True,
    "stop_words": "english",
}

# Hyperparameter Tuning Search Grids (evaluated on Train/Validation)
HYPERPARAM_GRIDS = {
    "MultinomialNB": {
        "alpha": [0.001, 0.01, 0.05, 0.1, 0.5, 1.0, 2.0],
    },
    "ComplementNB": {
        "alpha": [0.001, 0.01, 0.05, 0.1, 0.5, 1.0, 2.0],
    },
    "LinearSVC": {
        "C": [0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
    },
    "LogisticRegression": {
        "C": [0.01, 0.1, 0.5, 1.0, 5.0, 10.0],
    },
}
