import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from yellowbrick.cluster import SilhouetteVisualizer

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
OUTPUT_PATH = os.path.join(BASE_DIR, 'output')
DATA_PATH = os.path.join(OUTPUT_PATH, 'data.csv')
OUTFIELD_OUTPUT = os.path.join(OUTPUT_PATH, 'outfield_kmeans')
GK_OUTPUT = os.path.join(OUTPUT_PATH, 'gk_kmeans')
ALL_OUTPUT = os.path.join(OUTPUT_PATH, 'all_kmeans')
os.makedirs(OUTPUT_PATH, exist_ok=True)
os.makedirs(OUTFIELD_OUTPUT, exist_ok=True)
os.makedirs(GK_OUTPUT, exist_ok=True)
os.makedirs(ALL_OUTPUT, exist_ok=True)

print('Reading data...')
df = pd.read_csv(DATA_PATH)

df_out = df[~df['Pos'].str.contains('GK', na=False)].copy().reset_index(drop=True)
df_gk = df[df['Pos'].str.contains('GK', na=False)].copy().reset_index(drop=True)

OUTFIELD = [
    # --- CHỈ SỐ TẤN CÔNG (ATK) ---
    'Per 90 Minutes Gls',  # Bàn thắng ghi được mỗi 90 phút
    'Per 90 Minutes Ast',  # Số pha kiến tạo mỗi 90 phút
    'Standard Sh/90',      # Số cú sút tung ra mỗi 90 phút
    'Standard SoT/90',     # Số cú sút trúng đích mỗi 90 phút
    'Standard G/Sh',       # Tỷ lệ bàn thắng trên mỗi cú sút (Hiệu suất dứt điểm)
    'Performance Off',     # Số lần bị thổi việt vị
    'Performance Fld',     # Số lần bị phạm lỗi (mang lại quả phạt cho đội)
    
    # --- CHỈ SỐ PHÒNG NGỰ (DEF) ---
    'Performance TklW',    # Số pha tắc bóng (thu hồi bóng) thành công
    'Performance Int',     # Số lần cắt bóng / đánh chặn
    'Performance Fls',     # Số lần phạm lỗi với đối phương
    'Performance CrdY',    # Số thẻ vàng phải nhận
    'Performance CrdR',    # Số thẻ đỏ phải nhận
    'Performance Crs',     # Số lượng quả tạt bóng
    
    # --- CHỈ SỐ ĐÓNG GÓP TẬP THỂ (TEAM) ---
    'Team Success PPM',    # Điểm số trung bình giành được mỗi trận khi cầu thủ ra sân (Points Per Match)
    'Team Success +/-90',  # Hiệu số bàn thắng/thua của đội mỗi 90 phút khi cầu thủ có mặt trên sân
    # "Playing Time 90s",    # Tổng số thời gian thi đấu (quy đổi ra số trận 90 phút)
]

GK = [
    # --- CHỈ SỐ THỦ MÔN (GOALKEEPER) ---
    'Performance Save%',   # Tỷ lệ cứu thua thành công (%)
    'Performance GA90',    # Số bàn thua trung bình mỗi 90 phút (Goals Against)
    'Performance CS%',     # Tỷ lệ phần trăm số trận giữ sạch lưới (Clean Sheets)
    'Performance W',       # Số trận thắng bắt chính
    'Performance D',       # Số trận hòa bắt chính
    'Performance L',       # Số trận thua bắt chính
    'Penalty Kicks Save%', # Tỷ lệ cản phá phạt đền (Penalty) thành công (%)
    'Performance Saves',   # Tổng số pha cứu thua thành công
]

ALL = OUTFIELD + GK

print('Preprocessing data...')
def preprocess_features(data, columns):
    numeric_data = data[columns].copy()
    # Làm sạch các dấu phẩy và ép kiểu về số
    for col in columns:
        numeric_data[col] = numeric_data[col].astype(str).str.replace(',','')
        numeric_data[col] = pd.to_numeric(numeric_data[col], errors='coerce')
    # Loại bỏ các cột toàn NaN và điền 0 cho các giá trị NaN còn lại
    numeric_data = numeric_data.dropna(axis=1, how='all').fillna(0)
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(numeric_data)
    return numeric_data, scaled_data

X, X_scaled = preprocess_features(df_out, OUTFIELD)
X_gk, X_gk_scaled = preprocess_features(df_gk, GK)


