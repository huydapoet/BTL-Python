from flask import Flask, request, jsonify
import pandas as pd
import os

# Khởi tạo ứng dụng Flask
app = Flask(__name__)

app.json.ensure_ascii = False

# Xác định thư mục gốc của project
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Tìm file CSV
def find_csv():
    for candidate in [
        os.path.join(_PROJECT_ROOT, 'data.csv'),
        os.path.join(_PROJECT_ROOT, 'output', 'data.csv'),
    ]:
        if os.path.exists(candidate):
            return candidate
    return None

dataframe = None

# Hàm đọc dữ liệu
def get_data():
    global dataframe
    if dataframe is None:
        file_path = find_csv()
        if not file_path:
            return None
        try:
            dataframe = pd.read_csv(file_path)
        except Exception as e:
            print('Error loading CSV:', e)
            dataframe = None
    return dataframe

# Hàm tìm kiếm cầu thủ
def search_player(name):
    df = get_data()

    if df is None:
        return jsonify({'error': 'Data file not found'}), 500

    if 'Player' not in df.columns:
        return jsonify({'error': 'Invalid data format'}), 500

    player_data = df[df['Player'].str.contains(name, case=False, na=False)]

    if player_data.empty:
        return jsonify({'error': 'Player data not found'}), 404

    data = player_data.to_dict(orient='records')
    return jsonify({'data': data}), 200

# Tra cứu bằng query string: /api/player?name=Haaland
@app.route('/api/player', methods=['GET'])
def get_player_stats_query():
    name_query = request.args.get('name')
    if not name_query:
        return jsonify({'error': 'Missing name query parameter'}), 400

    return search_player(name_query)

# Tra cứu bằng path variable: /api/player/Haaland
@app.route('/api/player/<string:name>', methods=['GET'])
def get_player_stats_path(name):
    return search_player(name)

# Khởi chạy server
if __name__ == '__main__':
    print('Starting Flask server...')
    print('API Endpoints:')
    print('1. GET /api/player?name=<player_name>')
    print('2. GET /api/player/<player_name>')
    app.run(debug=True)

