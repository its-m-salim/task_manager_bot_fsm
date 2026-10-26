from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.filters import Command
from dotenv import load_dotenv
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from service import *
from connection import *
import os
import asyncio


load_dotenv()

token = os.getenv("BOT_TOKEN")


bot = Bot(token=token)

dp = Dispatcher()


main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Add task"), KeyboardButton(text="delete task")],
        [KeyboardButton(text="update")]
    ],
    resize_keyboard=True
)



class AddTask(StatesGroup):
    get_title = State()
    get_caption = State()

class DeleteTask(StatesGroup):
    get_id = State()


class UpadeteTask(StatesGroup):
    get_id = State()
    get_title = State()
    get_caption = State()


@dp.message(F.text == "Add task")
@dp.message(Command("add"))
async def add_task(message: Message, state: FSMContext):
    await message.answer("Введите имя таска: ")
    await state.set_state(AddTask.get_title)


@dp.message(AddTask.get_title)
async def add_caption(message: Message, state : FSMContext):
    await state.update_data(title = message.text)
    await message.answer("Введите описания для таска: ")
    await state.set_state(AddTask.get_caption)


@dp.message(AddTask.get_caption)
async def add_task(message: Message, state : FSMContext):
    await state.update_data(caption = message.text)
    data = await state.get_data()
    await message.answer(f"""
Your task
Title: {data["title"]}
Caption: {data["caption"]}
""")
    await state.clear()


@dp.message(Command("start"))
async def start(message: Message):
    user = message.from_user
    is_indb = await profile(message.from_user.id)
    if is_indb:
        await message.answer(f"С Возвпащением, {user.full_name}", reply_markup=main_kb)
        return

    await create_user(user.username, user.full_name, user.id)
    await message.answer(f"""
Привет, {user.full_name} 
Этот бот предназначен для управления задачами
""")




async def  main():
    print("Bot started!")
    await create_tables()
    await dp.start_polling(bot)
    
    
if __name__ == "__main__":
    asyncio.run(main())