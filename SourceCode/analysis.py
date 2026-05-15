import os
import pandas as pd

# Khởi tạo các đường dẫn truy cập đến thư mục và file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_PATH = os.path.join(BASE_DIR, 'output')
DATA_PATH = os.path.join(OUTPUT_PATH, 'data.csv')

# Tạo thư mục nếu chưa có
os.makedirs(OUTPUT_PATH, exist_ok=True)

df = pd.read_csv(DATA_PATH)

# Lọc bỏ các cột chứa chữ (định danh), tự động lấy TẤT CẢ các cột còn lại làm chỉ số tính toán
INFO_COLS = ['Player', 'Nation', 'Pos', 'Squad', 'Age', 'Born']
NUMERIC_METRICS = [col for col in df.columns if col not in INFO_COLS]

# Ép kiểu số, thay N/a -> NaN
for col in NUMERIC_METRICS:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# ----------------------------------Tính median / mean / std theo từng đội----------------------------------

group = df.groupby('Squad')[NUMERIC_METRICS]

stats_median = group.median().add_suffix('_median')
stats_mean = group.mean().add_suffix('_mean')
stats_std = group.std().add_suffix('_std')

# Ghép ba bảng lại với nhau nối theo chiều ngang với (axis = 1) và các chỉ số ở các cột lấy sau dấu phẩy 4 chữ số
stats_all = pd.concat([stats_median, stats_mean, stats_std], axis=1).round(4)

# Sắp xếp lại cột:
ordered_cols = []
for x in NUMERIC_METRICS:
    ordered_cols += [f"{x}_median", f"{x}_mean", f"{x}_std"]
stats_all = stats_all[ordered_cols]

# Ghi ra csv
csv_path = os.path.join(OUTPUT_PATH, 'team_stats.csv')
stats_all.to_csv(csv_path, encoding='utf-8')
print(f"Statistical results have been successfully saved!")

# ----------------------------------Tìm đội bóng có chỉ số điểm số cao nhất ở mỗi chỉ số----------------------------------

mean_df = group.mean().round(4)

# Loại bỏ những cột mà tất cả giá trị là NaN
mean_df_clean = mean_df.dropna(axis=1, how='all')

# Hàm idxmax trả về tên đội bóng có chỉ số lớn nhất trong cột đó
best_team_per_metric = mean_df_clean.idxmax(skipna=True)

#Hàm max trả về chỉ số
best_val_per_metric = mean_df_clean.max(skipna=True)

best_table = pd.DataFrame({
    'Metric'     : best_team_per_metric.index,
    'Best Team'          : best_team_per_metric.values,
    'Mean value'    : best_val_per_metric.values.round(4),
})

best_csv = os.path.join(OUTPUT_PATH, 'best_team_per_stat.csv')
best_table.to_csv(best_csv, index=False, encoding='utf-8-sig')
print(f"Best team per stat has been successfully saved!")

# ----------------------------------Tìm đội bóng có phong độ tốt nhất giải ngoại hạng Anh----------------------------------

FORM_POSITIVE = [
    'Performance Gls', 'Performance Ast', 'Standard SoT', 'Standard SoT%', 'Standard G/Sh',
    'Team Success PPM', 'Team Success +/-', 'Performance TklW', 'Performance Int', 'Performance Fld',
]

FORM_NEGATIVE = [
    'Performance CrdY', 'Performance CrdR', 'Performance Fls',
    'Performance OG', 'Team Success onGA',
]

# Tổng trọng số của tất cả các chỉ số nên bằng 1.0 (hoặc 100%)
WEIGHTS = {
    # Hiệu suất chung (Quan trọng nhất)
    'Team Success PPM': 0.30,
    'Team Success +/-': 0.15,
    # Tấn công
    'Performance Gls': 0.12,
    'Performance Ast': 0.08,
    'Standard SoT': 0.05,
    'Standard SoT%': 0.04,
    'Standard G/Sh': 0.04,
    'Performance Fld': 0.02,
    # Phòng ngự & Kỷ luật
    'Team Success onGA': 0.10,
    'Performance TklW': 0.04,
    'Performance Int': 0.04,
    'Performance CrdR': 0.01,
    'Performance CrdY': 0.005,
    'Performance Fls': 0.005,
    'Performance OG': 0.01,
}

# Gom nhóm và tính trung bình theo Đội bóng
grouped = df.groupby('Squad')[FORM_POSITIVE + FORM_NEGATIVE].mean()

# Chuẩn hóa Min-Max chuẩn theo từng nhóm hướng dữ liệu (Thang điểm 0 - 1)
normalized = pd.DataFrame(index=grouped.index)

# Nhóm càng cao càng tốt
for col in FORM_POSITIVE:
    min_val, max_val = grouped[col].min(), grouped[col].max()
    if max_val != min_val:
        normalized[col] = (grouped[col] - min_val) / (max_val - min_val)
    else:
        normalized[col] = 1.0

# Nhóm càng thấp càng tốt (Tự động đảo chiều điểm số không cần nhân -1 trước)
for col in FORM_NEGATIVE:
    min_val, max_val = grouped[col].min(), grouped[col].max()
    if max_val != min_val:
        normalized[col] = (max_val - grouped[col]) / (max_val - min_val)
    else:
        normalized[col] = 1.0

# Nhân điểm đã chuẩn hóa với trọng số tương ứng
for col in WEIGHTS.keys():
    normalized[col] = normalized[col] * WEIGHTS[col]

# Tính tổng điểm phong độ cuối cùng
team_ranking = normalized[list(WEIGHTS.keys())].sum(axis=1) * 100

# Xuất kết quả định dạng chuẩn
ranking = (
    team_ranking.sort_values(ascending=False)
    .round(2)
    .reset_index()
)
ranking.columns = ['Team', 'Score']
ranking.index += 1
ranking.index.name = 'Rank'

rank_csv = os.path.join(OUTPUT_PATH, 'team_form_ranking.csv')
ranking.to_csv(rank_csv, encoding='utf-8')
print(f"Ranking results have been successfully saved with optimized weights!")