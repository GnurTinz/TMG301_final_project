"""
Script gộp toàn bộ các dataset đã xử lý (Banking77 và BSCS) thành 1 dataset hợp nhất.
Chức năng:
1. Đọc các file đã xử lý trong thư mục 'processed_datasets/'.
2. Chỉ trích xuất 2 trường duy nhất: 'text' và 'label' (lấy từ label_group).
3. Làm sạch nhẹ và kiểm tra chất lượng dữ liệu.
4. Xuất file kết quả hợp nhất ra 'processed_datasets/combined_dataset.csv' và 'processed_datasets/combined_dataset.json'.
"""

from pathlib import Path
import pandas as pd


def combine_processed_datasets():
    print("=" * 75)
    print(" 🚀 BẮT ĐẦU GỘP CÁC BỘ DỮ LIỆU ĐÃ XỬ LÝ (BANKING77 & BSCS)")
    print("=" * 75)

    current_dir = Path(__file__).resolve().parent
    project_root = current_dir.parent
    processed_dir = project_root / "processed_datasets"

    banking77_file = processed_dir / "banking77_processed.csv"
    bscs_file = processed_dir / "bscs_processed.csv"

    # Kiểm tra sự tồn tại của các file đầu vào
    if not banking77_file.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {banking77_file.resolve()}")
    if not bscs_file.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {bscs_file.resolve()}")

    # 1. Đọc file Banking77
    print(f"📂 Đang đọc: {banking77_file.name}")
    df_banking = pd.read_csv(banking77_file, encoding="utf-8")
    df_b77_clean = pd.DataFrame({
        "text": df_banking["text"].astype(str).str.strip(),
        "label": df_banking["label_group"].astype(str).str.strip(),
    })
    print(f" - Banking77: {len(df_b77_clean):,} dòng")

    # 2. Đọc file BSCS
    print(f"📂 Đang đọc: {bscs_file.name}")
    df_bscs = pd.read_csv(bscs_file, encoding="utf-8")
    df_bscs_clean = pd.DataFrame({
        "text": df_bscs["text"].astype(str).str.strip(),
        "label": df_bscs["label_group"].astype(str).str.strip(),
    })
    print(f" - BSCS:      {len(df_bscs_clean):,} dòng")

    # 3. Gộp 2 DataFrame thành 1
    combined_df = pd.concat([df_b77_clean, df_bscs_clean], ignore_index=True)
    total_rows = len(combined_df)
    print(f"\n✅ ĐÃ GỘP THÀNH CÔNG: {total_rows:,} dòng dữ liệu!")

    # 4. Kiểm tra chất lượng dữ liệu
    print("\n🔍 KIỂM TRA CHẤT LƯỢNG:")
    print(f" - Cột trong file mới:  {list(combined_df.columns)}")
    print(f" - Giá trị thiếu (NaN): {combined_df.isnull().sum().to_dict()}")

    # Loại bỏ dòng rỗng nếu có
    combined_df = combined_df[combined_df["text"] != ""]
    combined_df = combined_df[combined_df["label"] != ""]

    # 5. Thống kê phân bố nhãn gộp
    print("\n📊 PHÂN BỐ NHÃN TRONG TẬP DỮ LIỆU HỢP NHẤT:")
    label_counts = combined_df["label"].value_counts()
    for lbl, count in label_counts.items():
        pct = count / len(combined_df) * 100
        print(f" - {lbl:18s}: {count:6,} mẫu ({pct:5.2f}%)")

    # 6. Lưu kết quả ra file mới
    out_csv = processed_dir / "combined_dataset.csv"
    out_json = processed_dir / "combined_dataset.json"

    combined_df.to_csv(out_csv, index=False, encoding="utf-8-sig")
    combined_df.to_json(out_json, orient="records", force_ascii=False, indent=2)

    print("\n📁 FILE KẾT QUẢ ĐÃ ĐƯỢC LƯU TẠI:")
    print(f" 1. CSV:  {out_csv.resolve()} ({len(combined_df):,} dòng)")
    print(f" 2. JSON: {out_json.resolve()}")

    print("\n🔍 5 DÒNG MẪU ĐẦU TIÊN:")
    print(combined_df.head(5).to_string(index=False))

    print("\n🔍 5 DÒNG LẤY MẪU NGẪU NHIÊN:")
    print(combined_df.sample(5, random_state=42).to_string(index=False))
    print("=" * 75)


if __name__ == "__main__":
    combine_processed_datasets()
