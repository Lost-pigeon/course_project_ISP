from flask import Flask, request, jsonify, json
from model_route import model
from database.sql_provider import SQLProvider
import os

app = Flask(__name__)

with open("../data/db_config.json") as f:
    app.config['db_config'] = json.load(f)

app.config['provider'] = SQLProvider(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'api', 'sql'))


@app.route('/api/auth', methods=['POST'])
def authenticate():
    data = request.get_json()
    print(data)
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Invalid request"}), 400
    result = model(app.config['db_config'], data, app.config['provider'])
    print(result)
    if result.status:
        return jsonify({"id": result.result[0]['user_id'], "role": 'client'}), 200
    else:
        return jsonify({"error": "Unauthorized"}), 401


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5004)
