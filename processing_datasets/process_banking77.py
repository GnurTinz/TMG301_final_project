"""
Script xử lý bộ dữ liệu Banking77 theo cấu trúc phân loại của processing_datasets.
Chức năng:
1. Đọc file mapping nhóm từ 'banking77_label_group_map.json'.
2. Đọc dữ liệu Banking77 (Train và Test).
3. Chỉ trích xuất cột văn bản (text) và mục phân loại gốc (category).
4. Ánh xạ sang 3 nhãn nhóm cấp cao: 'Technical Issue', 'Payment', 'Return/Refund'.
5. Xuất dữ liệu đã xử lý ra định dạng CSV và JSON trong thư mục processing_datasets.
"""

import json
from pathlib import Path
import pandas as pd


def load_label_group_map(json_path: Path) -> dict:
    """Tải và chuyển đổi file json phân nhóm thành từ điển {nhãn_gốc: nhóm}."""
    with open(json_path, "r", encoding="utf-8") as f:
        group_data = json.load(f)

    label_to_group = {}
    for group, labels in group_data.items():
        for label in labels:
            label_to_group[label.strip()] = group
            # Thêm hỗ trợ lowercase để tránh lệch chữ hoa/thường
            label_to_group[label.strip().lower()] = group
    return label_to_group


def process_banking77():
    print("=" * 75)
    print(" 🚀 BẮT ĐẦU XỬ LÝ DỮ LIỆU BANKING77")
    print("=" * 75)

    current_dir = Path(__file__).resolve().parent
    project_root = current_dir.parent

    # 1. Đường dẫn file mapping
    map_path = current_dir / "banking77_label_group_map.json"
    if not map_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file mapping: {map_path}")

    label_to_group = load_label_group_map(map_path)
    print(f"✅ Đã tải file mapping: {map_path.name} (Gồm {len(set(label_to_group.values()))} nhóm)")

    # 2. Tìm kiếm file train và test
    data_dir = project_root / "datasets" / "banking77"
    train_path = data_dir / "banking77_train.csv"
    test_path = data_dir / "banking77_test.csv"

    if not train_path.exists() or not test_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file dữ liệu Banking77 tại: {data_dir}")

    # Đọc dữ liệu
    print(f"📂 Đang đọc dữ liệu Train từ: {train_path.name}")
    train_df = pd.read_csv(train_path, encoding="utf-8")
    print(f"📂 Đang đọc dữ liệu Test từ:  {test_path.name}")
    test_df = pd.read_csv(test_path, encoding="utf-8")

    # 3. Trích xuất chỉ các cột cần thiết: text và category
    train_df = train_df[["text", "category"]].copy()
    test_df = test_df[["text", "category"]].copy()

    train_df["split"] = "train"
    test_df["split"] = "test"

    combined_df = pd.concat([train_df, test_df], ignore_index=True)

    # Làm sạch nhẹ text và category
    combined_df["text"] = combined_df["text"].astype(str).str.strip()
    combined_df["category"] = combined_df["category"].astype(str).str.strip()

    # 4. Ánh xạ sang nhóm nhãn mới (label_group)
    combined_df["label_group"] = combined_df["category"].map(label_to_group)

    # Fallback kiểm tra dạng lowercase nếu có nhãn bị lệch case
    unmapped_mask = combined_df["label_group"].isnull()
    if unmapped_mask.any():
        combined_df.loc[unmapped_mask, "label_group"] = (
            combined_df.loc[unmapped_mask, "category"].str.lower().map(label_to_group)
        )

    # Kiểm tra chất lượng ánh xạ
    missing_count = combined_df["label_group"].isnull().sum()
    if missing_count > 0:
        missing_cats = combined_df[combined_df["label_group"].isnull()]["category"].unique()
        raise ValueError(f"❌ Phát hiện {missing_count} dòng chưa ánh xạ được! Các nhãn thiếu: {missing_cats}")

    print(f"✅ Ánh xạ thành công 100% mẫu ({len(combined_df):,} dòng, 0 nhãn bị thiếu)!")

    # 5. Thống kê phân bố nhãn nhóm
    print("\n📊 PHÂN BỐ NHÃN THEO NHÓM (LABEL GROUP DISTRIBUTION):")
    group_dist = combined_df["label_group"].value_counts()
    for grp, cnt in group_dist.items():
        pct = cnt / len(combined_df) * 100
        print(f" - {grp:18s}: {cnt:6,} mẫu ({pct:5.2f}%)")

    # Chỉ giữ lại đúng các trường yêu cầu: text, category, label_group, (kèm split để tiện huấn luyện)
    output_cols = ["text", "category", "label_group", "split"]
    final_df = combined_df[output_cols]

    # 6. Lưu file kết quả vào thư mục processed_datasets
    output_dir = project_root / "processed_datasets"
    output_dir.mkdir(parents=True, exist_ok=True)

    # File gộp toàn bộ
    out_csv = output_dir / "banking77_processed.csv"
    out_json = output_dir / "banking77_processed.json"

    # File chia theo Train / Test
    out_train_csv = output_dir / "banking77_train_processed.csv"
    out_test_csv = output_dir / "banking77_test_processed.csv"

    final_df.to_csv(out_csv, index=False, encoding="utf-8-sig")
    final_df.to_json(out_json, orient="records", force_ascii=False, indent=2)

    final_df[final_df["split"] == "train"][["text", "category", "label_group"]].to_csv(
        out_train_csv, index=False, encoding="utf-8-sig"
    )
    final_df[final_df["split"] == "test"][["text", "category", "label_group"]].to_csv(
        out_test_csv, index=False, encoding="utf-8-sig"
    )

    print("\n📁 KẾT QUẢ ĐÃ ĐƯỢC XUẤT VÀO THƯ MỤC processed_datasets:")
    print(f" 1. CSV gộp toàn bộ:    {out_csv.resolve()} ({len(final_df):,} dòng)")
    print(f" 2. JSON gộp toàn bộ:   {out_json.resolve()}")
    print(f" 3. CSV tập Train:      {out_train_csv.resolve()} ({len(train_df):,} dòng)")
    print(f" 4. CSV tập Test:       {out_test_csv.resolve()} ({len(test_df):,} dòng)")

    print("\n🔍 3 DÒNG MẪU ĐẦU TIÊN:")
    print(final_df[["text", "category", "label_group"]].head(3).to_string(index=False))
    print("=" * 75)


if __name__ == "__main__":
    process_banking77()
