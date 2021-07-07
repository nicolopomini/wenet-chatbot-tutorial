import requests
from flask import Flask, request

app = Flask(__name__)
telegram_api_token = "1842211613:AAHlR-D03I-WmTvku5FRSJqXasHxr6NQYYM"


@app.route(f"/{telegram_api_token}", methods=["POST"])
def bot_webhook():
    payload = request.json
    message = payload["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "")
    requests.post(f"https://api.telegram.org/bot{telegram_api_token}/sendMessage", json={
        "chat_id": chat_id,
        "text": "Hello!"
    })
    return {}


if __name__ == "__main__":
    app.run(port=5000, debug=True)
