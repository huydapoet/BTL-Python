# BÀI TẬP LỚN LẬP TRÌNH VỚI PYTHON
**Chủ đề: Thu thập và phân tích dữ liệu cầu thủ Ngoại hạng Anh mùa 2025-2026**

## Thông tin nhóm
* **Thành viên 1:** Trịnh Lâm Huy - B24DCCE134
* **Thành viên 2:** Trần Quang Hưng - B24DCCE120
* **Lớp:** D24CQCE01-B
* **Giảng viên hướng dẫn:** Thầy Kim Ngọc Bách

---

## Hướng dẫn cài đặt

1. **Yêu cầu hệ thống:** Python 3.8 trở lên.
2. **Cài đặt thư viện:** Mở terminal tại thư mục gốc của project (nơi chứa file `requirements.txt`) và chạy lệnh sau để cài đặt tất cả các thư viện cần thiết:
   ```bash
   pip install -r requirements.txt
   ```

---

## Cấu trúc Repository
Dự án được tổ chức như sau:

```text
BTL-Python/
├── Report/                   # Chứa file báo cáo chi tiết thuật toán & kết quả
│   └── report.pdf            # File báo cáo định dạng PDF
├── output/                   # Thư mục lưu trữ dữ liệu cào được và kết quả đầu ra (CSV, Biểu đồ)
├── requirements.txt          # Danh sách các thư viện cần thiết cho project
└── SourceCode/               # Toàn bộ mã nguồn chương trình Python
    ├── crawling.py           # Mã nguồn cào dữ liệu từ fbref.com (Câu 1)
    ├── api.py                # Restful API sử dụng Flask cung cấp dữ liệu (Câu 2)
    ├── gui.py                # Giao diện Tkinter & Biểu đồ Radar so sánh cầu thủ (Câu 3)
    ├── analysis.py           # Thống kê mô tả & Xếp hạng phong độ đội bóng (Câu 4)
    └── kmeans.py             # Phân cụm K-means & Giảm chiều PCA (Câu 5)
```

---

## Hướng dẫn chạy chương trình

Toàn bộ mã nguồn nằm trong thư mục `SourceCode`. Khi chạy các file xử lý, dữ liệu đầu ra và các biểu đồ sẽ được tự động lưu vào thư mục `output/` ở gốc dự án.

### 1. Thu thập dữ liệu (Crawling)
Script sử dụng `seleniumbase` để tự động mở trình duyệt và lấy dữ liệu cầu thủ từ FBref.
```bash
python SourceCode/crawling.py
```
* **Kết quả:** File dữ liệu thô `data.csv` sẽ được tạo và lưu trong thư mục `output/`.

### 2. Giao diện tra cứu & So sánh cầu thủ (API & GUI)
Để sử dụng giao diện so sánh cầu thủ bằng biểu đồ Radar, bạn **phải chạy 2 file song song** ở 2 cửa sổ Terminal/Command Prompt khác nhau:

**Bước 2.1: Chạy Server API (Terminal 1)**
```bash
python SourceCode/api.py
```
*(Giữ nguyên terminal này chạy ngầm để ứng dụng GUI có thể lấy được dữ liệu)*

**Bước 2.2: Chạy Giao diện GUI (Terminal 2)**
```bash
python SourceCode/gui.py
```
* **Cách sử dụng GUI:** 
  - Gõ tên cầu thủ 1 và cầu thủ 2 vào 2 ô tìm kiếm (VD: `Haaland`, `Salah`) và nhấn **Search**.
  - Tích chọn **ít nhất 3 chỉ số** giống nhau ở cả hai bên để có thể so sánh.
  - Nhấn nút **Compare** màu xanh ở dưới cùng để hệ thống hiển thị biểu đồ Radar so sánh năng lực của hai cầu thủ.

### 3. Phân tích thống kê (Analysis)
Tính toán các chỉ số thống kê, tìm đội xuất sắc nhất ở mỗi chỉ số và xếp hạng phong độ các đội bóng dựa trên trọng số điểm.
```bash
python SourceCode/analysis.py
```
* **Kết quả:** Tạo ra các file `team_stats.csv`, `best_team_per_stat.csv`, và `team_form_ranking.csv` trong thư mục `output/`.

### 4. Phân cụm Học máy (Machine Learning - K-Means & PCA)
Phân nhóm cầu thủ theo chỉ số và vẽ biểu đồ 2D/3D (yêu cầu thao tác trên terminal).
```bash
python SourceCode/kmeans.py
```
* **Cách sử dụng:** 
  1. Khi script chạy, nhập lựa chọn đối tượng phân cụm: `gk` (Thủ môn), hoặc `outfield` (Cầu thủ tuyến trên).
  2. Xem các biểu đồ Elbow và Silhouette hiện lên để đánh giá (tắt cửa sổ hình ảnh để tiếp tục).
  3. Nhập số lượng cụm (k) tối ưu vào terminal theo yêu cầu.
  4. Xem và nhận kết quả phân nhóm qua biểu đồ PCA 2D và 3D. (Tất cả biểu đồ sẽ được lưu tự động vào `output/`).


