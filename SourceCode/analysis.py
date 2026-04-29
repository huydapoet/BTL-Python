import os
import pandas as pd

# Đường dẫn thư mục Project ( BTL-Python)
BASE_DIR = os.path.join(os.path.dirname(__file__),'..')

# Đường dẫn vào file data.csv
DATA_PATH = os.path.join(BASE_DIR, 'data.csv')

# Đường dẫn vào thư mục output trong Project
OUTPUT_PATH = os.path.join(BASE_DIR, 'output')

# Tạo thư mục nếu chưa có
os.makedirs(OUTPUT_PATH, exist_ok=True)

df = pd.read_csv(DATA_PATH)

# Chọn các chỉ số liên quan đến phong độ cầu thủ
NUMERIC_METRICS = [
    # Chơi
    "Playing Time MP", "Playing Time Starts", "Playing Time Min", "Playing Time 90s",
    # Hiệu suất tấn công
    "Performance Gls", "Performance Ast", "Performance G+A",
    "Performance G-PK", "Performance PK", "Performance PKatt",
    "Performance CrdY", "Performance CrdR",
    # Per 90
    "Per 90 Minutes Gls", "Per 90 Minutes Ast", "Per 90 Minutes G+A",
    "Per 90 Minutes G-PK", "Per 90 Minutes G+A-PK",
    # Sút
    "Standard Sh", "Standard SoT", "Standard SoT%",
    "Standard Sh/90", "Standard SoT/90", "Standard G/Sh", "Standard G/SoT",
    # Đội bóng (hiệu suất nhóm khi cầu thủ trên sân)
    "Team Success PPM", "Team Success onG", "Team Success onGA",
    "Team Success +/-", "Team Success +/-90", "Team Success On-Off",
    # Khác
    "Performance 2CrdY", "Performance Fls", "Performance Fld",
    "Performance Off", "Performance Crs", "Performance Int",
    "Performance TklW", "Performance PKwon", "Performance PKcon", "Performance OG",
]

# Ép kiểu số, thay N/a -> NaN
for col in NUMERIC_METRICS:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# ----------------------------------Tính median / mean / std theo từng đội----------------------------------

group = df.groupby('Squad')[NUMERIC_METRICS]

stats_median = group.median().add_suffix("_median")
stats_mean = group.mean().add_suffix("_mean")
stats_std = group.std().add_suffix("_std")

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
    "Metric"     : best_team_per_metric.index,
    "Best Team"          : best_team_per_metric.values,
    "Mean value"    : best_val_per_metric.values.round(4),
})

best_csv = os.path.join(OUTPUT_PATH, 'best_team_per_stat.csv')
best_table.to_csv(best_csv, index=False, encoding="utf-8-sig")
print(f"Best team per stat has been successfully saved!")

# ----------------------------------Tìm đội bóng có phong độ tốt nhất giải ngoại hạng Anh----------------------------------

# Chọn chỉ số tấn công / phòng ngự / teamwork để đánh giá phong độ
FORM_POSITIVE = [           # cao hơn = tốt hơn
    "Performance Gls", "Performance Ast", "Performance G+A",
    "Per 90 Minutes Gls", "Per 90 Minutes G+A",
    "Standard SoT", "Standard SoT%", "Standard G/Sh",
    "Team Success PPM", "Team Success +/-", "Team Success +/-90",
    "Performance TklW", "Performance Int", "Performance Fld",
]
FORM_NEGATIVE = [          # cao hơn = xấu hơn
    "Performance CrdY", "Performance CrdR",
    "Performance Fls", "Performance OG",
    "Team Success onGA",
]

form_mean = mean_df.copy()

# Chuẩn hóa Min-Max từng chỉ số
def minmax(series):
    mn, mx = series.min(), series.max()
    if mx == mn:
        return pd.Series(0.5, index=series.index)
    return (series - mn) / (mx - mn)
# vd A: 10 ban, B: 30 ban, C: 50 ban => A: 0 diem, B: 0,5 diem, C: 1 diem

score = pd.Series(0.0, index=form_mean.index)

for col in FORM_POSITIVE:
    if col in form_mean.columns:
        score += minmax(form_mean[col])
for col in FORM_NEGATIVE:
    if col in form_mean.columns:
        score += (1 - minmax(form_mean[col]))

# Số lượng chỉ số để xét
n_cols = len(FORM_POSITIVE) + len(FORM_NEGATIVE)

composite = (score / n_cols * 100).round(2) # Thang 0-100

ranking = composite.sort_values(ascending=False).reset_index()
ranking.columns = ["Team", "Composite Score (0–100)"]
ranking.index = ranking.index + 1
ranking.index.name = "Rank"

rank_csv = os.path.join(OUTPUT_PATH, 'team_form_ranking.csv')
ranking.to_csv(rank_csv, encoding='utf-8')
print(f"Ranking results have been successfully saved!")