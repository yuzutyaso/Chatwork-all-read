from flask import Flask, request, render_template, jsonify
import requests
import json
import os

app = Flask(__name__)

def mark_rooms_as_read(api_token):
    """
    指定されたAPIトークンで、すべてのChatworkの部屋を既読にする
    """
    headers = {
        "X-ChatWorkToken": api_token,
        "Accept": "application/json"
    }

    try:
        # 1. 部屋の一覧を取得する
        rooms_url = "https://api.chatwork.com/v2/rooms"
        rooms_response = requests.get(rooms_url, headers=headers)
        rooms_response.raise_for_status()
        rooms = rooms_response.json()

        if not rooms:
            return {"message": "既読にする部屋はありませんでした。"}, 200

        # 2. 各部屋に対して既読化リクエストを送信する
        for room in rooms:
            room_id = room.get("room_id")
            read_url = f"https://api.chatwork.com/v2/rooms/{room_id}/messages/read"
            requests.post(read_url, headers=headers).raise_for_status()

        return {"message": f"すべての部屋（{len(rooms)}件）を既読にしました。"}, 200

    except requests.exceptions.HTTPError as e:
        error_details = {"error": f"HTTPエラーが発生しました: {e}"}
        try:
            error_details["details"] = e.response.json()
        except (json.JSONDecodeError, AttributeError):
            pass
        return error_details, e.response.status_code
    except Exception as e:
        return {"error": f"予期せぬエラーが発生しました: {e}"}, 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mark-as-read', methods=['POST'])
def handle_read_request():
    data = request.json
    api_token = data.get('apiToken')

    if not api_token:
        return jsonify({"message": "APIトークンが提供されていません。"}), 400

    result, status_code = mark_rooms_as_read(api_token)
    return jsonify(result), status_code

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
