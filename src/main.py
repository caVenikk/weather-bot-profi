import time
from datetime import datetime

import requests
import telebot
from requests.exceptions import ConnectionError, ReadTimeout
from telebot.types import InlineKeyboardMarkup
from urllib3.exceptions import ReadTimeoutError, TimeoutError

from config import TOKEN, APPID

bot = telebot.TeleBot(TOKEN)
URL_BASE = "https://api.openweathermap.org/data/2.5/"


def current_weather(q: str = "Chicago", appid: str = APPID) -> dict:
    return requests.get(URL_BASE + "weather", params=locals()).json()


@bot.message_handler(commands=["start"])
def start_def(message):
    bot.send_message(
        message.chat.id,
        "Этот бот поможет тебе узнать погоду." "\nВведите город пожалусат",
    )
    bot.register_next_step_handler(message, weather_def)


def weather_def(message):
    global location

    location = message.text.strip()
    d = current_weather(location)
    if d["cod"] == "404":
        bot.send_message(message.chat.id, "Такой город не найден, попробуйте ещё раз")
        bot.register_next_step_handler(message, weather_def)
    else:
        d_main = d["main"]
        t_max = round(d_main["temp_max"]) - 273
        t_min = round(d_main["temp_min"]) - 273
        t_feels_like = round(d_main["feels_like"]) - 273
        button = telebot.types.InlineKeyboardButton(
            text="Узнать погоду в другом городе", callback_data="button_clicked"
        )
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(button)
        bot.send_message(
            message.chat.id,
            f"Температура в городе  {location} "
            f"\nТемпература варьируется от {t_max} до {t_min} (°C) "
            f"\nОщущается как {t_feels_like}  (°C)",
            reply_markup=keyboard,
        )


@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    global location
    if call.data == "button_clicked":
        bot.send_message(call.message.chat.id, "Введите название города")
        bot.register_next_step_handler(call.message, weather_def)
        reply_markup = InlineKeyboardMarkup()
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=reply_markup,
        )


if __name__ == "__main__":
    print(f"{datetime.now()} | Running")
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except (ConnectionError, ReadTimeout, ReadTimeoutError, TimeoutError) as e:
            if "traceback" not in e:
                print(f"{datetime.now()} | {e}")
            time.sleep(5)
            continue
