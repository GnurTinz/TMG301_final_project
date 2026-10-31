from pathlib import Path
import pandas as pd

# Tạo thư mục lưu dữ liệu
output_dir = Path("datasets/banking77")
output_dir.mkdir(parents=True, exist_ok=True)

# Hai file CSV gốc của BANKING77
train_url = (
    "https://raw.githubusercontent.com/PolyAI-LDN/"
    "task-specific-datasets/master/banking_data/train.csv"
)

test_url = (
    "https://raw.githubusercontent.com/PolyAI-LDN/"
    "task-specific-datasets/master/banking_data/test.csv"
)

# Đọc trực tiếp từ GitHub
train_df = pd.read_csv(train_url)
test_df = pd.read_csv(test_url)

# Lưu vào thư mục dự án
train_path = output_dir / "banking77_train.csv"
test_path = output_dir / "banking77_test.csv"

train_df.to_csv(train_path, index=False, encoding="utf-8-sig")
test_df.to_csv(test_path, index=False, encoding="utf-8-sig")

# Kiểm tra
print(f"Train: {train_df.shape[0]} mẫu")
print(f"Test:  {test_df.shape[0]} mẫu")
print("\n5 dòng đầu của train:")
print(train_df.head())

print(f"\nĐã lưu train tại: {train_path.resolve()}")
print(f"Đã lưu test tại:  {test_path.resolve()}")