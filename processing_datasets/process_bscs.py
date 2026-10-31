"""
Script xử lý bộ dữ liệu Bitext Sample Customer Support (BSCS) theo cấu trúc phân loại của processing_datasets.
Chức năng:
1. Đọc file mapping nhóm từ 'BSCS_label_group_map.json'.
2. Đọc dữ liệu BSCS (Bitext 27K samples).
3. Chỉ trích xuất cột câu hỏi (instruction -> text) và các mục phân loại (category, intent).
4. Ánh xạ sang 3 nhãn nhóm cấp cao: 'Technical Issue', 'Payment', 'Return/Refund'.
5. Xuất dữ liệu đã xử lý ra định dạng CSV và JSON trong thư mục processing_datasets.
"""

import json
from pathlib import Path
import pandas as pd


def load_label_group_map(json_path: Path) -> dict:
    """Tải và chuyển đổi file json phân nhóm thành từ điển {intent: nhóm}."""
    with open(json_path, "r", encoding="utf-8") as f:
        group_data = json.load(f)

    intent_to_group = {}
    for group, intents in group_data.items():
        for intent in intents:
            intent_to_group[intent.strip()] = group
            intent_to_group[intent.strip().lower()] = group
    return intent_to_group


def process_bscs():
    print("=" * 75)
    print(" 🚀 BẮT ĐẦU XỬ LÝ DỮ LIỆU BITEXT SAMPLE CUSTOMER SUPPORT (BSCS)")
    print("=" * 75)

    current_dir = Path(__file__).resolve().parent
    project_root = current_dir.parent

    # 1. Đường dẫn file mapping
    map_path = current_dir / "BSCS_label_group_map.json"
    if not map_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file mapping: {map_path}")

    intent_to_group = load_label_group_map(map_path)
    print(f"✅ Đã tải file mapping: {map_path.name} (Gồm {len(set(intent_to_group.values()))} nhóm)")

    # 2. Tìm kiếm file dữ liệu BSCS
    candidate_paths = [
        project_root / "datasets" / "Bitext_Sample_Customer_Support" / "Bitext_Sample_Customer_Support_Training_Dataset_27K_responses-v11.csv",
        project_root / "datasets" / "Bitext_Sample_Customer_Support_Training_Dataset_27K_responses-v11.csv",
    ]

    data_path = None
    for p in candidate_paths:
        if p.exists():
            data_path = p
            break

    if data_path is None:
        raise FileNotFoundError("Không tìm thấy file dữ liệu BSCS trong thư mục datasets/Bitext_Sample_Customer_Support!")

    print(f"📂 Đang đọc dữ liệu từ: {data_path.name}")
    df_raw = pd.read_csv(data_path, encoding="utf-8")
    print(f" - Tổng số dòng ban đầu: {len(df_raw):,} dòng x {df_raw.shape[1]} cột")

    # 3. Trích xuất chỉ các cột cần thiết: text (instruction), category, intent
    df_processed = pd.DataFrame()
    df_processed["text"] = df_raw["instruction"].astype(str).str.strip()
    df_processed["category"] = df_raw["category"].astype(str).str.strip()
    df_processed["intent"] = df_raw["intent"].astype(str).str.strip()

    # 4. Ánh xạ sang nhóm nhãn mới (label_group) dựa vào intent
    df_processed["label_group"] = df_processed["intent"].map(intent_to_group)

    # Fallback kiểm tra dạng lowercase nếu có
    unmapped_mask = df_processed["label_group"].isnull()
    if unmapped_mask.any():
        df_processed.loc[unmapped_mask, "label_group"] = (
            df_processed.loc[unmapped_mask, "intent"].str.lower().map(intent_to_group)
        )

    # Kiểm tra chất lượng ánh xạ
    missing_count = df_processed["label_group"].isnull().sum()
    if missing_count > 0:
        missing_intents = df_processed[df_processed["label_group"].isnull()]["intent"].unique()
        raise ValueError(f"❌ Phát hiện {missing_count} dòng chưa ánh xạ được! Các intent thiếu: {missing_intents}")

    print(f"✅ Ánh xạ thành công 100% mẫu ({len(df_processed):,} dòng, 0 intent bị thiếu)!")

    # 5. Thống kê phân bố nhãn nhóm
    print("\n📊 PHÂN BỐ NHÃN THEO NHÓM (LABEL GROUP DISTRIBUTION):")
    group_dist = df_processed["label_group"].value_counts()
    for grp, cnt in group_dist.items():
        pct = cnt / len(df_processed) * 100
        print(f" - {grp:18s}: {cnt:6,} mẫu ({pct:5.2f}%)")

    # 6. Lưu file kết quả vào thư mục processed_datasets
    output_dir = project_root / "processed_datasets"
    output_dir.mkdir(parents=True, exist_ok=True)

    out_csv = output_dir / "bscs_processed.csv"
    out_json = output_dir / "bscs_processed.json"

    df_processed.to_csv(out_csv, index=False, encoding="utf-8-sig")
    df_processed.to_json(out_json, orient="records", force_ascii=False, indent=2)

    print("\n📁 KẾT QUẢ ĐÃ ĐƯỢC XUẤT VÀO THƯ MỤC processed_datasets:")
    print(f" 1. CSV xử lý:    {out_csv.resolve()} ({len(df_processed):,} dòng)")
    print(f" 2. JSON xử lý:   {out_json.resolve()}")

    print("\n🔍 3 DÒNG MẪU ĐẦU TIÊN:")
    print(df_processed.head(3).to_string(index=False))
    print("=" * 75)


if __name__ == "__main__":
    process_bscs()
