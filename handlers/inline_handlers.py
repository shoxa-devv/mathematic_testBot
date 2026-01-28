"""Inline keyboard handlerlari"""
from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.inline import (
    get_main_menu_keyboard, get_registration_keyboard, get_categories_keyboard,
    get_back_to_main_keyboard, get_admin_panel_keyboard, get_test_keyboard
)
from utils.helpers import is_admin, is_user_blocked
from utils.states import RegistrationStates, TestTakingStates

def register_inline_handlers(dp, bot, db):
    """Inline handlerlarni ro'yxatdan o'tkazish"""
    
    # Ro'yxatdan o'tish
    @dp.callback_query(F.data == "register")
    async def start_registration(callback: CallbackQuery, state: FSMContext):
        await state.set_state(RegistrationStates.waiting_for_full_name)
        await callback.message.edit_text(
            "📝 Ro'yxatdan o'tish\n\n"
            "Ism va familiyangizni birga yuboring (masalan: Aliyev Vali):"
        )
        await callback.answer()
    
    # Asosiy menyu funksiyalari
    @dp.callback_query(F.data == "take_test")
    async def start_test_taking(callback: CallbackQuery, state: FSMContext):
        user_id = callback.from_user.id
        
        if is_user_blocked(user_id):
            await callback.answer("❌ Siz botdan bloklangansiz!", show_alert=True)
            return
        
        if not db.is_user_registered(user_id):
            await callback.message.edit_text(
                "❌ Test topshirish uchun avval ro'yxatdan o'ting!",
                reply_markup=get_registration_keyboard()
            )
            await callback.answer()
            return
        
        categories = db.get_all_categories()
        if not categories:
            await callback.message.edit_text("❌ Hozircha kategoriyalar mavjud emas!")
            await callback.answer()
            return
        
        await callback.message.edit_text(
            "📚 Test kategoriyasini tanlang:",
            reply_markup=get_categories_keyboard(categories)
        )
        await callback.answer()
    
    @dp.callback_query(F.data == "support")
    async def support(callback: CallbackQuery):
        text = (
            "💬 Qo'llab-quvvatlash\n\n"
            "Savollaringiz bo'lsa, adminlarga murojaat qiling:\n"
            "Telegram: @shoxa_devv"
        )
        await callback.message.edit_text(text, reply_markup=get_back_to_main_keyboard())
        await callback.answer()
    
    @dp.callback_query(F.data == "about")
    async def about_bot(callback: CallbackQuery):
        text = (
            "ℹ️ Bot haqida\n\n"
            "Bu matematik testlar boti. Siz bu yerda turli darajadagi "
            "matematik testlarni topshirishingiz mumkin."
        )
        await callback.message.edit_text(text, reply_markup=get_back_to_main_keyboard())
        await callback.answer()
    
    # Asosiy menyuga qaytish
    @dp.callback_query(F.data == "back_to_main")
    async def back_to_main_callback(callback: CallbackQuery, state: FSMContext):
        is_user_admin = is_admin(callback.from_user.id)
        await callback.message.edit_text(
            "🏠 Asosiy menyu:",
            reply_markup=get_main_menu_keyboard(is_user_admin)
        )
        await state.clear()
        await callback.answer()
    
    # Admin panel
    @dp.callback_query(F.data == "admin_panel")
    async def admin_panel_callback(callback: CallbackQuery, state: FSMContext):
        if not is_admin(callback.from_user.id):
            await callback.answer("❌ Siz admin emassiz!", show_alert=True)
            return
        
        await callback.message.edit_text(
            "🔐 Admin Panel\n\nQuyidagilardan birini tanlang:",
            reply_markup=get_admin_panel_keyboard()
        )
        await state.clear()
        await callback.answer()
    
    # Kategoriya tanlash
    @dp.callback_query(F.data.startswith("category_"))
    async def select_category(callback: CallbackQuery, state: FSMContext):
        category_id = int(callback.data.split("_")[1])
        category = db.get_category(category_id)
        
        if not category:
            await callback.answer("❌ Kategoriya topilmadi!", show_alert=True)
            return
        
        # Testlarni olish (20 ta)
        tests = db.get_tests_by_category(category_id, limit=20)
        
        if not tests:
            await callback.message.edit_text(
                f"❌ {category['category_name']} kategoriyasida testlar mavjud emas!",
                reply_markup=get_back_to_main_keyboard()
            )
            await callback.answer()
            return
        
        # Test ishlashni boshlash
        await state.update_data(
            category_id=category_id,
            tests=tests,
            current_question=0,
            answers={}
        )
        await state.set_state(TestTakingStates.taking_test)
        
        # Birinchi testni ko'rsatish
        from utils.test_logic import show_test_question
        await show_test_question(callback.message, tests[0], 0, len(tests), bot, db)
        await callback.answer()
    
    @dp.callback_query(F.data.startswith("test_answer_"), TestTakingStates.taking_test)
    async def process_test_answer(callback: CallbackQuery, state: FSMContext):
        from utils.test_logic import show_test_question, finish_test
        
        data = await state.get_data()
        tests = data['tests']
        current_question = data['current_question']
        answers = data.get('answers', {})
        
        # Javobni saqlash
        parts = callback.data.split("_")
        test_id = int(parts[2])
        user_answer = parts[3]
        
        test = next((t for t in tests if t['test_id'] == test_id), None)
        if test:
            is_correct = user_answer.lower() == test['correct_answer'].lower()
            answers[test_id] = {
                'user_answer': user_answer,
                'is_correct': is_correct
            }
        
        # Keyingi savol
        current_question += 1
        
        if current_question < len(tests):
            await state.update_data(current_question=current_question, answers=answers)
            await show_test_question(callback.message, tests[current_question], current_question, len(tests), bot, db)
            await callback.answer()
        else:
            # Test yakunlandi
            await state.update_data(answers=answers)
            await finish_test(callback.message, state, tests, answers, bot, db)
            await callback.answer()
