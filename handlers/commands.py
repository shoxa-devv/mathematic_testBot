"""Komanda handlerlari"""
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from keyboards.inline import get_main_menu_keyboard, get_registration_keyboard
from utils.helpers import is_admin, is_user_blocked

def register_commands(dp, bot, db):
    """Komandalarni ro'yxatdan o'tkazish"""
    
    @dp.message(Command("start"))
    async def cmd_start(message: Message, state: FSMContext):
        user_id = message.from_user.id
        
        # Bloklangan tekshirish
        if is_user_blocked(user_id):
            await message.answer("❌ Siz botdan bloklangansiz!")
            return
        
        # Foydalanuvchini bazaga qo'shish
        db.add_user(
            user_id=user_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name
        )
        
        # Ro'yxatdan o'tganligini tekshirish
        is_user_admin = is_admin(user_id)
        if not db.is_user_registered(user_id):
            await message.answer(
                "👋 Salom! Botdan foydalanish uchun ro'yxatdan o'ting.",
                reply_markup=get_registration_keyboard()
            )
        else:
            await message.answer(
                "👋 Salom! Matematik testlar botiga xush kelibsiz!\n\nAsosiy menyu:",
                reply_markup=get_main_menu_keyboard(is_user_admin)
            )
        
        await state.clear()
    
    @dp.message(Command("admin"))
    async def cmd_admin(message: Message):
        from keyboards.inline import get_admin_panel_keyboard
        
        if not is_admin(message.from_user.id):
            await message.answer("❌ Siz admin emassiz!")
            return
        
        await message.answer(
            "🔐 Admin Panel\n\nQuyidagilardan birini tanlang:",
            reply_markup=get_admin_panel_keyboard()
        )
