"""
Script Huấn luyện và Đánh giá Mô hình Tự động Điều hướng Khiếu nại Khách hàng (Support Ticket Router).
TMG301 - Multi-class Text Classification.

Mục tiêu:
1. Đọc dữ liệu hợp nhất (combined_dataset.csv) gồm 3 nhóm nhãn:
   - Technical Issue (Lỗi kỹ thuật)
   - Payment (Thanh toán)
   - Return/Refund (Đổi trả / Hoàn tiền)
2. Phân chia tập dữ liệu thành Train (70%), Validation (15%), Test (15%) theo phương pháp Stratified.
3. Trích xuất đặc trưng văn bản bằng TF-IDF Vectorizer (Unigram + Bigram).
4. Huấn luyện và so sánh các mô hình Machine Learning:
   - Naive Bayes: MultinomialNB và ComplementNB
   - Support Vector Machine (SVM): LinearSVC
   - Baseline: Logistic Regression
5. Tối ưu siêu tham số và đánh giá trên tập Validation:
   - Tinh chỉnh alpha cho Naive Bayes
   - Tinh chỉnh C cho LinearSVC
   - Vẽ đồ thị Validation Curve (Train vs Val score)
   - Vẽ đồ thị Learning Curve (đánh giá Overfitting/Underfitting qua các kích thước dữ liệu)
6. Đánh giá toàn diện trên tập Test:
   - Accuracy, Balanced Accuracy, Precision, Recall, F1-Score (Macro & Weighted).
   - Detailed Classification Report cho từng phòng ban.
   - Vẽ Confusion Matrix Heatmap.
   - Vẽ biểu đồ so sánh hiệu năng giữa các mô hình.
7. Ghi Log chi tiết quá trình huấn luyện và lưu Artifacts (Model, Plots, Results).
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend suitable for scripts
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, learning_curve
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB, ComplementNB
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix,
)
import joblib

# Import cấu hình
from config import (
    DATA_FILE,
    SAVED_MODELS_DIR,
    LOGS_DIR,
    PLOTS_DIR,
    RESULTS_DIR,
    TRAIN_RATIO,
    VAL_RATIO,
    TEST_RATIO,
    RANDOM_STATE,
    LABEL_MAPPINGS,
    TFIDF_CONFIG,
    HYPERPARAM_GRIDS,
)


def setup_logger():
    """Thiết lập logging ra cả Console và file training.log."""
    # Đảm bảo mã hóa an toàn trên Windows terminal
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    log_filename = LOGS_DIR / f"training_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    latest_log = LOGS_DIR / "training_latest.log"

    logger = logging.getLogger("TicketRouterLogger")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    # Định dạng log
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Handler ghi file chi tiết (UTF-8 đầy đủ)
    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Handler ghi file latest
    latest_handler = logging.FileHandler(latest_log, mode="w", encoding="utf-8")
    latest_handler.setFormatter(formatter)
    logger.addHandler(latest_handler)

    # Handler hiển thị console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger.info("=" * 80)
    logger.info("=== KHOI DONG PIPELINE HUAN LUYEN VA DANH GIA SUPPORT TICKET ROUTER ===")
    logger.info("=" * 80)
    logger.info(f"[LOG] File duoc luu tai: {log_filename}")
    return logger


def load_and_validate_data(logger):
    """Nạp dữ liệu từ combined_dataset.csv và kiểm tra chất lượng."""
    logger.info(f"📂 Đang đọc dữ liệu từ: {DATA_FILE}")
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Không tìm thấy file dữ liệu: {DATA_FILE}")

    df = pd.read_csv(DATA_FILE, encoding="utf-8")
    logger.info(f"Tổng số dòng ban đầu: {len(df):,}")

    # Làm sạch dữ liệu cơ bản
    df["text"] = df["text"].astype(str).str.strip()
    df["label"] = df["label"].astype(str).str.strip()

    # Loại bỏ giá trị rỗng nếu có
    initial_len = len(df)
    df = df[(df["text"] != "") & (df["label"] != "")]
    if len(df) < initial_len:
        logger.warning(f"Đã loại bỏ {initial_len - len(df)} dòng dữ liệu rỗng.")

    # Lọc chỉ lấy các nhãn nằm trong định nghĩa hệ thống
    valid_labels = set(LABEL_MAPPINGS.keys())
    invalid_rows = ~df["label"].isin(valid_labels)
    if invalid_rows.any():
        logger.warning(f"Phát hiện {invalid_rows.sum()} dòng có nhãn không hợp lệ, tiến hành loại bỏ.")
        df = df[~invalid_rows]

    logger.info(f"✅ Dữ liệu sau kiểm tra: {len(df):,} mẫu hợp lệ.")
    logger.info("📊 Phân bố các lớp tổng quan:")
    for lbl, count in df["label"].value_counts().items():
        pct = count / len(df) * 100
        dept = LABEL_MAPPINGS[lbl]["department"]
        logger.info(f"  - {lbl:18s} ({LABEL_MAPPINGS[lbl]['vi_name']}): {count:6,} mẫu ({pct:5.2f}%) -> {dept}")

    return df


def split_data(df, logger):
    """
    Phân chia dữ liệu thành Train (70%), Val (15%), Test (15%) theo Stratified Split.
    """
    logger.info("-" * 80)
    logger.info("✂️  TIẾN HÀNH PHÂN CHIA DỮ LIỆU: TRAIN (70%) - VAL (15%) - TEST (15%)")
    logger.info("-" * 80)

    X = df["text"].values
    y = df["label"].values

    # Bước 1: Tách Test set (15%)
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X, y, test_size=TEST_RATIO, random_state=RANDOM_STATE, stratify=y
    )

    # Bước 2: Tách Val set từ phần còn lại (15% trên tổng số -> 0.15 / 0.85 ~ 0.17647)
    val_size_adjusted = VAL_RATIO / (TRAIN_RATIO + VAL_RATIO)
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val, y_train_val, test_size=val_size_adjusted, random_state=RANDOM_STATE, stratify=y_train_val
    )

    logger.info(f"✅ Số lượng mẫu tập Train:      {len(X_train):6,} ({len(X_train)/len(df)*100:5.2f}%)")
    logger.info(f"✅ Số lượng mẫu tập Validation: {len(X_val):6,} ({len(X_val)/len(df)*100:5.2f}%)")
    logger.info(f"✅ Số lượng mẫu tập Test:       {len(X_test):6,} ({len(X_test)/len(df)*100:5.2f}%)")

    # Thống kê chi tiết từng lớp
    split_stats = []
    classes = sorted(list(LABEL_MAPPINGS.keys()))

    for cls in classes:
        tr_cnt = np.sum(y_train == cls)
        val_cnt = np.sum(y_val == cls)
        te_cnt = np.sum(y_test == cls)
        tot_cls = tr_cnt + val_cnt + te_cnt
        split_stats.append({
            "Class": cls,
            "Tiếng Việt": LABEL_MAPPINGS[cls]["vi_name"],
            "Train": tr_cnt,
            "Train_Pct": tr_cnt / len(y_train) * 100,
            "Val": val_cnt,
            "Val_Pct": val_cnt / len(y_val) * 100,
            "Test": te_cnt,
            "Test_Pct": te_cnt / len(y_test) * 100,
            "Total": tot_cls,
        })
        logger.info(
            f"  • {cls:16s} | Train: {tr_cnt:5,} ({tr_cnt/len(y_train)*100:5.2f}%) | "
            f"Val: {val_cnt:5,} ({val_cnt/len(y_val)*100:5.2f}%) | "
            f"Test: {te_cnt:5,} ({te_cnt/len(y_test)*100:5.2f}%)"
        )

    # Vẽ biểu đồ phân bố nhãn
    plot_dataset_distribution(split_stats, logger)

    return X_train, X_val, X_test, y_train, y_val, y_test


def plot_dataset_distribution(split_stats, logger):
    """Vẽ biểu đồ phân bố các lớp trên 3 tập Train, Validation, Test."""
    df_stats = pd.DataFrame(split_stats)

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    x = np.arange(len(df_stats))
    width = 0.25

    rects1 = ax.bar(x - width, df_stats["Train"], width, label=f"Train ({TRAIN_RATIO*100:.0f}%)", color="#2b5c8f")
    rects2 = ax.bar(x, df_stats["Val"], width, label=f"Validation ({VAL_RATIO*100:.0f}%)", color="#e27c38")
    rects3 = ax.bar(x + width, df_stats["Test"], width, label=f"Test ({TEST_RATIO*100:.0f}%)", color="#3ea65a")

    ax.set_ylabel("Số lượng mẫu (Tickets / Emails)", fontsize=12, fontweight="bold")
    ax.set_title("Phân bố dữ liệu theo nhãn trên các tập Train, Validation và Test (Stratified)", fontsize=14, fontweight="bold", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{row['Class']}\n({row['Tiếng Việt']})" for _, row in df_stats.iterrows()], fontsize=11)
    ax.legend(fontsize=11)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f"{height:,}",
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 4),  # 4 points vertical offset
                        textcoords="offset points",
                        ha="center", va="bottom", fontsize=9)

    autolabel(rects1)
    autolabel(rects2)
    autolabel(rects3)

    plt.tight_layout()
    out_path = PLOTS_DIR / "dataset_split_distribution.png"
    plt.savefig(out_path)
    plt.close()
    logger.info(f"📊 Đã lưu biểu đồ phân bố dữ liệu: {out_path}")


def tune_and_evaluate_validation(X_train, y_train, X_val, y_val, logger):
    """
    Tối ưu siêu tham số trên tập Validation:
    - Naive Bayes: alpha
    - SVM: C
    - Logistic Regression: C
    Ghi log quá trình và vẽ biểu đồ Validation Curves.
    """
    logger.info("=" * 80)
    logger.info("⚙️  TIẾN HÀNH TRÍCH XUẤT ĐẶC TRƯNG TF-IDF & ĐÁNH GIÁ TRÊN TẬP VALIDATION")
    logger.info("=" * 80)

    # 1. Khởi tạo và Fit TF-IDF trên tập Train
    logger.info(f"Trích xuất đặc trưng văn bản bằng TF-IDF:")
    logger.info(f"  - N-gram range: {TFIDF_CONFIG['ngram_range']}")
    logger.info(f"  - Max features: {TFIDF_CONFIG['max_features']}")
    logger.info(f"  - Sublinear TF: {TFIDF_CONFIG['sublinear_tf']}")

    tfidf = TfidfVectorizer(**TFIDF_CONFIG)
    t0 = time.time()
    X_train_vec = tfidf.fit_transform(X_train)
    X_val_vec = tfidf.transform(X_val)
    vocab_size = len(tfidf.vocabulary_)
    logger.info(f"✅ Đã tạo ma trận TF-IDF: Kích thước từ vựng (Vocabulary size) = {vocab_size:,} trong {time.time()-t0:.2f}s")
    logger.info(f"  - Shape X_train_vec: {X_train_vec.shape}")
    logger.info(f"  - Shape X_val_vec:   {X_val_vec.shape}")

    best_configs = {}
    tuning_history = {}

    # 2. Tinh chỉnh Naive Bayes (MultinomialNB & ComplementNB)
    for model_name, model_cls in [("MultinomialNB", MultinomialNB), ("ComplementNB", ComplementNB)]:
        logger.info("-" * 60)
        logger.info(f"🔍 Thử nghiệm siêu tham số cho {model_name}:")
        alphas = HYPERPARAM_GRIDS[model_name]["alpha"]
        train_accs, val_accs, val_f1s = [], [], []
        best_f1, best_alpha = -1.0, alphas[0]

        for alpha in alphas:
            clf = model_cls(alpha=alpha)
            clf.fit(X_train_vec, y_train)

            train_pred = clf.predict(X_train_vec)
            val_pred = clf.predict(X_val_vec)

            tr_acc = accuracy_score(y_train, train_pred)
            v_acc = accuracy_score(y_val, val_pred)
            v_f1 = precision_recall_fscore_support(y_val, val_pred, average="macro")[2]

            train_accs.append(tr_acc)
            val_accs.append(v_acc)
            val_f1s.append(v_f1)

            logger.info(f"  • alpha={alpha:<5} | Train Acc: {tr_acc*100:6.2f}% | Val Acc: {v_acc*100:6.2f}% | Val Macro-F1: {v_f1*100:6.2f}%")

            if v_f1 > best_f1:
                best_f1 = v_f1
                best_alpha = alpha

        logger.info(f"  🏆 Tối ưu nhất {model_name}: alpha={best_alpha} (Val Macro-F1: {best_f1*100:.2f}%)")
        best_configs[model_name] = {"alpha": best_alpha}
        tuning_history[model_name] = {"param_name": "alpha", "param_vals": alphas, "train_accs": train_accs, "val_accs": val_accs, "val_f1s": val_f1s}

    # 3. Tinh chỉnh Support Vector Machine (LinearSVC)
    logger.info("-" * 60)
    logger.info("🔍 Thử nghiệm siêu tham số cho Support Vector Machine (LinearSVC):")
    c_values = HYPERPARAM_GRIDS["LinearSVC"]["C"]
    train_accs, val_accs, val_f1s = [], [], []
    best_f1, best_c = -1.0, c_values[0]

    for c in c_values:
        clf = LinearSVC(C=c, random_state=RANDOM_STATE, max_iter=3000, dual="auto")
        clf.fit(X_train_vec, y_train)

        train_pred = clf.predict(X_train_vec)
        val_pred = clf.predict(X_val_vec)

        tr_acc = accuracy_score(y_train, train_pred)
        v_acc = accuracy_score(y_val, val_pred)
        v_f1 = precision_recall_fscore_support(y_val, val_pred, average="macro")[2]

        train_accs.append(tr_acc)
        val_accs.append(v_acc)
        val_f1s.append(v_f1)

        logger.info(f"  • C={c:<5} | Train Acc: {tr_acc*100:6.2f}% | Val Acc: {v_acc*100:6.2f}% | Val Macro-F1: {v_f1*100:6.2f}%")

        if v_f1 > best_f1:
            best_f1 = v_f1
            best_c = c

    logger.info(f"  🏆 Tối ưu nhất LinearSVC: C={best_c} (Val Macro-F1: {best_f1*100:.2f}%)")
    best_configs["LinearSVC"] = {"C": best_c}
    tuning_history["LinearSVC"] = {"param_name": "C", "param_vals": c_values, "train_accs": train_accs, "val_accs": val_accs, "val_f1s": val_f1s}

    # 4. Tinh chỉnh Logistic Regression Baseline
    logger.info("-" * 60)
    logger.info("🔍 Thử nghiệm siêu tham số cho Logistic Regression Baseline:")
    lr_c_values = HYPERPARAM_GRIDS["LogisticRegression"]["C"]
    train_accs, val_accs, val_f1s = [], [], []
    best_f1, best_lr_c = -1.0, lr_c_values[0]

    for c in lr_c_values:
        clf = LogisticRegression(C=c, random_state=RANDOM_STATE, max_iter=1000)
        clf.fit(X_train_vec, y_train)

        train_pred = clf.predict(X_train_vec)
        val_pred = clf.predict(X_val_vec)

        tr_acc = accuracy_score(y_train, train_pred)
        v_acc = accuracy_score(y_val, val_pred)
        v_f1 = precision_recall_fscore_support(y_val, val_pred, average="macro")[2]

        train_accs.append(tr_acc)
        val_accs.append(v_acc)
        val_f1s.append(v_f1)

        logger.info(f"  • C={c:<5} | Train Acc: {tr_acc*100:6.2f}% | Val Acc: {v_acc*100:6.2f}% | Val Macro-F1: {v_f1*100:6.2f}%")

        if v_f1 > best_f1:
            best_f1 = v_f1
            best_lr_c = c

    logger.info(f"  🏆 Tối ưu nhất LogisticRegression: C={best_lr_c} (Val Macro-F1: {best_f1*100:.2f}%)")
    best_configs["LogisticRegression"] = {"C": best_lr_c}
    tuning_history["LogisticRegression"] = {"param_name": "C", "param_vals": lr_c_values, "train_accs": train_accs, "val_accs": val_accs, "val_f1s": val_f1s}

    # Vẽ đồ thị Tuning / Validation Curves
    plot_validation_curves(tuning_history, logger)

    return tfidf, best_configs, X_train_vec, X_val_vec


def plot_validation_curves(tuning_history, logger):
    """Vẽ đồ thị hiệu năng Train vs Validation khi thay đổi siêu tham số."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), dpi=300)
    axes = axes.flatten()

    models = ["ComplementNB", "MultinomialNB", "LinearSVC", "LogisticRegression"]

    for idx, model_name in enumerate(models):
        ax = axes[idx]
        hist = tuning_history[model_name]
        param_vals = [str(p) for p in hist["param_vals"]]

        ax.plot(param_vals, [a * 100 for a in hist["train_accs"]], marker="o", linewidth=2, label="Train Accuracy", color="#2b5c8f")
        ax.plot(param_vals, [a * 100 for a in hist["val_accs"]], marker="s", linewidth=2, label="Validation Accuracy", color="#e27c38")
        ax.plot(param_vals, [f * 100 for f in hist["val_f1s"]], marker="^", linewidth=2, linestyle="--", label="Val Macro-F1", color="#3ea65a")

        ax.set_title(f"Validation Curve: {model_name}", fontsize=13, fontweight="bold")
        ax.set_xlabel(f"Hyperparameter ({hist['param_name']})", fontsize=11, fontweight="bold")
        ax.set_ylabel("Score (%)", fontsize=11, fontweight="bold")
        ax.legend(fontsize=10)
        ax.grid(True, linestyle=":", alpha=0.6)

    plt.suptitle("Đánh giá Siêu tham số trên Train vs Validation (Độ nhạy & Khả năng Tổng quát hóa)", fontsize=15, fontweight="bold", y=1.00)
    plt.tight_layout()
    out_path = PLOTS_DIR / "validation_curves.png"
    plt.savefig(out_path)
    plt.close()
    logger.info(f"📊 Đã lưu đồ thị Validation Curves: {out_path}")


