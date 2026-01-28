"""Asosiy bot fayli - barcha handlerlarni birlashtiradi"""
import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, ADMIN_ID
from database import Database
from utils.helpers import init_ocr, set_db_instance
from handlers import commands, inline_handlers, message_handlers, admin_handlers

# Logging sozlamalari
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot va Dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
db = Database()

# Database instance ni helpers ga o'rnatish
set_db_instance(db)

# Birinchi adminni qo'shish
if ADMIN_ID > 0:
    db.add_admin(ADMIN_ID, "Admin", "Admin")

# OCR ni ishga tushirish
init_ocr()

# Handlerlarni ro'yxatdan o'tkazish
commands.register_commands(dp, bot, db)
inline_handlers.register_inline_handlers(dp, bot, db)
message_handlers.register_message_handlers(dp, bot, db)
admin_handlers.register_admin_handlers(dp, bot, db)


# Botni ishga tushirish
async def main():
    os.makedirs("tests", exist_ok=True)
    logger.info("Bot ishga tushmoqda...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