X_all, X_all_scaled = preprocess_features(df, ALL)

# Hàm vẽ Elbow plot
def elbow_plot(X_scaled_data, title, output_path, file_name, kmin=1, kmax=10):
    distortions = []
    K_range = range(kmin, kmax + 1)
    for k in K_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(X_scaled_data)
        distortions.append(kmeans.inertia_)

    fig = plt.figure(figsize=(10, 6))
    plt.plot(K_range, distortions, 'bx-')
    plt.xlabel('Number of clusters (k)')
    plt.ylabel('Distortion')
    plt.title(title)
    plt.grid(True)
    out_path = os.path.join(output_path, file_name)
    fig.savefig(out_path)
    plt.show()
    plt.close(fig)
    print('Elbow plot generated successfully.')

# Hàm vẽ Silhouette plot
def silhouette_multi_plot(X_scaled_data, title, output_path, file_name, k_min=2, k_max=5):
    num_k = k_max - k_min + 1
    cols = 2
    rows = (num_k + 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(15, 6 * rows))
    fig.suptitle(title, fontsize=16)

    for i, k in enumerate(range(k_min, k_max + 1)):
        ax = axes[i // cols, i % cols] if rows > 1 else axes[i % cols]
        model = KMeans(n_clusters=k, random_state=42, n_init=10)
        visualizer = SilhouetteVisualizer(model, ax=ax, colors='yellowbrick', force_model=True)
        visualizer.fit(X_scaled_data)
        visualizer.finalize()
        ax.set_title(f"k = {k}")

    fig.tight_layout()
    out_path = os.path.join(output_path, file_name)
    fig.savefig(out_path)
    plt.show()
    plt.close(fig)
    print('Silhouette plots created successfully.')

# Sử dụng thuật toán PCA vẽ scatter plot phân cụm dữ liệu trên mặt 2D
def plot_pca_2d(df, X_scaled_data, title, output_path, file_name, cluster_col='Cluster'):
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled_data)
    df['PCA1_2D'] = X_pca[:, 0]
    df['PCA2_2D'] = X_pca[:, 1]

    fig = plt.figure(figsize=(10, 8))
    sns.scatterplot(x='PCA1_2D', y='PCA2_2D', hue=cluster_col, palette='viridis', data=df, s=80, alpha=0.8)
    plt.title(title)
    plt.xlabel('Principal Component 1 (PCA1)')
    plt.ylabel('Principal Component 2 (PCA2)')
    plt.legend(title='Cluster')
    plt.grid(True)
    out_path = os.path.join(output_path, file_name)
    fig.savefig(out_path)
    plt.show()
    plt.close(fig)
    print('PCA 2D plot generated successfully.')

# Sử dụng thuật toán PCA vẽ scatter plot phân cụm dữ liệu trên mặt 3D
def plot_pca_3d(df, X_scaled_data, title, output_path, file_name, cluster_col='Cluster'):
    pca = PCA(n_components=3)
    X_pca = pca.fit_transform(X_scaled_data)
    df['PCA1_3D'] = X_pca[:, 0]
    df['PCA2_3D'] = X_pca[:, 1]
    df['PCA3_3D'] = X_pca[:, 2]

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    scatter = ax.scatter(df['PCA1_3D'], df['PCA2_3D'], df['PCA3_3D'], c=df[cluster_col], cmap='viridis', s=40, alpha=0.8)
    ax.set_title(title)
    ax.set_xlabel('PCA1')
    ax.set_ylabel('PCA2')
    ax.set_zlabel('PCA3')
    legend = ax.legend(*scatter.legend_elements(), title='Cluster')
    ax.add_artist(legend)
    out_path = os.path.join(output_path, file_name)
    fig.savefig(out_path)
    plt.show()
    plt.close(fig)
    print('PCA 3D plot generated successfully.')