def compute_and_plot_learning_curves(tfidf, best_configs, X_train, y_train, logger):
    """
    Tính toán và vẽ Learning Curve (Train score vs Validation score theo số lượng mẫu huấn luyện)
    để phát hiện Overfitting (High Variance) hoặc Underfitting (High Bias).
    """
    logger.info("=" * 80)
    logger.info("📈 ĐANG TÍNH TOÁN LEARNING CURVE CHO CÁC MÔ HÌNH CHÍNH (TRAIN vs VAL)")
    logger.info("=" * 80)

    train_sizes = np.linspace(0.1, 1.0, 5)

    models_to_plot = {
        "ComplementNB": ComplementNB(**best_configs["ComplementNB"]),
        "LinearSVC": LinearSVC(**best_configs["LinearSVC"], random_state=RANDOM_STATE, max_iter=3000, dual="auto"),
    }

    fig, axes = plt.subplots(1, 2, figsize=(14, 6), dpi=300)

    for idx, (name, clf) in enumerate(models_to_plot.items()):
        ax = axes[idx]
        logger.info(f"Đang tính toán Learning Curve cho {name} qua 5 kích thước dữ liệu (5-Fold CV)...")

        pipe = Pipeline([
            ("tfidf", TfidfVectorizer(**TFIDF_CONFIG)),
            ("clf", clf)
        ])

        # Sử dụng 3-fold cross validation trên tập Train để tốc độ nhanh và đáng tin cậy
        tr_sizes, tr_scores, val_scores = learning_curve(
            pipe,
            X_train,
            y_train,
            train_sizes=train_sizes,
            cv=3,
            scoring="accuracy",
            n_jobs=1,
            random_state=RANDOM_STATE,
        )

        tr_mean = np.mean(tr_scores, axis=1) * 100
        tr_std = np.std(tr_scores, axis=1) * 100
        val_mean = np.mean(val_scores, axis=1) * 100
        val_std = np.std(val_scores, axis=1) * 100

        for sz, tm, vm in zip(tr_sizes, tr_mean, val_mean):
            logger.info(f"  - Samples: {sz:5,} | Train Acc: {tm:5.2f}% | Val Acc: {vm:5.2f}% (Gap: {tm-vm:4.2f}%)")

        ax.plot(tr_sizes, tr_mean, "o-", color="#2b5c8f", label="Training Score (Train Acc)", linewidth=2)
        ax.fill_between(tr_sizes, tr_mean - tr_std, tr_mean + tr_std, alpha=0.15, color="#2b5c8f")

        ax.plot(tr_sizes, val_mean, "s-", color="#e27c38", label="Cross-Validation Score (Val Acc)", linewidth=2)
        ax.fill_between(tr_sizes, val_mean - val_std, val_mean + val_std, alpha=0.15, color="#e27c38")

        ax.set_title(f"Learning Curve: {name}", fontsize=13, fontweight="bold")
        ax.set_xlabel("Số lượng mẫu huấn luyện (Training Samples)", fontsize=11, fontweight="bold")
        ax.set_ylabel("Accuracy Score (%)", fontsize=11, fontweight="bold")
        ax.legend(loc="lower right", fontsize=10)
        ax.grid(True, linestyle="--", alpha=0.6)

    plt.suptitle("Đồ thị Learning Curves: Phân tích Bias - Variance & Khả năng Hội tụ của Mô hình", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    out_path = PLOTS_DIR / "learning_curves.png"
    plt.savefig(out_path)
    plt.close()
    logger.info(f"📊 Đã lưu đồ thị Learning Curves: {out_path}")


def evaluate_on_test_set(tfidf, best_configs, X_train, y_train, X_val, y_val, X_test, y_test, logger):
    """
    Huấn luyện mô hình tốt nhất trên (Train + Val) và đánh giá chi tiết các metrics trên tập TEST độc lập.
    """
    logger.info("=" * 80)
    logger.info("🧪 ĐÁNH GIÁ CÁC METRICS TRÊN TẬP TEST ĐỘC LẬP (UNSEEN DATA)")
    logger.info("=" * 80)

    # Gộp Train và Val để huấn luyện mô hình hoàn chỉnh nhất cho tập Test
    X_full_train = np.concatenate([X_train, X_val])
    y_full_train = np.concatenate([y_train, y_val])

    logger.info(f"Số lượng mẫu huấn luyện mô hình chính thức: {len(X_full_train):,} mẫu")
    logger.info(f"Số lượng mẫu kiểm tra tập Test:            {len(X_test):,} mẫu")

    candidate_models = {
        "Naive Bayes (ComplementNB)": ComplementNB(**best_configs["ComplementNB"]),
        "Naive Bayes (MultinomialNB)": MultinomialNB(**best_configs["MultinomialNB"]),
        "Support Vector Machine (LinearSVC)": LinearSVC(**best_configs["LinearSVC"], random_state=RANDOM_STATE, max_iter=3000, dual="auto"),
        "Logistic Regression (Baseline)": LogisticRegression(**best_configs["LogisticRegression"], random_state=RANDOM_STATE, max_iter=1000),
    }

    test_results = {}
    fitted_pipelines = {}
    classes = sorted(list(LABEL_MAPPINGS.keys()))

    for model_name, clf in candidate_models.items():
        logger.info("-" * 75)
        logger.info(f"🚀 Đang huấn luyện & đánh giá: {model_name}")

        pipe = Pipeline([
            ("tfidf", TfidfVectorizer(**TFIDF_CONFIG)),
            ("clf", clf)
        ])

        t_start = time.time()
        pipe.fit(X_full_train, y_full_train)
        train_time = time.time() - t_start

        # Dự đoán trên Test
        t_infer = time.time()
        y_pred = pipe.predict(X_test)
        infer_time = time.time() - t_infer

        # Tính toán các chỉ số
        acc = accuracy_score(y_test, y_pred)
        bal_acc = balanced_accuracy_score(y_test, y_pred)
        p_macro, r_macro, f1_macro, _ = precision_recall_fscore_support(y_test, y_pred, average="macro")
        p_weighted, r_weighted, f1_weighted, _ = precision_recall_fscore_support(y_test, y_pred, average="weighted")

        report_dict = classification_report(y_test, y_pred, output_dict=True, target_names=classes)
        cm = confusion_matrix(y_test, y_pred, labels=classes)

        fitted_pipelines[model_name] = pipe

        test_results[model_name] = {
            "accuracy": float(acc),
            "balanced_accuracy": float(bal_acc),
            "macro_precision": float(p_macro),
            "macro_recall": float(r_macro),
            "macro_f1": float(f1_macro),
            "weighted_precision": float(p_weighted),
            "weighted_recall": float(r_weighted),
            "weighted_f1": float(f1_weighted),
            "train_time_sec": float(train_time),
            "infer_time_sec": float(infer_time),
            "classification_report": report_dict,
            "confusion_matrix": cm.tolist(),
        }

        logger.info(f"  ⏱️  Thời gian Train: {train_time:.2f}s | Infer {len(X_test)} mẫu: {infer_time:.4f}s")
        logger.info(f"  🎯 Test Accuracy:          {acc*100:6.2f}%")
        logger.info(f"  🎯 Test Balanced Accuracy: {bal_acc*100:6.2f}%")
        logger.info(f"  🎯 Test Macro F1-Score:    {f1_macro*100:6.2f}%")
        logger.info(f"  🎯 Test Weighted F1-Score: {f1_weighted*100:6.2f}%")
        logger.info(f"\n  📋 Báo cáo chi tiết từng phòng ban:")
        for cls in classes:
            r = report_dict[cls]
            dept_name = LABEL_MAPPINGS[cls]["vi_name"]
            logger.info(
                f"    • {cls:16s} ({dept_name}): "
                f"Precision={r['precision']*100:5.2f}% | "
                f"Recall={r['recall']*100:5.2f}% | "
                f"F1={r['f1-score']*100:5.2f}% | Support={r['support']:,}"
            )

    # Chọn mô hình tốt nhất dựa trên Macro F1 trên tập Test
    best_model_name = max(test_results.keys(), key=lambda k: test_results[k]["macro_f1"])
    best_pipe = fitted_pipelines[best_model_name]
    logger.info("=" * 80)
    logger.info(f"👑 MÔ HÌNH TỐT NHẤT LÀ: {best_model_name}")
    logger.info(f"   Accuracy: {test_results[best_model_name]['accuracy']*100:.2f}% | Macro F1: {test_results[best_model_name]['macro_f1']*100:.2f}%")
    logger.info("=" * 80)

    # Lưu kết quả ra JSON và CSV
    save_results_and_plots(test_results, classes, best_model_name, best_pipe, logger)

    return test_results, best_model_name, best_pipe


def save_results_and_plots(test_results, classes, best_model_name, best_pipe, logger):
    """Lưu trữ kết quả JSON, CSV và vẽ đồ thị đánh giá Test."""
    # 1. Lưu file JSON tổng hợp
    summary_path = RESULTS_DIR / "test_evaluation_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2)
    logger.info(f"💾 Đã lưu tóm tắt kết quả: {summary_path}")

    # 2. Lưu bảng CSV so sánh
    rows = []
    for name, res in test_results.items():
        rows.append({
            "Model": name,
            "Accuracy (%)": round(res["accuracy"] * 100, 2),
            "Balanced Acc (%)": round(res["balanced_accuracy"] * 100, 2),
            "Macro F1 (%)": round(res["macro_f1"] * 100, 2),
            "Weighted F1 (%)": round(res["weighted_f1"] * 100, 2),
            "Macro Precision (%)": round(res["macro_precision"] * 100, 2),
            "Macro Recall (%)": round(res["macro_recall"] * 100, 2),
            "Train Time (s)": round(res["train_time_sec"], 2),
        })
    df_compare = pd.DataFrame(rows)
    csv_path = RESULTS_DIR / "model_comparison_metrics.csv"
    df_compare.to_csv(csv_path, index=False, encoding="utf-8-sig")
    logger.info(f"💾 Đã lưu bảng so sánh metrics: {csv_path}")

    # 3. Vẽ biểu đồ so sánh các metrics
    fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
    models = list(test_results.keys())
    x = np.arange(len(models))
    width = 0.18

    accs = [test_results[m]["accuracy"] * 100 for m in models]
    mf1s = [test_results[m]["macro_f1"] * 100 for m in models]
    wf1s = [test_results[m]["weighted_f1"] * 100 for m in models]
    precs = [test_results[m]["macro_precision"] * 100 for m in models]
    recs = [test_results[m]["macro_recall"] * 100 for m in models]

    r1 = ax.bar(x - 2 * width, accs, width, label="Accuracy", color="#2b5c8f")
    r2 = ax.bar(x - width, mf1s, width, label="Macro F1-Score", color="#e27c38")
    r3 = ax.bar(x, wf1s, width, label="Weighted F1-Score", color="#3ea65a")
    r4 = ax.bar(x + width, precs, width, label="Macro Precision", color="#8b5cf6")
    r5 = ax.bar(x + 2 * width, recs, width, label="Macro Recall", color="#ec4899")

    ax.set_ylabel("Điểm số (%)", fontsize=12, fontweight="bold")
    ax.set_title("So sánh Hiệu năng các Mô hình Phân loại Khiếu nại trên Tập Test", fontsize=14, fontweight="bold", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels([m.replace(" (", "\n(") for m in models], fontsize=10, fontweight="bold")
    ax.set_ylim(80, 102)
    ax.legend(loc="lower right", fontsize=10)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    for rect_group in [r1, r2, r3, r4, r5]:
        for rect in rect_group:
            h = rect.get_height()
            ax.annotate(f"{h:.1f}%",
                        xy=(rect.get_x() + rect.get_width() / 2, h),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha="center", va="bottom", fontsize=7.5, rotation=45)

    plt.tight_layout()
    plot_compare_path = PLOTS_DIR / "model_comparison_metrics.png"
    plt.savefig(plot_compare_path)
    plt.close()
    logger.info(f"📊 Đã lưu biểu đồ so sánh: {plot_compare_path}")

    # 4. Vẽ Heatmap Confusion Matrix cho tất cả các mô hình
    fig, axes = plt.subplots(2, 2, figsize=(14, 12), dpi=300)
    axes = axes.flatten()

    class_vi_labels = [f"{cls}\n({LABEL_MAPPINGS[cls]['vi_name']})" for cls in classes]

    for idx, (m_name, res) in enumerate(test_results.items()):
        ax = axes[idx]
        cm = np.array(res["confusion_matrix"])
        cm_norm = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis] * 100

        # Hiển thị số lượng và phần trăm
        annot = np.empty_like(cm, dtype=object)
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                annot[i, j] = f"{cm[i, j]:,}\n({cm_norm[i, j]:.1f}%)"

        sns.heatmap(
            cm,
            annot=annot,
            fmt="",
            cmap="Blues",
            ax=ax,
            cbar=False,
            xticklabels=class_vi_labels,
            yticklabels=class_vi_labels,
            annot_kws={"size": 10, "fontweight": "bold"}
        )

        acc_pct = res["accuracy"] * 100
        f1_pct = res["macro_f1"] * 100
        ax.set_title(f"{m_name}\nAcc: {acc_pct:.2f}% | Macro F1: {f1_pct:.2f}%", fontsize=12, fontweight="bold")
        ax.set_xlabel("Nhãn Dự Đoán (Predicted)", fontsize=10, fontweight="bold")
        ax.set_ylabel("Nhãn Thực Tế (Actual)", fontsize=10, fontweight="bold")

    plt.suptitle("Ma Trận Nhầm Lẫn (Confusion Matrix) trên Tập Test Độc Lập", fontsize=15, fontweight="bold", y=0.99)
    plt.tight_layout()
    cm_path = PLOTS_DIR / "confusion_matrices_all_models.png"
    plt.savefig(cm_path)
    plt.close()
    logger.info(f"📊 Đã lưu Ma trận nhầm lẫn: {cm_path}")

    # 5. Lưu mô hình tốt nhất vào saved_models/
    model_save_path = SAVED_MODELS_DIR / "best_ticket_router_pipeline.joblib"
    joblib.dump({
        "pipeline": best_pipe,
        "model_name": best_model_name,
        "classes": classes,
        "label_mappings": LABEL_MAPPINGS,
        "metrics": test_results[best_model_name],
        "created_at": datetime.now().isoformat(),
    }, model_save_path)
    logger.info(f"💾 ĐÃ LƯU MÔ HÌNH XUẤT SẮC NHẤT TẠI: {model_save_path}")


def main():
    logger = setup_logger()
    try:
        # 1. Đọc và kiểm tra dữ liệu
        df = load_and_validate_data(logger)

        # 2. Phân chia Train / Val / Test
        X_train, X_val, X_test, y_train, y_val, y_test = split_data(df, logger)

        # 3. Trích xuất đặc trưng & Tinh chỉnh siêu tham số trên Validation
        tfidf, best_configs, X_train_vec, X_val_vec = tune_and_evaluate_validation(
            X_train, y_train, X_val, y_val, logger
        )

        # 4. Vẽ đồ thị Learning Curves trên Train vs Validation
        compute_and_plot_learning_curves(tfidf, best_configs, X_train, y_train, logger)

        # 5. Đánh giá toàn diện trên tập Test
        test_results, best_model_name, best_pipe = evaluate_on_test_set(
            tfidf, best_configs, X_train, y_train, X_val, y_val, X_test, y_test, logger
        )

        logger.info("=" * 80)
        logger.info("🎉 HOÀN THÀNH QUÁ TRÌNH HUẤN LUYỆN VÀ ĐÁNH GIÁ THÀNH CÔNG RỰC RỠ!")
        logger.info(f"📂 Thư mục chứa mô hình:  {SAVED_MODELS_DIR}")
        logger.info(f"📂 Thư mục chứa đồ thị:   {PLOTS_DIR}")
        logger.info(f"📂 Thư mục chứa kết quả: {RESULTS_DIR}")
        logger.info(f"📂 Thư mục chứa log:      {LOGS_DIR}")
        logger.info("=" * 80)

    except Exception as e:
        logger.exception(f"❌ Xảy ra lỗi trong quá trình thực thi: {str(e)}")
        raise


if __name__ == "__main__":
    main()
