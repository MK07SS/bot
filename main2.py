import telebot
import time
import threading
import gspread
from gspread.exceptions import APIError
from google.oauth2.service_account import Credentials

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота
API_TOKEN = ''

# URL таблицы
SPREADSHEET_URL = ''

# Путь к файлу с учетными данными ну в принципе если делать через отправку файла в тг то это можно будет удалить
CREDENTIALS_FILE = ''

# Используемые API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

# Инициализация бота
bot = telebot.TeleBot(API_TOKEN)

# Словарь для хранения данных о пользователях
users_data = {}

# Состояния пользователя
STATE_WAITING_FOR_NAME = 1
STATE_WAITING_FOR_TEMPERATURE = 2


def ask_temperature_periodically():
    while True:
        for user_id in users_data:
            if users_data[user_id]['state'] == STATE_WAITING_FOR_TEMPERATURE:
                bot.send_message(user_id, "Введите вашу температуру:")
        time.sleep(560)  # Пауза
        # time.sleep(43200)  # Пауза в 12 часов


# Запуск потока для периодического запроса температуры
ask_thread = threading.Thread(target=ask_temperature_periodically)
ask_thread.daemon = True
ask_thread.start()


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id

    # Запоминаем состояние пользователя
    users_data[user_id] = {'state': STATE_WAITING_FOR_NAME, 'name': None, 'temperature': None}

    # Отправляем приветственное сообщение и просим ввести фамилию и имя
    bot.send_message(user_id, "Привет! Введите вашу фамилию и имя:")


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    user_message = message.text

    # Проверяем, есть ли пользователь в словаре
    if user_id in users_data:
        if users_data[user_id]['state'] == STATE_WAITING_FOR_NAME:
            # Запоминаем фамилию и имя
            users_data[user_id]['name'] = user_message
            users_data[user_id]['state'] = STATE_WAITING_FOR_TEMPERATURE

            # Отправляем приветственное сообщение и просим ввести температуру
            bot.send_message(user_id, f"Спасибо, {user_message}! Введите вашу температуру:")
        elif users_data[user_id]['state'] == STATE_WAITING_FOR_TEMPERATURE:
            try:
                # Пытаемся преобразовать сообщение в число
                temperature = float(user_message)

                # Запоминаем температуру
                users_data[user_id]['temperature'] = temperature

                print(f'{users_data}')

                # # Записываем данные в Google Sheets
                # write_to_google_table(user_id, users_data[user_id]['name'], temperature)

                # Отправляем подтверждение
                bot.send_message(user_id, f"Ваша температура: {temperature}°C. Спасибо!")
            except ValueError:
                # Если сообщение не является числом, просим повторить ввод
                bot.send_message(user_id, "Пожалуйста, введите числовое значение температуры.")
    else:
        # Если пользователь не найден, просим начать с команды /start
        bot.send_message(user_id, "Пожалуйста, начните с команды /start.")


# создаем таблицу и отправляем ее по команде
import openpyxl


def create_excel_file(user_id, name, temperature):
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet['A1'] = 'User ID'
    sheet['B1'] = 'Name'
    sheet['C1'] = 'Temperature'
    sheet.append([user_id, name, temperature])
    wb.save('example.xlsx')


def send_file(bot, chat_id, file_path):
    with open(file_path, 'rb') as file:
        bot.send_document(chat_id=chat_id, document=file)


# тут просто оставил для себя шпору
# # Создаем новый Excel-файл и активную страницу
# wb = openpyxl.Workbook()
# sheet = wb.active
#
# # Вносим переменные в таблицу ну эти данные нужно вытащить из словаря users_data = {}
# sheet['A1'] = 'Переменная 1'
# sheet['B1'] = 'Переменная 2'
#
# # Сохраняем файл
# wb.save('example.xlsx')
#
#
# # ID чата, куда будет отправлен файл тут просто подставлен мой id который я получил написав боту (проблема в том что при перезапуске бота id меняется)
# # посему нужно написать че нить типо def send_file()
# CHAT_ID = '159701137'
#
# # Путь к файлу, который нужно отправить
# FILE_PATH = 'example.xlsx'
#
# def send_file(bot, chat_id, file_path):
#     with open(file_path, 'rb') as file:
#         bot.send_document(chat_id=chat_id, document=file)
#
# def main():
#     # Создаем объект бота
#     bot = telegram.Bot(token=API_TOKEN)
#
#     # Отправляем файл
#     send_file(bot, CHAT_ID, FILE_PATH)


# Запуск бота
bot.polling()
