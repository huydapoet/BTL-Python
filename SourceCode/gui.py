import tkinter as tk
from tkinter import messagebox
import requests
import matplotlib.pyplot as plt
import numpy as np

class PlayerCompareGUI:

    def __init__(self, root):

        self.root = root
        self.root.title('Player Search & Comparison')
        self.root.geometry('900x600')

        self.api_url = 'http://127.0.0.1:5000/api/player'
        self.data_p1 = None
        self.data_p2 = None

        # Từ điển để lưu các checkbox được tích chọn
        # Chỉ số (stat_name) -> BooleanVar
        self.check_vars = {}

        # Giao diện chính chia làm 2 cột
        self.frame_main = tk.Frame(root)
        self.frame_main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Khung chứa cột 1
        self.frame_p1 = tk.Frame(self.frame_main, bd=1, relief='ridge')
        self.frame_p1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # Khung chứa cột 2
        self.frame_p2 = tk.Frame(self.frame_main, bd=1, relief='ridge')
        self.frame_p2.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        # ---------------- CỘT 1 ----------------
        tk.Label(self.frame_p1, text='Player 1', font=('Arial', 12, 'bold')).pack(pady=5)
        self.entry_p1 = tk.Entry(self.frame_p1, font=('Arial', 12))
        self.entry_p1.pack(fill=tk.X, padx=10, pady=5)
        tk.Button(self.frame_p1, text='Search', bg='blue', fg='white', command=lambda: self.search_player(1)).pack \
            (pady=5)

        self.canvas_p1, self.scroll_p1, self.inner_p1 = self.create_scrollable_frame(self.frame_p1)

        # ---------------- CỘT 2 ----------------
        tk.Label(self.frame_p2, text='Player 2', font=('Arial', 12, 'bold')).pack(pady=5)
        self.entry_p2 = tk.Entry(self.frame_p2, font=('Arial', 12))
        self.entry_p2.pack(fill=tk.X, padx=10, pady=5)
        tk.Button(self.frame_p2, text='Search', bg='blue', fg='white', command=lambda: self.search_player(2)).pack \
            (pady=5)

        self.canvas_p2, self.scroll_p2, self.inner_p2 = self.create_scrollable_frame(self.frame_p2)

        # ---------------- NÚT SO SÁNH ----------------
        tk.Button(root, text='Compare', font=('Arial', 14, 'bold'), bg='#4CAF50', fg='white', command=self.compare).pack(pady=15)

    def create_scrollable_frame(self, parent):
        """Hàm hỗ trợ tạo frame có thanh cuộn dọc (Scrollbar)"""
        canvas = tk.Canvas(parent)
        scrollbar = tk.Scrollbar(parent, orient='vertical', command=canvas.yview)
        inner_frame = tk.Frame(canvas)

        inner_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        canvas.create_window((0, 0), window=inner_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Cập nhật cuộn bằng chuột
        def _on_mousewheel(event):
            # Chỉ cuộn canvas nếu con trỏ chuột đang nằm trên nó hoặc các con của nó
            try:
                widget = event.widget.winfo_containing(event.x_root, event.y_root)
                curr = widget
                while curr:
                    if curr == canvas:
                        canvas.yview_scroll(int(- 1 *(event.delta/120)), 'units')
                        return
                    curr = curr.master
            except Exception:
                pass

        canvas.bind_all('<MouseWheel>', _on_mousewheel, add='+')

        return canvas, scrollbar, inner_frame

    def search_player(self, player_num):
        entry = self.entry_p1 if player_num == 1 else self.entry_p2
        name = entry.get().strip()
        if not name:
            messagebox.showwarning('Error', 'Please enter a player name!')
            return

        try:
            # Gửi request lên API
            response = requests.get(f"{self.api_url}?name={name}")
            if response.status_code == 200:
                data = response.json().get('data', [])
                if data:
                    player_data = data[0] # Lấy kết quả đầu tiên tìm được
                    if player_num == 1:
                        self.data_p1 = player_data
                        self.display_stats(self.inner_p1, player_data)
                    else:
                        self.data_p2 = player_data
                        self.display_stats(self.inner_p2, player_data)
                else:
                    messagebox.showinfo('Info', 'Player not found!')
            else:
                messagebox.showerror('Error', f"Server error: {response.json().get('error', 'Unknown Error')}")
        except requests.exceptions.ConnectionError:
            messagebox.showerror('Error', 'Cannot connect to API. Make sure api.py is running!')
        except Exception as e:
            messagebox.showerror('Error', f"An error occurred: {e}")

    def safe_float(self, val):
        """Hỗ trợ chuyển đổi an toàn sang float"""
        try:
            return float(str(val).replace(',', ''))
        except ValueError:
            return 0.0

    def display_stats(self, parent, player_data):
        # Xóa các widget cũ trong frame kết quả
        for widget in parent.winfo_children():
            widget.destroy()

        # Hiển thị thông tin cơ bản
        tk.Label(parent, text=f"Name: {player_data.get('Player', 'N/A')}", font=('Arial', 11, 'bold')).pack(anchor='w', padx=10, pady=(5 ,0))
        tk.Label(parent, text=f"Club: {player_data.get('Squad', 'N/A')}").pack(anchor='w', padx=10)
        tk.Label(parent, text='--- Stats ---', fg='blue').pack(anchor='w', padx=10, pady=(5, 5))

        # Bỏ qua những cột không phải là số/chỉ số (tuỳ vào dữ liệu thực tế)
        exclude_cols = ['Player', 'Nation', 'Pos', 'Squad', 'Age', 'Born', 'Matches']

        # Hiển thị tickbox cho mỗi chỉ số
        for stat_name, stat_val in player_data.items():
            if stat_name in exclude_cols:
                continue

            try:
                # Đảm bảo là số hợp lệ thì mới hiện checkbox
                num_val = float(str(stat_val).replace(',', ''))

                frame = tk.Frame(parent)
                frame.pack(fill=tk.X, anchor='w', padx=15)

                # Tạo BooleanVar cho chỉ số nếu chưa có
                if stat_name not in self.check_vars:
                    self.check_vars[stat_name] = tk.BooleanVar(value=False)

                cb = tk.Checkbutton(frame, text=f"{stat_name}: {num_val:g}", variable=self.check_vars[stat_name])
                cb.pack(side=tk.LEFT)
            except ValueError:
                pass

    def compare(self):
        if not self.data_p1 or not self.data_p2:
            messagebox.showwarning('Warning', 'Need to search for 2 players to compare!')
            return

        # Lấy danh sách các chỉ số được chọn
        selected_stats = [stat for stat, var in self.check_vars.items() if var.get()]

        if len(selected_stats) < 3:
            messagebox.showwarning('Warning', 'Please select at least 3 stats to draw radar chart!')
            return

        name1 = self.data_p1.get('Player', 'Player 1')
        name2 = self.data_p2.get('Player', 'Player 2')

        values1 = []
        values2 = []

        # Lấy giá trị của các chỉ số đã chọn
        for stat in selected_stats:
            v1 = self.safe_float(self.data_p1.get(stat, 0))
            v2 = self.safe_float(self.data_p2.get(stat, 0))
            values1.append(v1)
            values2.append(v2)

        # Chuẩn hoá dữ liệu (thang 0 -> 1) để vẽ cùng trên biểu đồ radar
        max_vals = [max(v1, v2, 1e-9) for v1, v2 in zip(values1, values2)]
        norm_v1 = [v / m for v, m in zip(values1, max_vals)]
        norm_v2 = [v / m for v, m in zip(values2, max_vals)]

        # Lặp lại giá trị đầu tiên để đóng kín radar chart
        norm_v1 += norm_v1[:1]
        norm_v2 += norm_v2[:1]
        angles = np.linspace(0, 2 * np.pi, len(selected_stats), endpoint=False).tolist()
        angles += angles[:1]

        # Vẽ biểu đồ radar với matplotlib
        fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
        ax.set_theta_offset(np.pi / 2) # Xoay góc bắt đầu lên đỉnh
        ax.set_theta_direction(-1)     # Vẽ theo chiều kim đồng hồ

        # Cài đặt nhãn cho các trục
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(selected_stats, fontsize=9)

        # Vẽ Player 1
        ax.plot(angles, norm_v1, label=name1, linewidth=2, linestyle='solid', color='blue')
        ax.fill(angles, norm_v1, alpha=0.25, color='blue')

        # Vẽ Player 2
        ax.plot(angles, norm_v2, label=name2, linewidth=2, linestyle='solid', color='red')
        ax.fill(angles, norm_v2, alpha=0.25, color='red')

        ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'], color='grey', size=8)
        ax.set_ylim(0, 1.0)

        # Thêm ghi chú
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        plt.title(f"Comparison: {name1} vs {name2}", y=1.08, fontweight='bold')

        plt.tight_layout()
        plt.show()

if __name__ == '__main__':
    root = tk.Tk()
    app = PlayerCompareGUI(root)
    root.mainloop()
