"""
Script chạy phân tích EDA tự động cho bộ dữ liệu Twitter Customer Support (TWCS)
Tự động in báo cáo chi tiết ra terminal và lưu toàn bộ biểu đồ vào thư mục EDA/plots_twitter/
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
    print("=" * 80)
    print(" 🚀 BẮT ĐẦU PHÂN TÍCH EDA - TWITTER CUSTOMER SUPPORT DATASET (TWCS)")
    print("=" * 80)

    # 1. Tìm đường dẫn file dữ liệu
    candidate_paths = [
        Path("datasets/twitter/twcs/twcs.csv"),
        Path("../datasets/twitter/twcs/twcs.csv"),
        Path.cwd() / "datasets" / "twitter" / "twcs" / "twcs.csv",
        Path.cwd().parent / "datasets" / "twitter" / "twcs" / "twcs.csv",
        Path("datasets/twitter/sample.csv"),
        Path("../datasets/twitter/sample.csv"),
    ]

    file_path = None
    for p in candidate_paths:
        if p.exists():
            file_path = p
            break

    if file_path is None:
        raise FileNotFoundError(
            "Không tìm thấy file twcs.csv hoặc sample.csv trong thư mục datasets/twitter!"
        )

    # Thư mục lưu plots
    plots_dir = Path("EDA/plots_twitter")
    if not plots_dir.parent.exists():
        plots_dir = Path("plots_twitter")
    plots_dir.mkdir(parents=True, exist_ok=True)

    # Cấu hình biểu đồ
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    plt.rcParams["figure.figsize"] = (12, 6)
    plt.rcParams["font.size"] = 10

    # 2. Đọc file
    print(f"\n[1] ĐANG ĐỌC DỮ LIỆU TỪ: {file_path.resolve()}")
    
    # Kiểm tra kích thước file
    file_size_mb = file_path.stat().st_size / (1024 * 1024)
    print(f" - Dung lượng file đĩa: {file_size_mb:.2f} MB")

    # Để tối ưu bộ nhớ RAM và thời gian chạy mượt mà:
    # Nếu file lớn (twcs.csv), có thể lấy mẫu phân tích hoặc phân tích tối ưu dtypes
    # Đọc tối đa 500,000 dòng để phân tích sâu NLP, hoặc toàn bộ nếu RAM cho phép
    # Ở đây đọc tối đa 300,000 dòng đại diện nếu là file lớn, sample.csv thì đọc toàn bộ
    if file_size_mb > 50:
        print(" - File dữ liệu lớn (>50MB). Đang tải mẫu đại diện 300,000 dòng đầu để phân tích EDA chuyên sâu...")
        df = pd.read_csv(file_path, nrows=300000, encoding="utf-8")
    else:
        df = pd.read_csv(file_path, encoding="utf-8")

    n_rows, n_cols = df.shape
    mem_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)

    print(f" - Kích thước tập phân tích: {n_rows:,} dòng x {n_cols} cột")
    print(f" - Bộ nhớ RAM chiếm dụng:   {mem_mb:.2f} MB")
    print(f" - Danh sách các cột:       {list(df.columns)}")

    # 3. Kiểm tra missing & duplicates
    print(f"\n[2] KIỂM TRA CHẤT LƯỢNG DỮ LIỆU:")
    missing_dict = df.isnull().sum().to_dict()
    print(f" - Missing values trên từng cột:")
    for col, count in missing_dict.items():
        print(f"    * {col:25s}: {count:8,} missing ({count/n_rows*100:5.2f}%)")
    print(f" - Số dòng trùng lặp hoàn toàn: {df.duplicated().sum():,}")
    print(f" - Số tweet text trùng lặp:      {df.duplicated(subset=['text']).sum():,}")

    # 4. Phân tích Inbound vs Outbound
    print(f"\n[3] PHÂN BỐ CHIỀU HƯỚNG TIN NHẮN (INBOUND vs OUTBOUND):")
    inbound_counts = df["inbound"].value_counts()
    inbound_true = inbound_counts.get(True, 0)
    inbound_false = inbound_counts.get(False, 0)
    print(f" - Inbound = True  (Khách hàng gửi đến hãng): {inbound_true:,} ({inbound_true/n_rows*100:.2f}%)")
    print(f" - Inbound = False (Hãng phản hồi khách hàng): {inbound_false:,} ({inbound_false/n_rows*100:.2f}%)")

    # Plot 1: Inbound Bar & Pie Chart
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    colors = ["#2b5c8f", "#d95f02"]
    labels = ["Khách hàng (Inbound)", "Hãng hỗ trợ (Outbound)"]
    counts = [inbound_true, inbound_false]

    sns.barplot(x=labels, y=counts, palette=colors, ax=axes[0], hue=labels, legend=False)
    axes[0].set_title("Số lượng Tweet theo Chiều hướng (Inbound vs Outbound)", fontsize=12, weight="bold")
    axes[0].set_ylabel("Số lượng mẫu")
    for i, v in enumerate(counts):
        axes[0].text(i, v + (max(counts) * 0.02), f"{v:,} ({v/n_rows*100:.1f}%)", ha="center", weight="bold")

    axes[1].pie(
        counts,
        labels=labels,
        autopct="%1.1f%%",
        startangle=140,
        colors=colors,
        explode=(0.04, 0),
        textprops={"fontsize": 11, "weight": "bold"},
    )
    axes[1].set_title("Tỷ lệ % Chiều hướng Hội thoại", fontsize=12, weight="bold")
    plt.tight_layout()
    fig.savefig(plots_dir / "01_inbound_distribution.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    # 5. Phân tích Top Thương hiệu Chăm sóc Khách hàng (author_id khi inbound=False)
    print(f"\n[4] TOP THƯƠNG HIỆU HỖ TRỢ KHÁCH HÀNG (OUTBOUND):")
    brand_df = df[df["inbound"] == False]
    top_brands = brand_df["author_id"].value_counts().head(15)
    print(f" - Số lượng thương hiệu phản hồi độc nhất: {brand_df['author_id'].nunique():,}")
    for rank, (brand, cnt) in enumerate(top_brands.head(10).items(), 1):
        print(f"   {rank:2d}. {brand:20s}: {cnt:7,} phản hồi ({cnt/len(brand_df)*100:.2f}%)")

    # Plot 2: Top Brands Bar Chart
    fig, ax = plt.subplots(figsize=(13, 7))
    palette = sns.color_palette("mako", len(top_brands))
    sns.barplot(x=top_brands.values, y=top_brands.index, palette=palette, ax=ax, hue=top_brands.index, legend=False)
    ax.set_title("Top 15 Thương hiệu có số lượng phản hồi hỗ trợ nhiều nhất trên Twitter", fontsize=13, weight="bold")
    ax.set_xlabel("Số lượng phản hồi (Tweets)")
    ax.set_ylabel("Tên tài khoản Hỗ trợ (Brand Handle)")
    for i, v in enumerate(top_brands.values):
        ax.text(v + (max(top_brands.values) * 0.01), i, f"{v:,}", va="center", fontsize=9, weight="bold")
    plt.tight_layout()
    fig.savefig(plots_dir / "02_top_support_brands.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    # 6. Phân tích Độ dài Văn bản (Text Length Analysis)
    print(f"\n[5] PHÂN TÍCH ĐẶC TRƯNG ĐỘ DÀI VĂN BẢN (TEXT LENGTH):")
    df["char_len"] = df["text"].astype(str).apply(len)
    df["word_count"] = df["text"].astype(str).apply(lambda x: len(x.split()))

    cust_words = df[df["inbound"] == True]["word_count"]
    brand_words = df[df["inbound"] == False]["word_count"]

    print(f" - Khách hàng (Inbound):  Mean = {cust_words.mean():.1f} từ, Median = {cust_words.median():.0f}, 95th = {cust_words.quantile(0.95):.0f}, Max = {cust_words.max()} từ")
    print(f" - Hãng hỗ trợ (Outbound): Mean = {brand_words.mean():.1f} từ, Median = {brand_words.median():.0f}, 95th = {brand_words.quantile(0.95):.0f}, Max = {brand_words.max()} từ")

    # Plot 3: Text Length Distribution
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    sns.histplot(cust_words, bins=35, kde=True, ax=axes[0, 0], color="#2b5c8f")
    axes[0, 0].set_title("Phân bố số từ của Khách hàng (Inbound)", fontsize=11, weight="bold")
    axes[0, 0].set_xlabel("Số từ (Word count)")

    sns.histplot(brand_words, bins=35, kde=True, ax=axes[0, 1], color="#d95f02")
    axes[0, 1].set_title("Phân bố số từ của Hãng hỗ trợ (Outbound)", fontsize=11, weight="bold")
    axes[0, 1].set_xlabel("Số từ (Word count)")

    sns.boxplot(x=cust_words, ax=axes[1, 0], color="#5b8bb8")
    axes[1, 0].set_title("Boxplot số từ của Khách hàng", fontsize=11, weight="bold")
    axes[1, 0].set_xlabel("Số từ")

    sns.boxplot(x=brand_words, ax=axes[1, 1], color="#e88c5d")
    axes[1, 1].set_title("Boxplot số từ của Hãng hỗ trợ", fontsize=11, weight="bold")
    axes[1, 1].set_xlabel("Số từ")

    plt.tight_layout()
    fig.savefig(plots_dir / "03_text_length_distribution.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    # 7. Phân tích Thực thể đặc thù Twitter (Mentions, URLs, Hashtags, Emojis)
    print(f"\n[6] PHÂN TÍCH THỰC THỂ ĐẶC TRÙ TRÊN TWITTER:")
    mention_pattern = re.compile(r"@\w+")
    url_pattern = re.compile(r"https?://\S+|t\.co/\S+")
    hashtag_pattern = re.compile(r"#\w+")

    df["mention_count"] = df["text"].astype(str).apply(lambda x: len(mention_pattern.findall(x)))
    df["url_count"] = df["text"].astype(str).apply(lambda x: len(url_pattern.findall(x)))
    df["hashtag_count"] = df["text"].astype(str).apply(lambda x: len(hashtag_pattern.findall(x)))

    pct_mentions = (df["mention_count"] > 0).mean() * 100
    pct_urls = (df["url_count"] > 0).mean() * 100
    pct_hashtags = (df["hashtag_count"] > 0).mean() * 100

    print(f" - Tỷ lệ tweet chứa @mention: {pct_mentions:.1f}%")
    print(f" - Tỷ lệ tweet chứa Link URL: {pct_urls:.1f}%")
    print(f" - Tỷ lệ tweet chứa #hashtag: {pct_hashtags:.1f}%")

    # Plot 4: Entity Frequency
    entity_stats = pd.DataFrame({
        "Thực thể": ["Chứa @mention", "Chứa URL / Link", "Chứa #hashtag"],
        "Tỷ lệ (%)": [pct_mentions, pct_urls, pct_hashtags],
        "Số lượng mẫu": [
            (df["mention_count"] > 0).sum(),
            (df["url_count"] > 0).sum(),
            (df["hashtag_count"] > 0).sum(),
        ]
    })

    fig, ax = plt.subplots(figsize=(10, 5))
    palette = ["#1f77b4", "#2ca02c", "#ff7f0e"]
    sns.barplot(x="Tỷ lệ (%)", y="Thực thể", data=entity_stats, palette=palette, ax=ax, hue="Thực thể", legend=False)
    ax.set_title("Tỷ lệ xuất hiện của các thực thể mạng xã hội trong dữ liệu", fontsize=12, weight="bold")
    ax.set_xlim(0, 100)
    for i, row in entity_stats.iterrows():
        ax.text(row["Tỷ lệ (%)"] + 1.5, i, f"{row['Tỷ lệ (%)']:.1f}% ({row['Số lượng mẫu']:,} mẫu)", va="center", weight="bold")
    plt.tight_layout()
    fig.savefig(plots_dir / "04_twitter_entities.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    # 8. Phân tích Từ vựng & Bigrams (Keywords & N-grams)
    print(f"\n[7] PHÂN TÍCH TỪ VỰNG & N-GRAMS (SO SÁNH KHÁCH HÀNG VS HÃNG):")

    def clean_tokens(text):
        # Bỏ url và mention
        t = re.sub(r"https?://\S+|@\w+", " ", text.lower())
        tokens = re.findall(r"\b[a-z]{2,}\b", t)
        return [tok for tok in tokens if tok not in stopwords and len(tok) > 2]

    stopwords = set([
        "the", "and", "to", "of", "in", "for", "is", "on", "that", "this", "it", "you", "your",
        "with", "we", "can", "have", "are", "be", "at", "as", "from", "my", "me", "our", "us",
        "do", "not", "so", "if", "but", "about", "what", "there", "an", "they", "will", "all",
        "just", "up", "out", "been", "has", "more", "when", "how", "any", "get", "no", "re",
        "by", "would", "like", "one", "co", "http", "https"
    ])

    # Lấy mẫu nhỏ hơn để chạy n-gram cực nhanh
    sample_nlp = df.sample(min(30000, len(df)), random_state=42)
    cust_texts = sample_nlp[sample_nlp["inbound"] == True]["text"].dropna()
    brand_texts = sample_nlp[sample_nlp["inbound"] == False]["text"].dropna()

    cust_words_list = [w for t in cust_texts for w in clean_tokens(t)]
    brand_words_list = [w for t in brand_texts for w in clean_tokens(t)]

    top_cust_words = Counter(cust_words_list).most_common(15)
    top_brand_words = Counter(brand_words_list).most_common(15)

    def extract_bigrams(texts):
        bgs = []
        for t in texts:
            toks = clean_tokens(t)
            for i in range(len(toks) - 1):
                bgs.append(f"{toks[i]} {toks[i+1]}")
        return Counter(bgs).most_common(15)

    top_cust_bigrams = extract_bigrams(cust_texts)
    top_brand_bigrams = extract_bigrams(brand_texts)

    # Plot 5: Keywords Comparison
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    df_cw = pd.DataFrame(top_cust_words, columns=["Word", "Count"]).sort_values("Count")
    axes[0, 0].barh(df_cw["Word"], df_cw["Count"], color="#2b5c8f")
    axes[0, 0].set_title("Top 15 Từ khóa phổ biến của Khách hàng (Inbound)", weight="bold")

    df_bw = pd.DataFrame(top_brand_words, columns=["Word", "Count"]).sort_values("Count")
    axes[0, 1].barh(df_bw["Word"], df_bw["Count"], color="#d95f02")
    axes[0, 1].set_title("Top 15 Từ khóa phản hồi của Thương hiệu (Outbound)", weight="bold")

    df_cb = pd.DataFrame(top_cust_bigrams, columns=["Bigram", "Count"]).sort_values("Count")
    axes[1, 0].barh(df_cb["Bigram"], df_cb["Count"], color="#5b8bb8")
    axes[1, 0].set_title("Top 15 Cụm 2 từ (Bigrams) từ Khách hàng", weight="bold")

    df_bb = pd.DataFrame(top_brand_bigrams, columns=["Bigram", "Count"]).sort_values("Count")
    axes[1, 1].barh(df_bb["Bigram"], df_bb["Count"], color="#e88c5d")
    axes[1, 1].set_title("Top 15 Cụm 2 từ (Bigrams) từ Phản hồi Thương hiệu", weight="bold")

    plt.tight_layout()
    fig.savefig(plots_dir / "05_keywords_bigrams_comparison.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    # 9. Phân tích Chuỗi thời gian (Temporal Trends)
    print(f"\n[8] PHÂN TÍCH CHUỖI THỜI GIAN (TEMPORAL PATTERNS):")
    try:
        # Chuyển đổi định dạng thời gian của Twitter
        df["dt"] = pd.to_datetime(df["created_at"], errors="coerce")
        valid_dt = df["dt"].dropna()
        if len(valid_dt) > 0:
            df["hour"] = valid_dt.dt.hour
            df["day_name"] = valid_dt.dt.day_name()

            day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            day_counts = df["day_name"].value_counts().reindex(day_order).fillna(0)
            hour_counts = df["hour"].value_counts().sort_index()

            # Plot 6: Temporal Trends
            fig, axes = plt.subplots(1, 2, figsize=(15, 5))
            sns.barplot(x=hour_counts.index, y=hour_counts.values, ax=axes[0], color="#2b5c8f")
            axes[0].set_title("Số lượng Tweet theo Khung giờ trong ngày (0 - 23h)", weight="bold")
            axes[0].set_xlabel("Giờ trong ngày (UTC)")
            axes[0].set_ylabel("Số lượng Tweet")

            sns.barplot(x=day_counts.index, y=day_counts.values, ax=axes[1], color="#457b9d")
            axes[1].set_title("Số lượng Tweet theo Ngày trong tuần", weight="bold")
            axes[1].set_xlabel("Ngày trong tuần")
            axes[1].tick_params(axis='x', rotation=30)
            axes[1].set_ylabel("Số lượng Tweet")

            plt.tight_layout()
            fig.savefig(plots_dir / "06_temporal_trends.png", dpi=200, bbox_inches="tight")
            plt.close(fig)
            print(f" - Khung giờ cao điểm nhất: {hour_counts.idxmax()}h ({hour_counts.max():,} tweets)")
            print(f" - Ngày trong tuần sôi động nhất: {day_counts.idxmax()} ({int(day_counts.max()):,} tweets)")
    except Exception as e:
        print(f" - Bỏ qua chi tiết temporal do parse date: {e}")

    print(f"\n✅ HOÀN TẤT PHÂN TÍCH EDA TWITTER! TOÀN BỘ 6 BIỂU ĐỒ ĐÃ LƯU TẠI: {plots_dir.resolve()}")
    print("=" * 80)


if __name__ == "__main__":
    main()
