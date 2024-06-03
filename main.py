import os

from pyrogram import Client, filters
from dotenv import load_dotenv
from os import getenv
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from dialog import Dialog
from database_operator import Operator
from parser import get_json, get_schedule, get_session_schedule
import hashlib
import logging

# Initialization

logging.basicConfig(level=logging.INFO, filemode='w',
                    format='%(asctime)s %(levelname)s %(message)s')

load_dotenv()

api_id = getenv('api_id')
api_hash = getenv('api_hash')
bot_token = getenv('bot_token')
logging.info('Environment variables loaded')

app = Client('MPUScheduleBot', api_id=api_id, api_hash=api_hash, bot_token=bot_token)

dialogs: [str, Dialog] = dict()

general_calendars = list()

operator = Operator()

if not os.path.isdir('schedules'):
    os.mkdir('schedules')

# Main handlers


@app.on_message(filters.text & filters.private & filters.command("start"))
async def start(client: Client, message: Message):
    logging.info(f'Bot Started by {message.chat.id}')
    dialogs[message.chat.id] = Dialog()
    dialogs[message.chat.id].started()
    await menu(client, message)


async def menu(client: Client, message: Message):
    await app.send_message(
        message.chat.id,  # Edit this
        "Меню",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Получить расписание по номеру группы",
                        callback_data="get_timetable",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Получить расписание сессии по номеру группы",
                        callback_data="get_session_timetable",
                    ),
                ]
            ]
        )
    )


@app.on_callback_query()
async def get_timetable(client: Client, callback: CallbackQuery):
    if callback.data == "get_timetable":
        dialogs[callback.message.chat.id].get_timetable()
        await app.send_message(callback.message.chat.id, "Введите номер группы")
    if callback.data == "get_session_timetable":
        dialogs[callback.message.chat.id].get_session_timetable()
        await app.send_message(callback.message.chat.id, "Введите номер группы")


@app.on_message(filters.text & filters.private)
async def recv_timetable(client: Client, message: Message):
    if dialogs[message.chat.id].state == 'recv_timetable':
        data = get_json(message.text, is_session=False)
        if data[0] == 0:
            hash_json = hashlib.md5(str(data[1]).encode()).hexdigest()
            if operator.check_group(message.text):
                if not operator.check_hash(message.text, hash_json):
                    operator.update_record(message.text, hash_json)
                    with open(f'schedules/{message.text}.ics', 'wb') as file:
                        file.write(get_schedule(data[1]).to_ical())
            else:
                operator.add_record(message.text, hash_json)
                with open(f'schedules/{message.text}.ics', 'wb') as file:
                    file.write(get_schedule(data[1]).to_ical())
            await app.send_document(message.chat.id, f'schedules/{message.text}.ics', caption="Расписание файлом")
        elif data[0] == 2:
            await app.send_message(message.chat.id, 'Группа с таким номером не найдена')
        else:
            await app.send_message(message.chat.id, 'Неизвестная ошибка или ошибка на стороне сервера Политеха')
        dialogs[message.chat.id].to_menu()
        await menu(client, message)
    if dialogs[message.chat.id].state == 'recv_session_timetable':
        data = get_json(message.text, is_session=True)
        if data[0] == 0:
            hash_json = hashlib.md5(str(data[1]).encode()).hexdigest()
            if operator.check_group(message.text):
                if not operator.check_hash(message.text, hash_json):
                    operator.update_record(message.text, hash_json)
                    with open(f'schedules/{message.text}-session.ics', 'wb') as file:
                        file.write(get_session_schedule(data[1]).to_ical())
            else:
                operator.add_record(message.text, hash_json)
                with open(f'schedules/{message.text}-session.ics', 'wb') as file:
                    file.write(get_session_schedule(data[1]).to_ical())
            await app.send_document(message.chat.id, f'schedules/{message.text}-session.ics', caption="Расписание файлом")
        elif data[0] == 2:
            await app.send_message(message.chat.id, 'Группа с таким номером не найдена')
        else:
            await app.send_message(message.chat.id, 'Неизвестная ошибка или ошибка на стороне сервера Политеха')
        dialogs[message.chat.id].to_menu()
        await menu(client, message)


app.run()  # Automatically start() and idle()
