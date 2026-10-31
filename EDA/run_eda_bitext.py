"""
Script chạy phân tích EDA tự động cho bộ dữ liệu Bitext Sample Customer Support
Tự động in báo cáo chi tiết ra terminal và lưu toàn bộ biểu đồ vào thư mục EDA/plots_bitext/
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
    print("=" * 75)
    print(" 🚀 BẮT ĐẦU PHÂN TÍCH EDA - BITEXT SAMPLE CUSTOMER SUPPORT DATASET")
    print("=" * 75)

    # 1. Tìm đường dẫn file dữ liệu
    candidate_paths = [
        Path("datasets/Bitext_Sample_Customer_Support"),
        Path("../datasets/Bitext_Sample_Customer_Support"),
        Path.cwd() / "datasets" / "Bitext_Sample_Customer_Support",
        Path.cwd().parent / "datasets" / "Bitext_Sample_Customer_Support",
    ]

    target_filename = "Bitext_Sample_Customer_Support_Training_Dataset_27K_responses-v11.csv"
    file_path = None
    for p in candidate_paths:
        if (p / target_filename).exists():
            file_path = p / target_filename
            break

    if file_path is None:
        raise FileNotFoundError(
            f"Không tìm thấy file {target_filename} trong thư mục datasets/Bitext_Sample_Customer_Support!"
        )

    # Thư mục lưu plots
    plots_dir = Path("EDA/plots_bitext")
    if not plots_dir.parent.exists():
        plots_dir = Path("plots_bitext")
    plots_dir.mkdir(parents=True, exist_ok=True)

    # Cấu hình biểu đồ
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    plt.rcParams["figure.figsize"] = (12, 6)
    plt.rcParams["font.size"] = 10

    # 2. Đọc file
    print(f"\n[1] ĐANG ĐỌC DỮ LIỆU: {file_path.name}")
    df = pd.read_csv(file_path, encoding="utf-8")
    n_rows, n_cols = df.shape
    mem_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)

    print(f" - Kích thước: {n_rows:,} dòng x {n_cols} cột")
    print(f" - Bộ nhớ RAM: {mem_mb:.2f} MB")
    print(f" - Các cột:    {list(df.columns)}")

    # 3. Kiểm tra missing & duplicates
    print(f"\n[2] KIỂM TRA CHẤT LƯỢNG:")
    print(f" - Missing values: {df.isnull().sum().to_dict()}")
    print(f" - Dòng trùng lặp hoàn toàn:     {df.duplicated().sum()}")
    print(f" - Câu hỏi (`instruction`) trùng: {df.duplicated(subset=['instruction']).sum():,}")
    print(f" - Phản hồi (`response`) trùng:   {df.duplicated(subset=['response']).sum():,}")

    # 4. Tập nhãn
    cats = sorted(df["category"].unique())
    ints = sorted(df["intent"].unique())
    print(f"\n[3] TẬP NHÃN PHÂN CẤP:")
    print(f" - Số lượng Category cấp cao: {len(cats)} danh mục -> {cats}")
    print(f" - Số lượng Intent chi tiết:  {len(ints)} intents")

    cat_counts = df["category"].value_counts()
    intent_counts = df["intent"].value_counts()
    print(f"\n[4] PHÂN BỐ NHÃN (CLASS BALANCE):")
    print(f" - Intents: Min = {intent_counts.min()}, Max = {intent_counts.max()}, Mean = {intent_counts.mean():.1f}, Std = {intent_counts.std():.1f}")
    print(f" - Tỷ lệ mất cân bằng Intent (Max/Min): {intent_counts.max() / intent_counts.min():.2f}x (Cực kỳ cân bằng)")

    # Plot 1: Category Bar & Pie Chart
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    palette = sns.color_palette("Blues_r", len(cat_counts))
    sns.barplot(x=cat_counts.values, y=cat_counts.index, hue=cat_counts.index, palette=palette, ax=axes[0], legend=False)
    axes[0].set_title("Phân bố Số lượng mẫu theo Category")
    axes[0].set_xlabel("Số lượng mẫu")
    for i, v in enumerate(cat_counts.values):
        axes[0].text(v + 100, i, f"{v:,} ({v/len(df)*100:.1f}%)", va="center", fontsize=9, weight="bold")

    axes[1].pie(
        cat_counts.values,
        labels=cat_counts.index,
        autopct="%1.1f%%",
        startangle=140,
        colors=palette,
        textprops={"fontsize": 9, "weight": "bold"},
    )
    axes[1].set_title("Tỷ lệ % các nhóm Category")
    plt.tight_layout()
    fig.savefig(plots_dir / "01_category_distribution.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    # Plot 2: Full Intent Horizontal Bar
    fig, ax = plt.subplots(figsize=(12, 11))
    intent_cat_map = df.drop_duplicates(subset=["intent"]).set_index("intent")["category"].to_dict()
    sorted_intents = intent_counts.sort_values(ascending=True)
    unique_cats = list(df["category"].unique())
    cat_colors = dict(zip(unique_cats, sns.color_palette("tab10", len(unique_cats))))
    bar_colors = [cat_colors[intent_cat_map[it]] for it in sorted_intents.index]

    y_pos = np.arange(len(sorted_intents))
    ax.barh(y_pos, sorted_intents.values, color=bar_colors, height=0.7)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(sorted_intents.index, fontsize=9)
    ax.set_xlabel("Số lượng mẫu")
    ax.set_title(f"Phân bố toàn bộ {len(sorted_intents)} Intents (Tô màu theo Category)", fontsize=13, weight="bold")
    for i, v in enumerate(sorted_intents.values):
        ax.text(v + 15, i, f"{v:,}", va="center", fontsize=8)
    handles = [plt.Rectangle((0, 0), 1, 1, color=cat_colors[cat]) for cat in unique_cats]
    ax.legend(handles, unique_cats, loc="lower right", title="Category")
    plt.tight_layout()
    fig.savefig(plots_dir / "02_intent_distribution.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    # 5. Phân tích Flags
    print(f"\n[5] PHÂN TÍCH FLAGS NGÔN NGỮ:")
    flag_combos = df["flags"].value_counts()
    all_chars = set("".join(df["flags"].dropna().unique()))
    for char in sorted(all_chars):
        c_count = df["flags"].str.contains(char, na=False).sum()
        print(f" - Flag '{char}': {c_count:,} mẫu ({c_count/len(df)*100:.1f}%)")

    fig, ax = plt.subplots(figsize=(10, 5))
    top_flags = flag_combos.head(10)
    sns.barplot(x=top_flags.values, y=top_flags.index, hue=top_flags.index, palette="viridis", ax=ax, legend=False)
    ax.set_title("Top 10 Tổ hợp Flags phổ biến nhất")
    ax.set_xlabel("Số lượng mẫu")
    for i, v in enumerate(top_flags.values):
        ax.text(v + 100, i, f"{v:,} ({v / len(df) * 100:.1f}%)", va="center", fontsize=9, weight="bold")
    plt.tight_layout()
    fig.savefig(plots_dir / "03_flags_distribution.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    # 6. Text Length Analysis
    df["inst_word_count"] = df["instruction"].astype(str).apply(lambda x: len(x.split()))
    df["resp_word_count"] = df["response"].astype(str).apply(lambda x: len(x.split()))
    df["inst_char_len"] = df["instruction"].astype(str).apply(len)
    df["resp_char_len"] = df["response"].astype(str).apply(len)

    print(f"\n[6] THỐNG KÊ ĐỘ DÀI VĂN BẢN (WORD COUNT):")
    print(f" - Instruction (Câu hỏi):  Mean = {df['inst_word_count'].mean():.1f}, Median = {df['inst_word_count'].median()}, 95th = {df['inst_word_count'].quantile(0.95):.0f}, Max = {df['inst_word_count'].max()}")
    print(f" - Response (Phản hồi):    Mean = {df['resp_word_count'].mean():.1f}, Median = {df['resp_word_count'].median()}, 95th = {df['resp_word_count'].quantile(0.95):.0f}, Max = {df['resp_word_count'].max()}")

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    sns.histplot(df["inst_word_count"], kde=True, ax=axes[0, 0], color="#1d3557", bins=25)
    axes[0, 0].set_title("Phân phối Số từ của Câu hỏi (Instruction)")
    sns.histplot(df["resp_word_count"], kde=True, ax=axes[0, 1], color="#2a9d8f", bins=35)
    axes[0, 1].set_title("Phân phối Số từ của Câu phản hồi (Response)")
    sns.boxplot(x=df["inst_word_count"], ax=axes[1, 0], color="#457b9d")
    axes[1, 0].set_title("Boxplot Số từ của Instruction")
    sns.boxplot(x=df["resp_word_count"], ax=axes[1, 1], color="#e76f51")
    axes[1, 1].set_title("Boxplot Số từ của Response")
    plt.tight_layout()
    fig.savefig(plots_dir / "04_text_length_distribution.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    # 7. Slot Placeholders
    slot_regex = r"\{\{([^}]+)\}\}"
    inst_slots = [slot for text in df["instruction"].dropna() for slot in re.findall(slot_regex, text)]
    resp_slots = [slot for text in df["response"].dropna() for slot in re.findall(slot_regex, text)]
    inst_slot_counts = Counter(inst_slots)
    resp_slot_counts = Counter(resp_slots)

    print(f"\n[7] THỰC THỂ GIỮ CHỖ (PLACEHOLDERS):")
    print(f" - Slots trong Instruction: {len(inst_slot_counts)} loại -> {inst_slot_counts.most_common(5)}")
    print(f" - Slots trong Response:    {len(resp_slot_counts)} loại -> {resp_slot_counts.most_common(5)}")

    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    top_inst_slots = pd.DataFrame(inst_slot_counts.most_common(10), columns=["Slot", "Count"])
    if len(top_inst_slots) > 0:
        sns.barplot(x="Count", y="Slot", hue="Slot", data=top_inst_slots, ax=axes[0], palette="mako", legend=False)
        axes[0].set_title("Top Slots trong Câu hỏi (Instruction)")

    top_resp_slots = pd.DataFrame(resp_slot_counts.most_common(10), columns=["Slot", "Count"])
    sns.barplot(x="Count", y="Slot", hue="Slot", data=top_resp_slots, ax=axes[1], palette="rocket", legend=False)
    axes[1].set_title("Top Slots trong Câu phản hồi (Response)")
    plt.tight_layout()
    fig.savefig(plots_dir / "05_slots_placeholders.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    # 8. Từ vựng & Bigrams
    def tokenize_clean(text):
        text_clean = re.sub(r"\{\{[^}]+\}\} ", " ", text)
        return re.findall(r"\b[a-zA-Z]{2,}\b", text_clean.lower())

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
        "now", "d", "ll", "m", "o", "re", "ve", "y", "need", "want", "like", "help", "please", 
        "would", "could", "get", "know"
    ])

    all_inst_tokens = [tok for text in df["instruction"].dropna() for tok in tokenize_clean(text)]
    filtered_words = [tok for tok in all_inst_tokens if tok not in stopwords]
    top_20_words = Counter(filtered_words).most_common(20)

    bigrams = []
    for text in df["instruction"].dropna():
        tokens = [tok for tok in tokenize_clean(text) if tok not in stopwords]
        for i in range(len(tokens) - 1):
            bigrams.append(f"{tokens[i]} {tokens[i+1]}")
    top_15_bigrams = Counter(bigrams).most_common(15)

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    top_words_df = pd.DataFrame(top_20_words, columns=["Word", "Frequency"]).sort_values("Frequency")
    axes[0].barh(top_words_df["Word"], top_words_df["Frequency"], color="#457b9d")
    axes[0].set_title("Top 20 Từ khóa trong câu hỏi khách hàng")

    top_bigrams_df = pd.DataFrame(top_15_bigrams, columns=["Bigram", "Frequency"]).sort_values("Frequency")
    axes[1].barh(top_bigrams_df["Bigram"], top_bigrams_df["Frequency"], color="#e76f51")
    axes[1].set_title("Top 15 Cụm 2 từ (Bigrams) phổ biến nhất")
    plt.tight_layout()
    fig.savefig(plots_dir / "06_top_words_bigrams.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    print(f"\n✅ ĐÃ HOÀN TẤT VÀ LƯU 6 BIỂU ĐỒ TẠI: {plots_dir.resolve()}")
    print("=" * 75)


if __name__ == "__main__":
    main()
