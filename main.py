import time

import logging
import requests
import telebot
from environs import Env
from telebot import apihelper


logger = logging.getLogger(__name__)


def run_bot(headers, params, url, bot, chat_id):
    attempt = 0
    while True:
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            attempt += 1
            if attempt > 10:
                time.sleep(20)
        else:
            attempt = 0
            notification = response.json()
            if notification.get("status") == "timeout":
                timestamp_to_request = notification.get("timestamp_to_request")
            if notification.get("status") == "found":
                timestamp_to_request = notification.get("last_attempt_timestamp")
                messages = notification.get("new_attempts")
                for message in messages:
                    link = message.get("lesson_url")
                    title = message.get("lesson_title")
                    if message.get("is_negative"):
                        review = "К сожалению, в работе нашлись ошибки."
                    else:
                        review = "Преподавателю все понравилось, можно приступать к следующему уроку!"
                    text = f"У вас проверили работу  <<{title}>>\n\n{review}\n\n{link}"
                    bot.send_message(chat_id=chat_id, text=text)
            params = {
                "timestamp": timestamp_to_request
            }


def main():
    env = Env()
    env.read_env()
    proxy_ip = env.str("PROXY")
    devman_api_token = env.str("DEVMAN_API_TOKEN")
    tg_bot_api_token = env.str("TELEGRAM_BOT_API_KEY")
    chat_id = env.str("TELEGRAM_CHAT_ID")
    proxy_url = f'socks5h://{proxy_ip}'
    apihelper.proxy = {'https': proxy_url}
    bot = telebot.TeleBot(tg_bot_api_token)

    class MyLogsHandler(logging.Handler):

        def emit(self, record):
            log_entry = self.format(record)
            bot.send_message(chat_id=chat_id, text=log_entry)

    logging.basicConfig(format="%(process)d %(levelname)s %(message)s")
    logger.setLevel(logging.INFO)
    logger.addHandler(MyLogsHandler())
    logger.info("Бот запущен.")
    logger.error("Бот упал с ошибкой")

    url = "https://dvmn.org/api/long_polling/"
    params = {}
    headers = {
        "Authorization": f"Token {devman_api_token}"
    }
    run_bot(headers, params, url, bot, chat_id)


if __name__ == "__main__":
    main()
