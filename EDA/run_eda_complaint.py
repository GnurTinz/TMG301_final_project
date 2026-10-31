"""
Script chạy phân tích EDA tự động cho bộ dữ liệu Consumer Financial Complaint Database
Tự động in báo cáo chi tiết ra terminal và lưu toàn bộ biểu đồ vào thư mục EDA/plots_complaint/
Hỗ trợ cơ chế đọc an toàn cho file dung lượng lớn (~5.5 GB)
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
    print(" 🚀 BẮT ĐẦU PHÂN TÍCH EDA - CONSUMER FINANCIAL COMPLAINT DATABASE (CFPB)")
    print("=" * 80)

    # 1. Tìm đường dẫn file dữ liệu
    candidate_paths = [
        Path("datasets/consumer_complaint_database/complaints.csv"),
        Path("../datasets/consumer_complaint_database/complaints.csv"),
        Path.cwd() / "datasets" / "consumer_complaint_database" / "complaints.csv",
        Path.cwd().parent / "datasets" / "consumer_complaint_database" / "complaints.csv",
    ]

    file_path = None
    for p in candidate_paths:
        if p.exists():
            file_path = p
            break

    if file_path is None:
        raise FileNotFoundError(
            "Không tìm thấy file complaints.csv trong thư mục datasets/consumer_complaint_database/!"
        )

    # Thư mục lưu plots
    plots_dir = Path("EDA/plots_complaint")
    if not plots_dir.parent.exists():
        plots_dir = Path("plots_complaint")
    plots_dir.mkdir(parents=True, exist_ok=True)

    # Cấu hình biểu đồ
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    plt.rcParams["figure.figsize"] = (12, 6)
    plt.rcParams["font.size"] = 10

    # 2. Đọc file
    file_size_gb = file_path.stat().st_size / (1024 ** 3)
    print(f"\n[1] ĐANG ĐỌC DỮ LIỆU TỪ: {file_path.resolve()}")
    print(f" - Dung lượng file đĩa: {file_size_gb:.2f} GB")

    # Lưu ý: complaints.csv có dung lượng ~5.5GB (>18 triệu dòng).
    # Để đảm bảo chạy mượt mà không tràn bộ nhớ RAM (OOM), ta lấy mẫu đại diện 250,000 dòng.
    # Người dùng có thể nâng SAMPLE_ROWS lên tùy thuộc dung lượng RAM của máy.
    SAMPLE_ROWS = 250000
    print(f" - Áp dụng cơ chế lấy mẫu an toàn: {SAMPLE_ROWS:,} dòng đầu đại diện...")

    use_cols = [
        "Date received", "Product", "Sub-product", "Issue", "Sub-issue",
        "Company public response", "Company", "State", "ZIP code", "Tags",
        "Submitted via", "Date sent to company", "Company response to consumer",
        "Timely response?", "Complaint ID"
    ]

    df = pd.read_csv(
        file_path,
        nrows=SAMPLE_ROWS,
        usecols=use_cols,
        low_memory=False,
        encoding="utf-8"
    )

    n_rows, n_cols = df.shape
    mem_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)

    print(f" - Kích thước tập phân tích: {n_rows:,} dòng x {n_cols} cột")
    print(f" - Bộ nhớ RAM chiếm dụng:   {mem_mb:.2f} MB")
    print(f" - Danh sách các cột:       {list(df.columns)}")

    # 3. Kiểm tra missing & duplicates
    print(f"\n[2] KIỂM TRA CHẤT LƯỢNG DỮ LIỆU & MISSING VALUES:")
    missing_dict = df.isnull().sum().to_dict()
    for col, count in missing_dict.items():
        print(f"    * {col:30s}: {count:8,} missing ({count/n_rows*100:5.2f}%)")
    print(f" - Số dòng trùng lặp hoàn toàn:     {df.duplicated().sum():,}")
    print(f" - Số Complaint ID trùng lặp:       {df.duplicated(subset=['Complaint ID']).sum():,}")

    # 4. Phân bố Nhóm Sản phẩm tài chính (Product)
    print(f"\n[3] PHÂN BỐ SẢN PHẨM TÀI CHÍNH (PRODUCT DISTRIBUTION):")
    product_counts = df["Product"].value_counts()
    print(f" - Số lượng nhóm sản phẩm độc nhất: {len(product_counts)}")
    for rank, (prod, cnt) in enumerate(product_counts.head(10).items(), 1):
        print(f"   {rank:2d}. {prod:50s}: {cnt:7,} ({cnt/n_rows*100:5.2f}%)")

    # Plot 1: Product Distribution
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    palette = sns.color_palette("Blues_r", len(product_counts.head(10)))
    top_products = product_counts.head(10)

    sns.barplot(x=top_products.values, y=top_products.index, palette=palette, ax=axes[0], hue=top_products.index, legend=False)
    axes[0].set_title("Top 10 Sản phẩm tài chính bị khiếu nại nhiều nhất", weight="bold")
    axes[0].set_xlabel("Số lượng khiếu nại")
    for i, v in enumerate(top_products.values):
        axes[0].text(v + (max(top_products.values) * 0.01), i, f"{v:,} ({v/n_rows*100:.1f}%)", va="center", weight="bold", fontsize=9)

    # Donut chart cho top 5 và nhóm khác
    top_5_prod = product_counts.head(5).copy()
    other_cnt = product_counts.iloc[5:].sum()
    if other_cnt > 0:
        top_5_prod["Other Products"] = other_cnt

    axes[1].pie(
        top_5_prod.values,
        labels=[p if len(p) < 30 else p[:27] + "..." for p in top_5_prod.index],
        autopct="%1.1f%%",
        startangle=140,
        colors=sns.color_palette("pastel", len(top_5_prod)),
        pctdistance=0.8,
        wedgeprops=dict(width=0.4, edgecolor='w')
    )
    axes[1].set_title("Tỷ lệ % Các nhóm sản phẩm chính", weight="bold")
    plt.tight_layout()
    fig.savefig(plots_dir / "01_product_distribution.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    # 5. Phân tích Sub-product
    print(f"\n[4] TOP SUB-PRODUCTS CHI TIẾT:")
    subprod_counts = df["Sub-product"].dropna().value_counts().head(12)
    print(f" - Số lượng Sub-products độc nhất: {df['Sub-product'].nunique()}")

    fig, ax = plt.subplots(figsize=(13, 6))
    sns.barplot(x=subprod_counts.values, y=subprod_counts.index, palette="viridis", ax=ax, hue=subprod_counts.index, legend=False)
    ax.set_title("Top 12 Sản phẩm con (Sub-products) có nhiều khiếu nại nhất", weight="bold")
    ax.set_xlabel("Số lượng khiếu nại")
    for i, v in enumerate(subprod_counts.values):
        ax.text(v + (max(subprod_counts.values) * 0.01), i, f"{v:,}", va="center", weight="bold", fontsize=9)
    plt.tight_layout()
    fig.savefig(plots_dir / "02_top_subproducts.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    # 6. Phân tích Vấn đề khiếu nại (Issue)
    print(f"\n[5] TOP VẤN ĐỀ (ISSUE) PHÁT SINH KHIẾU NẠI:")
    issue_counts = df["Issue"].value_counts().head(12)
    print(f" - Số lượng Issue độc nhất: {df['Issue'].nunique()}")
    for rank, (issue, cnt) in enumerate(issue_counts.head(8).items(), 1):
        print(f"   {rank:2d}. {issue[:55]:55s}: {cnt:7,} ({cnt/n_rows*100:5.2f}%)")

    fig, ax = plt.subplots(figsize=(14, 7))
    sns.barplot(x=issue_counts.values, y=issue_counts.index, palette="mako", ax=ax, hue=issue_counts.index, legend=False)
    ax.set_title("Top 12 Vấn đề (Issues) người tiêu dùng khiếu nại phổ biến nhất", weight="bold")
    ax.set_xlabel("Số lượng khiếu nại")
    for i, v in enumerate(issue_counts.values):
        ax.text(v + (max(issue_counts.values) * 0.01), i, f"{v:,}", va="center", weight="bold", fontsize=9)
    plt.tight_layout()
    fig.savefig(plots_dir / "03_top_issues.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    # 7. Top Tổ chức tài chính bị khiếu nại (Company)
    print(f"\n[6] TOP TỔ CHỨC TÀI CHÍNH / NGÂN HÀNG BỊ KHIẾU NẠI:")
    company_counts = df["Company"].value_counts().head(15)
    print(f" - Số lượng công ty/tổ chức độc nhất: {df['Company'].nunique():,}")
    top_3_pct = company_counts.head(3).sum() / n_rows * 100
    print(f" - Tỷ lệ tập trung khiếu nại ở Top 3 công ty: {top_3_pct:.2f}% (Chủ yếu là các cơ quan báo cáo tín dụng lớn)")

    fig, ax = plt.subplots(figsize=(14, 7))
    sns.barplot(x=company_counts.values, y=company_counts.index, palette="flare", ax=ax, hue=company_counts.index, legend=False)
    ax.set_title("Top 15 Tổ chức Tài chính & Ngân hàng nhận nhiều khiếu nại nhất", weight="bold")
    ax.set_xlabel("Số lượng khiếu nại")
    for i, v in enumerate(company_counts.values):
        ax.text(v + (max(company_counts.values) * 0.01), i, f"{v:,} ({v/n_rows*100:.1f}%)", va="center", weight="bold", fontsize=9)
    plt.tight_layout()
    fig.savefig(plots_dir / "04_top_companies.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    # 8. Kênh tiếp nhận (Submitted via) & Tỷ lệ phản hồi đúng hạn (Timely response?)
    print(f"\n[7] KÊNH TIẾP NHẬN & TỶ LỆ ĐÚNG HẠN:")
    submit_counts = df["Submitted via"].value_counts()
    timely_counts = df["Timely response?"].value_counts()
    print(f" - Kênh tiếp nhận: {submit_counts.to_dict()}")
    print(f" - Phản hồi đúng hạn: {timely_counts.to_dict()}")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    sns.barplot(x=submit_counts.index, y=submit_counts.values, palette="crest", ax=axes[0], hue=submit_counts.index, legend=False)
    axes[0].set_title("Phân bố Kênh tiếp nhận khiếu nại (Submitted via)", weight="bold")
    axes[0].set_ylabel("Số lượng mẫu")
    for i, v in enumerate(submit_counts.values):
        axes[0].text(i, v + (max(submit_counts.values) * 0.01), f"{v/n_rows*100:.1f}%", ha="center", weight="bold")

    axes[1].pie(
        timely_counts.values,
        labels=timely_counts.index,
        autopct="%1.2f%%",
        startangle=140,
        colors=["#2a9d8f", "#e76f51"],
        explode=(0.1, 0) if len(timely_counts) > 1 else None,
        textprops={"fontsize": 11, "weight": "bold"}
    )
    axes[1].set_title("Tỷ lệ phản hồi đúng hạn (Timely Response?)", weight="bold")
    plt.tight_layout()
    fig.savefig(plots_dir / "05_submission_and_timeliness.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    # 9. Kết quả phản hồi của Doanh nghiệp (Company response to consumer)
    print(f"\n[8] KẾT QUẢ PHẢN HỒI CỦA DOANH NGHIỆP:")
    resp_counts = df["Company response to consumer"].value_counts()
    for resp, cnt in resp_counts.items():
        print(f" - {resp:35s}: {cnt:7,} ({cnt/n_rows*100:.2f}%)")

    fig, ax = plt.subplots(figsize=(12, 5))
    sns.barplot(x=resp_counts.values, y=resp_counts.index, palette="Spectral", ax=ax, hue=resp_counts.index, legend=False)
    ax.set_title("Phân bố kết quả xử lý khiếu nại của tổ chức (Company response)", weight="bold")
    ax.set_xlabel("Số lượng khiếu nại")
    for i, v in enumerate(resp_counts.values):
        ax.text(v + (max(resp_counts.values) * 0.01), i, f"{v:,} ({v/n_rows*100:.1f}%)", va="center", weight="bold")
    plt.tight_layout()
    fig.savefig(plots_dir / "06_company_responses.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    # 10. Phân bố Địa lý theo Bang (State)
    print(f"\n[9] PHÂN BỐ ĐỊA LÝ THEO BANG (STATE):")
    state_counts = df["State"].dropna().value_counts().head(15)

    fig, ax = plt.subplots(figsize=(13, 6))
    sns.barplot(x=state_counts.index, y=state_counts.values, palette="mako", ax=ax, hue=state_counts.index, legend=False)
    ax.set_title("Top 15 Bang có số lượng khiếu nại tài chính cao nhất tại Hoa Kỳ", weight="bold")
    ax.set_ylabel("Số lượng khiếu nại")
    ax.set_xlabel("Bang (State)")
    for i, v in enumerate(state_counts.values):
        ax.text(i, v + (max(state_counts.values) * 0.01), f"{v:,}", ha="center", fontsize=8, weight="bold")
    plt.tight_layout()
    fig.savefig(plots_dir / "07_geographic_distribution.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    # 11. Phân tích Văn bản mô tả Vấn đề (Issue Text Length & Vocabulary)
    print(f"\n[10] PHÂN TÍCH ĐẶC TRƯNG VĂN BẢN (ISSUE DESCRIPTION TEXT LENGTH):")
    df["issue_word_count"] = df["Issue"].astype(str).apply(lambda x: len(x.split()))
    df["issue_char_len"] = df["Issue"].astype(str).apply(len)

    print(f" - Độ dài từ Issue: Mean = {df['issue_word_count'].mean():.1f}, Median = {df['issue_word_count'].median():.0f}, Max = {df['issue_word_count'].max()}")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    sns.histplot(df["issue_word_count"], bins=20, kde=True, ax=axes[0], color="#2b5c8f")
    axes[0].set_title("Phân bố số từ của Mô tả vấn đề (Issue)", weight="bold")
    axes[0].set_xlabel("Số lượng từ")

    sns.boxplot(x=df["issue_word_count"], ax=axes[1], color="#457b9d")
    axes[1].set_title("Boxplot số từ của Issue", weight="bold")
    axes[1].set_xlabel("Số lượng từ")

    plt.tight_layout()
    fig.savefig(plots_dir / "08_issue_text_length.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    print(f"\n✅ HOÀN TẤT PHÂN TÍCH EDA COMPLAINT DATABASE! TOÀN BỘ 8 BIỂU ĐỒ ĐÃ LƯU TẠI: {plots_dir.resolve()}")
    print("=" * 80)


if __name__ == "__main__":
    main()
