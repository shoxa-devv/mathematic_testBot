"""Test logic utility functions"""
import os
import logging
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from keyboards.inline import get_test_keyboard, get_main_menu_keyboard
from utils.helpers import is_admin

logger = logging.getLogger(__name__)

async def show_test_question(message: Message, test: dict, question_num: int, total: int, bot, db):
    """Test savolini ko'rsatish"""
    has_option_d = test.get('option_d') and test.get('option_d') != ""
    
    question_text = test.get('question_text', '')
    question_image = test.get('question_image')
    
    caption = f"❓ Savol {question_num + 1}/{total}\n\n"
    if question_text:
        caption += f"{question_text}\n\n"
    
    # Faqat testda matnli variantlar bo'lsa ko'rsatamiz
    if test.get('option_a'):
        caption += f"A) {test['option_a']}\n"
        caption += f"B) {test['option_b']}\n"
        caption += f"C) {test['option_c']}\n"
        if has_option_d:
            caption += f"D) {test['option_d']}\n"
    else:
        # Variantlar rasmda bo'lsa
        caption += "Variantlarni rasmda ko'ring va tegishli tugmani bosing."
    
    try:
        if question_image and os.path.exists(question_image):
            photo = FSInputFile(question_image)
            await message.answer_photo(
                photo=photo,
                caption=caption,
                reply_markup=get_test_keyboard(test['test_id'], question_num + 1, total, has_option_d)
            )
        else:
            await message.answer(
                caption,
                reply_markup=get_test_keyboard(test['test_id'], question_num + 1, total, has_option_d)
            )
    except Exception as e:
        logger.error(f"Xatolik: {e}")
        await message.answer(
            caption,
            reply_markup=get_test_keyboard(test['test_id'], question_num + 1, total, has_option_d)
        )

async def finish_test(message: Message, state: FSMContext, tests: list, answers: dict, bot, db):
    """Testni yakunlash"""
    data = await state.get_data()
    category_id = data['category_id']
    user_id = message.from_user.id
    
    # Natijalarni hisoblash
    total = len(tests)
    correct = sum(1 for ans in answers.values() if ans['is_correct'])
    percentage = (correct / total * 100) if total > 0 else 0
    
    # Natijani saqlash
    result_id = db.save_test_result(user_id, category_id, total, correct, percentage)
    
    # Har bir javobni saqlash
    for test in tests:
        test_id = test['test_id']
        if test_id in answers:
            db.save_test_answer(
                result_id, test_id,
                answers[test_id]['user_answer'],
                answers[test_id]['is_correct']
            )
    
    # Natijani ko'rsatish (foiz bilan)
    category = db.get_category(category_id) if category_id else None
    result_text = "✅ Test yakunlandi!\n\n"
    if category:
        result_text += f"📚 Kategoriya: {category['category_name']}\n"
    result_text += f"📊 To'g'ri javoblar: {correct}/{total}\n"
    result_text += f"📈 Natija: {percentage:.1f}%\n\n"
    result_text += "📝 Tafsilotlar:\n"
    
    # Tafsilotlarni ko'rsatish
    for i, test in enumerate(tests, 1):
        test_id = test['test_id']
        if test_id in answers:
            ans = answers[test_id]
            status = "✅" if ans['is_correct'] else "❌"
            result_text += f"{i}. {status} Sizning javob: {ans['user_answer'].upper()}, "
            result_text += f"To'g'ri javob: {test['correct_answer'].upper()}\n"
    
    is_user_admin = is_admin(user_id)
    await message.answer(result_text, reply_markup=get_main_menu_keyboard(is_user_admin))
    
    # Adminlarga xabar yuborish (har bir foydalanuvchining natijasi)
    profile = db.get_user_profile(user_id)
    if profile:
        user_name = f"{profile['first_name']} {profile['last_name']}"
        username_text = f"@{message.from_user.username}" if message.from_user.username else "Username yo'q"
        
        admin_message = (
            f"📢 Yangi test natijasi!\n\n"
            f"👤 Foydalanuvchi: {user_name}\n"
            f"📱 Username: {username_text}\n"
        )
        if category:
            admin_message += f"📚 Kategoriya: {category['category_name']}\n"
        admin_message += (
            f"📊 To'g'ri javoblar: {correct}/{total}\n"
            f"📈 Natija: {percentage:.1f}%"
        )
        
        try:
            admins = db.get_all_admins()
            for admin in admins:
                try:
                    await bot.send_message(admin['admin_id'], admin_message)
                except Exception as e:
                    logger.error(f"Adminga ({admin['admin_id']}) xabar yuborishda xatolik: {e}")
        except Exception as e:
             logger.error(f"Adminlarni olishda yoki xabar yuborishda umumiy xatolik: {e}")

    await state.clear()
