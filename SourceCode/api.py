from flask import Flask,request,jsonify
import pandas as pd

app = Flask(__name__)

def get_data():
    try:
        df = pd.read_csv('output/data.csv')
        return df
    except:
        return None

def search_player(name):
    df = get_data()
    if df is None:
        return jsonify({'error': 'Data file not found'})

    player_data = df[df['Player'].str.contains(name, case=False, na=False)]

    if player_data.empty:
        return jsonify({'error': 'Player data not found'})

    data = player_data.to_dict(orient='records')
    return jsonify({'data': data}), 200

# Tra cứu bằng query string: /api/player?name=Haaland
@app.route('/api/player', methods=['GET'])
def get_player_stats_query():
    name_query = request.args.get('name')
    if not name_query:
        return jsonify({'error': 'Missing name query parameter'})

    return search_player(name_query)

# Tra cứu bằng path variable: /api/player/Haaland
@app.route('/api/player/<string:name>', methods=['GET'])
def get_player_stats_path(name):
    return search_player(name)

if __name__ == '__main__':
    print("Starting Flask server...")
    print("API Endpoints:")
    print("1. GET /api/player?name=<player_name>")
    print("2. GET /api/player/<player_name>")
    app.run(debug=True)