while True:
    choice = input(
        '\nPlease select the clustering category:\n'
        '[all] All players clusters (GK + Outfield)\n'
        '[gk]  Goalkeeper clusters\n'
        '[outfield] Outfield player clusters\n'
        '[exit] Exit program\n'
        'Enter your choice: '
    ).lower()
    if choice == 'exit': break
    elif choice == 'outfield':
        # ---------------------- Vẽ elbow, housette, scatter cho outfield player
        # Vẽ Elbow plot
        print('Generating Elbow plots for outfield players...')
        elbow_plot(X_scaled, 'The Elbow Plot showing the optimal k for Outfield Players',OUTFIELD_OUTPUT, 'elbow_plot.png', kmin=2, kmax=10)

        # Vẽ Silhouette plot
        print('Generating Silhouette plots for outfield players...')
        silhouette_multi_plot(X_scaled, 'Silhouette Plots for Outfield Players (k=2 to 5)',OUTFIELD_OUTPUT, 'silhouette_multi_plot.png', k_min=2, k_max=5)

        # print("Running K-Means & PCA for outfield players...")
        optimal_k = int(input('\nEnter the optimal k for Outfield Players: '))
        kmeans_opt = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
        df_out['Cluster'] = kmeans_opt.fit_predict(X_scaled)

        # Vẽ scatter plot
        print('Generating PCA 2D & 3D for outfield players...')
        plot_pca_2d(df_out, X_scaled, 'Outfield Player Clusters (K-means) - PCA 2D', OUTFIELD_OUTPUT, 'pca_2d_clusters.png')
        plot_pca_3d(df_out, X_scaled, 'Outfield Player Clusters (K-means) - PCA 3D', OUTFIELD_OUTPUT, 'pca_3d_clusters.png')

        # for i in range(optimal_k):
        #     cluster_df = df_out[df_out['Cluster'] == i]
        #     file_path = os.path.join(OUTPUT_PATH, f'cluster_{i}.csv')
        #     cluster_df.to_csv(file_path, index=False)
        #     print(f"Saved Cluster {i} with {len(cluster_df)} players to: {file_path}")

    elif choice == 'gk':
        # ---------------------- Vẽ elbow, Sillhousette, scatter cho gk
        # Vẽ Elbow plot
        print('Generating Elbow plots for Goalkeepers...')
        elbow_plot(X_gk_scaled, 'The Elbow Plot showing the optimal k for GK',GK_OUTPUT, 'elbow_gk.png', kmin=1, kmax=6)

        # Vẽ Silhouette plot
        print('Generating Silhouette plots for outfield Goalkeepers...')
        silhouette_multi_plot(X_gk_scaled, 'Silhouette Plots for Goalkeepers (k=2 to 5)',GK_OUTPUT, 'silhouette_gk_multi_plot.png', k_min=2, k_max=5)

        # print("Running K-Means & PCA for Goalkeepers...")
        optimal_k = int(input('\nEnter the optimal k for Goalkeepers: '))
        kmeans_gk_opt = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
        df_gk['Cluster'] = kmeans_gk_opt.fit_predict(X_gk_scaled)

        print('Generating PCA 2D & 3D for Goalkeepers...')
        plot_pca_2d(df_gk, X_gk_scaled, 'GK Clusters (K-means) - PCA 2D', GK_OUTPUT, 'pca_gk_2d_clusters.png')
        plot_pca_3d(df_gk, X_gk_scaled, 'GK Clusters (K-means) - PCA 3D', GK_OUTPUT, 'pca_gk_3d_clusters.png')

    elif choice == 'all':
        # Vẽ Elbow plot
        print('Generating Elbow plots for all players...')
        elbow_plot(X_all_scaled, 'The Elbow Plot showing the optimal k for All Players',ALL_OUTPUT, 'elbow.png', kmin=2, kmax=6)

        # Vẽ Sillhousette plot
        print('Generating Silhouette plots for All players...')
        silhouette_multi_plot(X_all_scaled, 'Silhouette Plots for All Players (k=2 to 5)',ALL_OUTPUT, 'silhouette_multi_plot.png', k_min=2, k_max=5)

        optimal_k = int(input('\nEnter the optimal k for All Players: '))
        kmeans_opt = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
        df['Cluster'] = kmeans_opt.fit_predict(X_all_scaled)

        # Vẽ scatter plot
        print('Generating PCA 2D & 3D for all players...')
        plot_pca_2d(df, X_all_scaled, f'All Player Clusters (K-means) - PCA 2D', ALL_OUTPUT, 'pca_all_2d_clusters.png')
        plot_pca_3d(df, X_all_scaled, f'All Player Clusters (K-means) - PCA 3D', ALL_OUTPUT, 'pca_all_3d_clusters.png')

    else:
        print('Invalid input, please try again.')