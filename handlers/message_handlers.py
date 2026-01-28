"""Message handlerlari (oddiy buttonlar)"""
from aiogram import F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.inline import get_main_menu_keyboard, get_registration_keyboard, get_categories_keyboard
from keyboards.reply import get_phone_keyboard
from utils.helpers import is_admin, is_user_blocked
from utils.states import RegistrationStates

def register_message_handlers(dp, bot, db):
    """Message handlerlarni ro'yxatdan o'tkazish"""
    
    # Ro'yxatdan o'tish - ism va familiya
    @dp.message(RegistrationStates.waiting_for_full_name)
    async def process_full_name(message: Message, state: FSMContext):
        full_name = message.text.strip()
        parts = full_name.split(maxsplit=1)
        
        if len(parts) < 2:
            await message.answer("❌ Ism va familiyani to'liq yuboring (masalan: Aliyev Vali):")
            return
        
        first_name = parts[0]
        last_name = parts[1]
        
        await state.update_data(first_name=first_name, last_name=last_name)
        await state.set_state(RegistrationStates.waiting_for_phone)
        await message.answer(
            "✅ Ism va familiya qabul qilindi!\n\n"
            "Telefon raqamingizni yuboring:",
            reply_markup=get_phone_keyboard()
        )
    
    # Ro'yxatdan o'tish - telefon raqami
    @dp.message(RegistrationStates.waiting_for_phone, F.contact)
    async def process_phone_contact(message: Message, state: FSMContext):
        phone = message.contact.phone_number
        if not phone:
            await message.answer("❌ Telefon raqami topilmadi! Qayta yuboring:", reply_markup=get_phone_keyboard())
            return
        
        data = await state.get_data()
        db.add_user_profile(
            user_id=message.from_user.id,
            first_name=data['first_name'],
            last_name=data['last_name'],
            middle_name=None,
            phone_number=phone
        )
        
        is_user_admin = is_admin(message.from_user.id)
        await message.answer(
            "✅ Ro'yxatdan muvaffaqiyatli o'tdingiz!",
            reply_markup=get_main_menu_keyboard(is_user_admin)
        )
        await state.clear()
