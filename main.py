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
        [KeyboardButton(text="➕ Добавить задачу"), KeyboardButton(text="🗑 Удалить задачу")],
        [KeyboardButton(text="✏️ Изменить задачу"), KeyboardButton(text="📋 Мои задачи")]
    ],
    resize_keyboard=True    
)



class AddTask(StatesGroup):
    get_title = State()
    get_caption = State()
    get_due_date = State()

class DeleteTask(StatesGroup):
    get_id = State()


class UpadeteTask(StatesGroup):
    get_id = State()
    get_title = State()
    get_caption = State()
    get_status = State()


class GetTask(StatesGroup):
    get_id = State()


@dp.message(F.text == "➕ Добавить задачу")
@dp.message(Command("add"))
async def add_task(message: Message, state: FSMContext):
    await message.answer("📝 Как назовём вашу задачу?")
    await state.set_state(AddTask.get_title)


@dp.message(AddTask.get_title)
async def add_caption(message: Message, state : FSMContext):
    await state.update_data(title = message.text)
    await message.answer("📌 Добавьте описание задачи:")
    await state.set_state(AddTask.get_caption)


@dp.message(AddTask.get_caption)
async def add_task(message: Message, state : FSMContext):
    await state.update_data(caption = message.text)
    await message.answer("📅 Укажите срок выполнения задачи:") 
    await state.set_state(AddTask.get_due_date)

@dp.message(AddTask.get_due_date)
async def add_due(message: Message, state: FSMContext):
    await state.update_data(due_date = message.text)
    data = await state.get_data()
    await message.answer(f"""
🗂 Ваша задача
Название: {data["title"]}
Описание: {data["caption"]}
Срок выполнения: {data["due_date"]}
""")

    created = await create_task(data["title"], data["caption"], data["due_date"], message.from_user.id)
    if not created:
        await message.answer("⚠️ Не удалось создать задачу.\n")
        return
    await message.answer("🎉 Задача успешно создана!")
    
    await state.clear()


@dp.message(F.text == "🗑 Удалить задачу")
@dp.message(Command("delete"))
async def delete_start(message: Message, state: FSMContext):
    await message.answer("🗑 Введите ID задачи, которую хотите удалить:")
    await state.set_state(DeleteTask.get_id)


@dp.message(DeleteTask.get_id)
async def delete_get_id(message: Message, state: FSMContext):
    task_id = message.text
    if not task_id.isdigit():
        
        await message.answer("⚠️ ID должен быть числом. Попробуйте ещё раз:")
        await state.clear()
        return

    
    task = await get_task_by_id(message.from_user.id, int(id))
    
    if not task:
        await message.answer("🔎 Задача с таким ID не найдена.")
        
        await state.clear()
        return
    
    if await delete_task(int(task_id), message.from_user.id):
        await message.answer("✅ Задача удалена.")
    else:
        await message.answer("⚠️ Не удалось удалить задачу. Попробуйте ещё раз.")
    
    await state.clear()


@dp.message(F.text == "✏️ Изменить задачу")
@dp.message(Command("update"))
async def update_start(message: Message, state: FSMContext):
    await message.answer("✏️ Введите ID задачи, которую хотите изменить:")

    await state.set_state(UpadeteTask.get_id)


@dp.message(UpadeteTask.get_id)
async def update_get_id(message: Message, state: FSMContext):

    task_id = message.text
    if not task_id.isdigit():
        await message.answer("⚠️ ID должен быть числом. Попробуйте ещё раз:")
        return

    
    task = await get_task_by_id(message.from_user.id, int(message.text))

    if not task:
        await message.answer("🔎 Задача с таким ID не найдена.")
        await state.clear()
        return
    
    await state.update_data(id = int(message.text))

    await message.answer("📝 Введите новое название задачи:")
    await state.set_state(UpadeteTask.get_title)






@dp.message(UpadeteTask.get_title)
async def update_get_title(message: Message, state: FSMContext):
    await state.update_data(title = message.text)
    await message.answer("📌 Введите новое описание задачи:")

    await state.set_state(UpadeteTask.get_caption)


@dp.message(UpadeteTask.get_caption)
async def update_get_caption(message: Message, state: FSMContext):
    await state.update_data(caption=message.text)
    await message.answer("""
Укажите новый статус задачи:
1 — выполнена
0 — не выполнена
Любой другой текст — оставить текущий статус.
        """
    )

    await state.set_state(UpadeteTask.get_status)


@dp.message(UpadeteTask.get_status)
async def update_get_status(message: Message, state: FSMContext):
    status_text = (message.text or "").strip()
    data = await state.get_data()
    task = await get_task_by_id(message.from_user.id, data["id"])
    if not task:
        await message.answer("🔎 Задача не найдена. Начните изменение заново.")
        await state.clear()
        return


    status = (status_text == "1") if status_text in ("0", "1") else task["status"]
    updated = await update_task(data["title"], data["caption"], task["due_date"], status, message.from_user.id, data["id"])

    if updated:
        await message.answer("✅ Изменения сохранены!")
    else:
        await message.answer("⚠️ Не удалось сохранить изменения. Попробуйте ещё раз.")


    await state.clear()


@dp.message(Command("my_task"))
async def my_task(message: Message, state: FSMContext):
    await message.answer("🔎 Введите ID задачи, которую хотите посмотреть:")
    await state.set_state(GetTask.get_id)


@dp.message(GetTask.get_id)
async def my_task_get_id(message: Message, state: FSMContext):

    await state.update_data(id = message.text)
    task_id = message.text
    if not task_id.isdigit():
        await message.answer("⚠️ ID должен быть числом. Попробуйте ещё раз:")
        return

    
    task = await get_task_by_id(message.from_user.id, int(id))

    if not task:
        await message.answer("🔎 Задача с таким ID не найдена.")
        await state.clear()
        return

    
    await message.answer(f"""
📋 Задача №{task["id"]}
Название: {task["title"]}
Описание: {task["caption"]}
Срок выполнения: {task["due_date"] or "—"}
Статус: {"✅ Выполнена" if task["status"] else "⏳ Не выполнена"}
Создана: {task["created_at"]}
""")
    await state.clear()





@dp.message(F.text == "📋 Мои задачи")
@dp.message(Command("my_tasks"))
async def my_tasks(message: Message):
    tasks = await get_tasks(message.from_user.id)
    if not tasks:
        await message.answer("📭 У вас пока нет задач. Нажмите «➕ Добавить задачу», чтобы создать первую!")
        return
    text = "📋 Ваши задачи\n"

    for task in tasks:
        text += f"""
🆔 ID: {task['id']}
Название: {task['title']}
Описание: {task['caption']}
Статус: {"✅ Выполнена" if task["status"] else "⏳ Не выполнена"}
Создана: {task["created_at"]}"""
        
    await message.answer(text)


@dp.message(Command("start"))
async def start(message: Message):
    user = message.from_user
    is_indb = await profile(message.from_user.id)
    if is_indb:
        await message.answer(f"🎉 С возвращением, {user.full_name}!\n\nЧто будем планировать сегодня?", reply_markup=main_kb)
        return

    await create_user(user.username, user.full_name, user.id)
    await message.answer(f"""
👋 Добро пожаловать, {user.full_name}! 
✨ Здесь вы можете создавать задачи, следить за сроками и отмечать выполненное.
""", reply_markup=main_kb)




async def  main():
    print("Bot started!")
    await create_tables()
    await dp.start_polling(bot)
    
    
if __name__ == "__main__":
    asyncio.run(main())