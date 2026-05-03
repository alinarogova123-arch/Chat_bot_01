import requests
import telebot
from environs import Env


def run_bot(headers, params, url, bot, chat_id):
    while True:
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            continue
        else:
            if response.json().get("status") == "timeout":
                timestamp_to_request = response.json().get("timestamp_to_request")
            if response.json().get("status") == "found":
                timestamp_to_request = response.json().get("last_attempt_timestamp")
                messages = response.json().get("new_attempts")
                for message in messages:
                    link = message.get("lesson_url")
                    title = message.get("lesson_title")
                    if message.get("is_negative"):
                        result = "К сожалению, в работе нашлись ошибки."
                    else:
                        result = "Преподавателю все понравилось, можно приступать к следующему уроку!"
                    text = f"У вас проверили работу  <<{title}>>\n\n{result}\n\n{link}"
                    bot.send_message(chat_id=chat_id, text=text)
            params = {
                "timestamp": timestamp_to_request
            }


def main():
    env = Env()
    env.read_env()
    devman_api_token = env.str("DEVMAN_API_TOKEN")
    tg_bot_api_token = env.str("TELEGRAM_BOT_API_KEY")
    chat_id = env.str("TELEGRAM_CHAT_ID")
    bot = telebot.TeleBot(tg_bot_api_token)
    url = "https://dvmn.org/api/long_polling/"
    params = {}
    headers = {
        "Authorization": f"Token {devman_api_token}"
    }
    run_bot(headers, params, url, bot, chat_id)


if __name__ == "__main__":
    main()
