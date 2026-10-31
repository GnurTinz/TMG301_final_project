"""
Script chạy phân tích EDA tự động cho bộ dữ liệu Banking77
Tự động xuất bảng thống kê ra terminal và lưu toàn bộ biểu đồ vào thư mục EDA/plots/
"""

import os
import re
from pathlib import Path
from collections import Counter

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def main():
    print("=" * 70)
    print(" 🚀 BẮT ĐẦU QUÁ TRÌNH KHÁM PHÁ & PHÂN TÍCH DỮ LIỆU (EDA) - BANKING77")
    print("=" * 70)

    # 1. Tìm kiếm đường dẫn dữ liệu
    candidate_paths = [
        Path("datasets/banking77"),
        Path("../datasets/banking77"),
        Path.cwd() / "datasets" / "banking77",
        Path.cwd().parent / "datasets" / "banking77",
    ]

    data_dir = None
    for p in candidate_paths:
        if (p / "banking77_train.csv").exists() and (p / "banking77_test.csv").exists():
            data_dir = p
            break

    if data_dir is None:
        raise FileNotFoundError(
            "Không tìm thấy thư mục chứa datasets/banking77. "
            "Vui lòng chạy script download_banking77.py trước."
        )

    # Thư mục lưu biểu đồ
    plots_dir = Path("EDA/plots")
    if not plots_dir.parent.exists():
        plots_dir = Path("plots")
    plots_dir.mkdir(parents=True, exist_ok=True)

    # Cấu hình matplotlib
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    plt.rcParams["figure.figsize"] = (12, 6)
    plt.rcParams["font.size"] = 10

    # 2. Đọc dữ liệu
    train_df = pd.read_csv(data_dir / "banking77_train.csv")
    test_df = pd.read_csv(data_dir / "banking77_test.csv")

    n_train = len(train_df)
    n_test = len(test_df)
    total = n_train + n_test

    print(f"\n[1] KÍCH THƯỚC DỮ LIỆU:")
    print(f" - Train: {n_train:,} mẫu ({n_train / total * 100:.2f}%)")
    print(f" - Test:  {n_test:,} mẫu ({n_test / total * 100:.2f}%)")
    print(f" - Tổng:  {total:,} mẫu")

    # 3. Kiểm tra missing & duplicates
    print(f"\n[2] KIỂM TRA CHẤT LƯỢNG DỮ LIỆU:")
    print(f" - Missing values ở Train: {train_df.isnull().sum().to_dict()}")
    print(f" - Missing values ở Test:  {test_df.isnull().sum().to_dict()}")
    print(f" - Dòng trùng lặp hoàn toàn (Train): {train_df.duplicated().sum()}")
    print(f" - Dòng trùng lặp hoàn toàn (Test):  {test_df.duplicated().sum()}")
    overlap_texts = set(train_df["text"]).intersection(set(test_df["text"]))
    print(f" - Số câu trùng lặp giữa Train và Test (Leakage): {len(overlap_texts)}")

    # 4. Tập nhãn
    train_labels = set(train_df["category"].unique())
    test_labels = set(test_df["category"].unique())
    print(f"\n[3] TẬP NHÃN (LABEL SET):")
    print(f" - Số nhãn duy nhất ở Train: {len(train_labels)}")
    print(f" - Số nhãn duy nhất ở Test:  {len(test_labels)}")
    print(f" - Khớp nhãn 100% giữa Train và Test: {train_labels == test_labels}")

    # 5. Phân bố nhãn
    train_counts = train_df["category"].value_counts()
    test_counts = test_df["category"].value_counts()
    dist_df = pd.concat([train_counts.rename("train"), test_counts.rename("test")], axis=1)

    print(f"\n[4] THỐNG KÊ PHÂN BỐ NHÃN:")
    print(f" - Train: Min = {train_counts.min()}, Max = {train_counts.max()}, Mean = {train_counts.mean():.1f}, Std = {train_counts.std():.1f}")
    print(f" - Test:  Min = {test_counts.min()}, Max = {test_counts.max()}, Mean = {test_counts.mean():.1f}, Std = {test_counts.std():.1f}")

    # 6. Biểu đồ tròn Train/Test
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(
        [n_train, n_test],
        labels=[f"Train ({n_train:,})", f"Test ({n_test:,})"],
        autopct="%1.2f%%",
        startangle=140,
        colors=["#1d3557", "#457b9d"],
        explode=(0.05, 0),
        textprops={"fontsize": 11, "weight": "bold"},
    )
    ax.set_title("Tỷ lệ phân chia tập Train và Test trong Banking77", fontsize=13)
    fig.savefig(plots_dir / "01_train_test_split.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    # 7. Biểu đồ Histogram phân bố số lượng mẫu/nhãn
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    sns.histplot(train_counts, kde=True, ax=axes[0], color="#2b5c8f", bins=15)
    axes[0].axvline(train_counts.mean(), color="red", linestyle="--", label=f"Mean: {train_counts.mean():.1f}")
    axes[0].set_title("Phân bố Số mẫu / nhãn (Tập Train)")
    axes[0].set_xlabel("Số mẫu")
    axes[0].set_ylabel("Số lượng nhãn")
    axes[0].legend()

    sns.histplot(test_counts, kde=True, ax=axes[1], color="#e76f51", bins=10)
    axes[1].axvline(test_counts.mean(), color="red", linestyle="--", label=f"Mean: {test_counts.mean():.1f}")
    axes[1].set_title("Phân bố Số mẫu / nhãn (Tập Test)")
    axes[1].set_xlabel("Số mẫu")
    axes[1].set_ylabel("Số lượng nhãn")
    axes[1].legend()

    plt.tight_layout()
    fig.savefig(plots_dir / "02_label_distribution_hist.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    # 8. Top 15 và Bottom 15
    top_15 = dist_df.sort_values(by="train", ascending=False).head(15)
    bottom_15 = dist_df.sort_values(by="train", ascending=True).head(15)

    fig, axes = plt.subplots(2, 1, figsize=(14, 12))
    x = np.arange(15)
    width = 0.35
    axes[0].bar(x - width/2, top_15["train"], width, label="Train", color="#1d3557")
    axes[0].bar(x + width/2, top_15["test"], width, label="Test", color="#457b9d")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(top_15.index, rotation=35, ha="right")
    axes[0].set_ylabel("Số lượng mẫu")
    axes[0].set_title("Top 15 Nhãn có nhiều mẫu nhất (Train vs Test)")
    axes[0].legend()

    axes[1].bar(x - width/2, bottom_15["train"], width, label="Train", color="#e63946")
    axes[1].bar(x + width/2, bottom_15["test"], width, label="Test", color="#f4a261")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(bottom_15.index, rotation=35, ha="right")
    axes[1].set_ylabel("Số lượng mẫu")
    axes[1].set_title("Top 15 Nhãn có ít mẫu nhất (Train vs Test)")
    axes[1].legend()

    plt.tight_layout()
    fig.savefig(plots_dir / "03_top_bottom_15_labels.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    # 9. Toàn bộ 77 nhãn
    fig, ax = plt.subplots(figsize=(12, 22))
    sorted_full = dist_df.sort_values(by="train", ascending=True)
    y_pos = np.arange(len(sorted_full))
    ax.barh(y_pos, sorted_full["train"], height=0.65, color="#2a9d8f", alpha=0.9, label="Train")
    ax.barh(y_pos, sorted_full["test"], height=0.65, color="#e76f51", alpha=0.7, label="Test")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(sorted_full.index, fontsize=8)
    ax.set_xlabel("Số lượng mẫu")
    ax.set_title("So sánh phân bố toàn bộ 77 Nhãn (Train vs Test)", fontsize=14, weight="bold")
    ax.legend(loc="lower right")
    plt.tight_layout()
    fig.savefig(plots_dir / "04_full_77_labels.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    # 10. Phân tích độ dài câu
    train_df["word_count"] = train_df["text"].astype(str).apply(lambda x: len(x.split()))
    test_df["word_count"] = test_df["text"].astype(str).apply(lambda x: len(x.split()))
    train_df["char_length"] = train_df["text"].astype(str).apply(len)
    test_df["char_length"] = test_df["text"].astype(str).apply(len)

    print(f"\n[5] THỐNG KÊ ĐỘ DÀI VĂN BẢN (WORD COUNT):")
    print(f" - Train: Min = {train_df['word_count'].min()}, Mean = {train_df['word_count'].mean():.1f}, Median = {train_df['word_count'].median()}, 95th = {train_df['word_count'].quantile(0.95):.0f}, Max = {train_df['word_count'].max()}")
    print(f" - Test:  Min = {test_df['word_count'].min()}, Mean = {test_df['word_count'].mean():.1f}, Median = {test_df['word_count'].median()}, 95th = {test_df['word_count'].quantile(0.95):.0f}, Max = {test_df['word_count'].max()}")

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    sns.histplot(train_df["word_count"], kde=True, ax=axes[0, 0], color="#1d3557", label="Train", bins=30, stat="density")
    sns.histplot(test_df["word_count"], kde=True, ax=axes[0, 0], color="#e76f51", label="Test", bins=30, stat="density", alpha=0.6)
    axes[0, 0].set_title("Phân phối Số từ mỗi câu (Word Count)")
    axes[0, 0].legend()

    sns.histplot(train_df["char_length"], kde=True, ax=axes[0, 1], color="#2a9d8f", label="Train", bins=40, stat="density")
    sns.histplot(test_df["char_length"], kde=True, ax=axes[0, 1], color="#f4a261", label="Test", bins=40, stat="density", alpha=0.6)
    axes[0, 1].set_title("Phân phối Số ký tự mỗi câu (Character Length)")
    axes[0, 1].legend()

    combined_words = pd.concat([
        pd.DataFrame({"Word Count": train_df["word_count"], "Tập dữ liệu": "Train"}),
        pd.DataFrame({"Word Count": test_df["word_count"], "Tập dữ liệu": "Test"}),
    ])
    sns.boxplot(x="Tập dữ liệu", y="Word Count", hue="Tập dữ liệu", data=combined_words, ax=axes[1, 0], palette=["#1d3557", "#e76f51"], legend=False)
    axes[1, 0].set_title("Boxplot Số từ")

    combined_chars = pd.concat([
        pd.DataFrame({"Character Length": train_df["char_length"], "Tập dữ liệu": "Train"}),
        pd.DataFrame({"Character Length": test_df["char_length"], "Tập dữ liệu": "Test"}),
    ])
    sns.boxplot(x="Tập dữ liệu", y="Character Length", hue="Tập dữ liệu", data=combined_chars, ax=axes[1, 1], palette=["#2a9d8f", "#f4a261"], legend=False)
    axes[1, 1].set_title("Boxplot Số ký tự")

    plt.tight_layout()
    fig.savefig(plots_dir / "05_text_length_distribution.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    # 11. Từ vựng & Bigrams
    def tokenize(text):
        return re.findall(r"\b[a-zA-Z]{2,}\b", text.lower())

    stopwords = set([
        "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", 
        "he", "him", "his", "she", "her", "it", "its", "they", "them", "their", "what", "which", 
        "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", 
        "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", 
        "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", 
        "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", 
        "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", 
        "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", 
        "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", 
        "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", 
        "now", "d", "ll", "m", "o", "re", "ve", "y", "ain", "aren", "couldn", "did", "didn", "doesn", "hadn", 
        "hasn", "haven", "isn", "ma", "mightn", "mustn", "needn", "shan", "shouldn", "wasn", "weren", 
        "won", "wouldn"
    ])

    train_tokens = [tok for text in train_df["text"] for tok in tokenize(text)]
    test_tokens = [tok for text in test_df["text"] for tok in tokenize(text)]
    train_vocab = set(train_tokens)
    test_vocab = set(test_tokens)
    oov_words = test_vocab - train_vocab
    oov_token_count = sum(1 for tok in test_tokens if tok in oov_words)

    print(f"\n[6] VỐN TỪ VỰNG & HIỆN TƯỢNG OOV:")
    print(f" - Train Vocab: {len(train_vocab):,} từ")
    print(f" - Test Vocab:  {len(test_vocab):,} từ")
    print(f" - Số từ OOV (Test có, Train không): {len(oov_words):,} từ")
    print(f" - Tỷ lệ Token OOV ở Test: {oov_token_count / len(test_tokens) * 100:.2f}%")

    train_clean_words = [w for w in train_tokens if w not in stopwords]
    top_20_words = Counter(train_clean_words).most_common(20)

    bigrams_list = []
    for text in train_df["text"]:
        words = [w for w in tokenize(text) if w not in stopwords]
        for i in range(len(words) - 1):
            bigrams_list.append(f"{words[i]} {words[i+1]}")
    top_15_bigrams = Counter(bigrams_list).most_common(15)

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    words_df = pd.DataFrame(top_20_words, columns=["Word", "Frequency"]).sort_values("Frequency")
    axes[0].barh(words_df["Word"], words_df["Frequency"], color="#457b9d")
    axes[0].set_title("Top 20 Từ khóa xuất hiện nhiều nhất (Đã lọc Stopwords)")
    axes[0].set_xlabel("Tần suất")

    bigrams_df = pd.DataFrame(top_15_bigrams, columns=["Bigram", "Frequency"]).sort_values("Frequency")
    axes[1].barh(bigrams_df["Bigram"], bigrams_df["Frequency"], color="#e76f51")
    axes[1].set_title("Top 15 Cụm 2 từ (Bigrams) phổ biến nhất")
    axes[1].set_xlabel("Tần suất")

    plt.tight_layout()
    fig.savefig(plots_dir / "06_top_words_bigrams.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    print(f"\n✅ ĐÃ HOÀN THÀNH PHÂN TÍCH VÀ LƯU 6 BIỂU ĐỒ TẠI: {plots_dir.resolve()}")
    print("=" * 70)


if __name__ == "__main__":
    main()
