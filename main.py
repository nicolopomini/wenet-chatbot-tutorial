import requests
from flask import Flask, redirect, request
from wenet.interface.client import Oauth2Client
from wenet.interface.wenet import WeNet
from wenet.storage.cache import InMemoryCache

app = Flask(__name__)
TELEGRAM_API_TOKEN = "1842211613:AAHlR-D03I-WmTvku5FRSJqXasHxr6NQYYM"
WENET_CLIENT_ID = "A4glP1Fbc6"

cache = InMemoryCache()
authenticated_users = set()


@app.route(f"/{TELEGRAM_API_TOKEN}", methods=["POST"])
def bot_webhook():
    """
    This function handles all the messages coming from the bot.
    If the user is not authenticated, a link for the login is returned to the user.
    Otherwise, we handle the command the user sent
    """
    payload = request.json
    message = payload["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "")
    print(chat_id)
    print(authenticated_users)
    if chat_id not in authenticated_users:
        answer = f"Hello, to use this app you have to login into wenet! Go to http://wenet.u-hopper.com/dev/hub/frontend/oauth/login?client_id={WENET_CLIENT_ID}&external_id={chat_id}"
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/sendMessage", json={
            "chat_id": chat_id,
            "text": answer
        })
        return {}, 200
    answer = "Hello!"
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/sendMessage", json={
        "chat_id": chat_id,
        "text": answer
    })
    return {}, 200


@app.route("/login")
def login():
    """
    Handle the OAuth login, and saves the access token to a local cache
    """
    code = request.args.get('code')
    external_id = request.args.get("external_id")
    client = Oauth2Client.initialize_with_code(client_id=WENET_CLIENT_ID,
                                               client_secret="lRlxyuhUAEFxIaVjccpZ",
                                               code=code,
                                               resource_id=external_id,
                                               cache=cache,
                                               token_endpoint_url="https://wenet.u-hopper.com/dev/api/oauth2/token",
                                               redirect_url="https://wenet-chatbot-tutorial.herokuapp.com/login"
                                               )
    authenticated_users.add(external_id)
    connector = WeNet.build(client, platform_url="https://wenet.u-hopper.com/dev")
    token_details = connector.service_api.get_token_details()
    username = connector.service_api.get_user_profile(token_details.profile_id).name.first
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/sendMessage", json={
        "chat_id": external_id,
        "text": f"Welcome {username}!"
    })
    print(authenticated_users)
    return redirect(f"http://wenet.u-hopper.com/dev/hub/frontend/oauth/complete?app_id={WENET_CLIENT_ID}")


if __name__ == "__main__":
    app.run(port=5000, debug=True)
