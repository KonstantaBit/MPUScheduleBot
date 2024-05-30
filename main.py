from pyrogram import Client, filters
from dotenv import load_dotenv
from os import getenv
from pyrogram.types import Message, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery


load_dotenv()

api_id = getenv("api_id")
api_hash = getenv("api_hash")
bot_token = getenv("bot_token")

app = Client("my_account", api_id=api_id, api_hash=api_hash, bot_token=bot_token)


@app.on_message(filters.text & filters.private & filters.command("start"))
async def start(client, message):
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
                        "Посмотреть список общедоступный расписаний",
                        callback_data="get_timetable",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Создать СВОё общедоступное расписание",
                        callback_data="get_timetable",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Редактировать расписание",
                        callback_data="get_timetable",
                    ),
                ],
            ]
        )
    )


@app.on_callback_query()
async def get_timetable(client: Client, callback: CallbackQuery):
    if callback.data == "get_timetable":
        print(callback.message.chat.id)
        await app.send_message(callback.message.chat.id, "Введите номер группы")
        # тут юзер вводит номер группы


app.run()  # Automatically start() and idle()
