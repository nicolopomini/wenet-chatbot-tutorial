import requests
from flask import Flask, request

app = Flask(__name__)
telegram_api_token = "1842211613:AAHlR-D03I-WmTvku5FRSJqXasHxr6NQYYM"


@app.route(f"/{telegram_api_token}", methods=["POST"])
def bot_webhook():
    print("Reuqest received")
    payload = request.json
    print(payload)
    message = payload["message"]
    print(message)
    chat_id = message["chat"]["id"]
    print(chat_id)
    text = message.get("text", "")
    print(text)
    requests.post(f"https://api.telegram.org/bot{telegram_api_token}/sendMessage", json={
        "chat_id": chat_id,
        "text": "Hello!"
    })
    return {}, 200


if __name__ == "__main__":
    app.run(port=5000, debug=True)
