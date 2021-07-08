import requests
from flask import Flask, redirect, request
from wenet.interface.client import Oauth2Client
from wenet.interface.service_api import ServiceApiInterface
from wenet.interface.wenet import WeNet
from wenet.model.task.task import Task, TaskGoal
from wenet.storage.cache import InMemoryCache

app = Flask(__name__)
TELEGRAM_API_TOKEN = "1842211613:AAHlR-D03I-WmTvku5FRSJqXasHxr6NQYYM"
WENET_CLIENT_ID = "A4glP1Fbc6"
TASK_TYPE_ID = "60e6ba986fba661ff95b5b6a"

cache = InMemoryCache()
authenticated_users = {}
wenet_id_to_telegram_id = {}


def send_task(text: str, telegram_id: int):
    task = Task(
        None,
        None,
        None,
        TASK_TYPE_ID,
        authenticated_users[telegram_id],
        WENET_CLIENT_ID,
        None,
        TaskGoal(text, "")
    )
    client = Oauth2Client(
        client_id=WENET_CLIENT_ID,
        client_secret="lRlxyuhUAEFxIaVjccpZ",
        resource_id=str(telegram_id),
        cache=cache,
        token_endpoint_url="https://wenet.u-hopper.com/dev/api/oauth2/token"
    )
    service_api = ServiceApiInterface(client, "https://wenet.u-hopper.com/dev")
    service_api.create_task(task)


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
    if chat_id not in authenticated_users:
        answer = f"Hello, to use this app you have to login into wenet! Go to http://wenet.u-hopper.com/dev/hub/frontend/oauth/login?client_id={WENET_CLIENT_ID}&external_id={chat_id}"
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/sendMessage", json={
            "chat_id": chat_id,
            "text": answer
        })
        return {}, 200
    if text.startswith("/task"):
        task_text = text[5:]
        try:
            send_task(task_text, chat_id)
            response_text = "Your task has been sent"
        except Exception as e:
            print(e)
            response_text = "Something went wrong in sending the task"
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/sendMessage", json={
            "chat_id": chat_id,
            "text": response_text
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
    connector = WeNet.build(client, platform_url="https://wenet.u-hopper.com/dev")
    token_details = connector.service_api.get_token_details()
    user_profile = connector.service_api.get_user_profile(token_details.profile_id)
    username = user_profile.name.first
    wenet_id = user_profile.profile_id
    wenet_id_to_telegram_id[wenet_id] = external_id
    authenticated_users[int(external_id)] = wenet_id
    print("Saved ID binding")
    print(wenet_id_to_telegram_id)
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/sendMessage", json={
        "chat_id": external_id,
        "text": f"Welcome {username}!"
    })
    return redirect(f"http://wenet.u-hopper.com/dev/hub/frontend/oauth/complete?app_id={WENET_CLIENT_ID}")


@app.route("/wenet_callback", methods=["POST"])
def wenet_callback():
    print("Callback called")
    payload = request.json
    print(payload)
    return {}, 200


if __name__ == "__main__":
    app.run(port=5000, debug=True)
