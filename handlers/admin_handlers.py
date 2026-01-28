"""Admin handlerlari"""
from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import os
import logging

from keyboards.inline import (
    get_admin_panel_keyboard, get_level_selection_keyboard, get_delete_test_keyboard,
    get_back_to_admin_keyboard, get_admin_stats_keyboard, get_admin_keyboard,
    get_categories_keyboard, get_admin_categories_keyboard
)
from utils.helpers import is_admin, process_image_with_ocr, extract_options_from_text
from utils.states import (
    AddTestStates, BlockUserStates, UnblockUserStates, BroadcastStates, AddCategoryStates
)

logger = logging.getLogger(__name__)

def register_admin_handlers(dp, bot, db):
    """Admin handlerlarni ro'yxatdan o'tkazish"""
    


    # Test qo'shish
    @dp.callback_query(F.data == "admin_add_test")
    async def admin_add_test_start(callback: CallbackQuery, state: FSMContext):
        if not is_admin(callback.from_user.id):
            await callback.answer("❌ Siz admin emassiz!", show_alert=True)
            return
        
        await state.set_state(AddTestStates.waiting_for_image)
        await callback.message.edit_text(
            "➕ Test qo'shish\n\n"
            "Testni rasm yoki matn shaklida yuboring:\n"
            "📷 Rasm yuborsangiz - bot avtomatik textga aylantiradi\n"
            "📝 Matn yuborsangiz - to'g'ridan-to'g'ri qabul qilinadi\n\n"
            "Rasm yoki matnni yuboring:"
        )
        await callback.answer()
    
    # Rasm qabul qilish
    @dp.message(AddTestStates.waiting_for_image, F.photo)
    async def process_test_image(message: Message, state: FSMContext):
        if not is_admin(message.from_user.id):
            await message.answer("❌ Siz admin emassiz!")
            return
        
        photo = message.photo[-1]
        file = await bot.get_file(photo.file_id)
        file_path = f"tests/{photo.file_id}.jpg"
        
        os.makedirs("tests", exist_ok=True)
        await bot.download_file(file.file_path, file_path)
        
        await message.answer("⏳ Rasm tahlil qilinmoqda...")
        
        ocr_text = await process_image_with_ocr(file_path)
        
        # Validatsiya: Rasmdan matn topildimi?
        if not ocr_text or len(ocr_text.strip()) < 10:
            # Faylni o'chirish
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logger.error(f"Fayl o'chirishda xatolik: {e}")
                
            await message.answer(
                "❌ Rasmdan test topilmadi!\n"
                "Iltimos, qayta rasm yuboring yoki matn shaklida yuboring."
            )
            # State o'zgarmaydi (waiting_for_image da qoladi)
            return

        # Agar validatsiyadan o'tsa
        await state.update_data(question_image=file_path, question_text=ocr_text)
        
        # Variantlarni avtomatik ajratib olish
        options = extract_options_from_text(ocr_text)
        
        if len(options) >= 3:
            await state.update_data(
                option_a=options.get('A', ''),
                option_b=options.get('B', ''),
                option_c=options.get('C', ''),
                option_d=options.get('D', '')
            )
            
            text = "✅ Rasm textga aylantirildi!\n\n"
            text += f"📝 Savol: {ocr_text[:200]}...\n\n" if len(ocr_text) > 200 else f"📝 Savol: {ocr_text}\n\n"
            text += f"A) {options.get('A', 'Topilmadi')}\n"
            text += f"B) {options.get('B', 'Topilmadi')}\n"
            text += f"C) {options.get('C', 'Topilmadi')}\n"
            if 'D' in options:
                text += f"D) {options.get('D', 'Topilmadi')}\n"
            text += "\n✅ Variantlar avtomatik topildi!\n\n"
            text += "Endi to'g'ri javobni yuboring (a, b, c yoki d):"
            
            await state.set_state(AddTestStates.waiting_for_correct_answer)
            await message.answer(text)
        else:
            await message.answer(
                "✅ Rasm qabul qilindi!\n\n"
                "⚠️ Variantlar avtomatik topilmadi.\n"
                "Endi javoblarni quyidagi formatda yuboring:\n"
                "1.a 2.b 3.c ...\n\n"
                "Javoblar soni rasmda nechta savol bo'lsa shuncha bo'lishi kerak."
            )
            await state.set_state(AddTestStates.waiting_for_answers)
    
    # Matn qabul qilish (rasm emas)
    @dp.message(AddTestStates.waiting_for_image, ~F.photo)
    async def process_test_text(message: Message, state: FSMContext):
        if not is_admin(message.from_user.id):
            await message.answer("❌ Siz admin emassiz!")
            return
        
        text = message.text.strip()
        
        if len(text) < 10:
            await message.answer("❌ Matn juda qisqa! Iltimos, to'liq test matnini yuboring.")
            return
        
        await state.update_data(question_text=text, question_image=None)
        
        # Variantlarni avtomatik ajratib olish
        options = extract_options_from_text(text)
        
        if len(options) >= 3:
            await state.update_data(
                option_a=options.get('A', ''),
                option_b=options.get('B', ''),
                option_c=options.get('C', ''),
                option_d=options.get('D', '')
            )
            
            result_text = "✅ Test matni qabul qilindi!\n\n"
            result_text += f"📝 Savol: {text[:200]}...\n\n" if len(text) > 200 else f"📝 Savol: {text}\n\n"
            result_text += f"A) {options.get('A', 'Topilmadi')}\n"
            result_text += f"B) {options.get('B', 'Topilmadi')}\n"
            result_text += f"C) {options.get('C', 'Topilmadi')}\n"
            if 'D' in options:
                result_text += f"D) {options.get('D', 'Topilmadi')}\n"
            result_text += "\n✅ Variantlar avtomatik topildi!\n\n"
            result_text += "Endi to'g'ri javobni yuboring (a, b, c yoki d):"
            
            await state.set_state(AddTestStates.waiting_for_correct_answer)
            await message.answer(result_text)
        else:
            await message.answer(
                "✅ Test matni qabul qilindi!\n\n"
                "⚠️ Variantlar avtomatik topilmadi.\n"
                "Endi A variantini yuboring:"
            )
            await state.set_state(AddTestStates.waiting_for_option_a)

    @dp.message(AddTestStates.waiting_for_answers)
    async def process_test_answers(message: Message, state: FSMContext):
        import re
        text = message.text.lower()
        
        # Javoblarni ajratib olish (masalan: 1.a 2.b)
        matches = re.findall(r'(\d+)\.?\s*([a-d])', text)
        
        if not matches:
            await message.answer(
                "❌ Javoblar formati noto'g'ri!\n"
                "Iltimos, bunday ko'rinishda yuboring: 1.a 2.b 3.c"
            )
            return
        
        # Tartib bo'yicha saralash
        matches.sort(key=lambda x: int(x[0]))
        
        answers = [m[1] for m in matches]
        
        await state.update_data(answers=answers)
        
        # Kategoriyalarni olish
        categories = db.get_all_categories()
        if not categories:
            await message.answer(
                "❌ Hozircha kategoriyalar mavjud emas!\n"
                "Avval kategoriya qo'shing yoki kategoriya qo'shish uchun /admin_categories buyrug'ini bosing.",
                reply_markup=get_admin_panel_keyboard()
            )
            await state.clear()
            return

        await message.answer(
            f"✅ {len(answers)} ta javob qabul qilindi: {', '.join(answers)}\n\n"
            "Endi test kategoriyasini tanlang:",
            reply_markup=get_categories_keyboard(categories, for_admin=True)
        )
        await state.set_state(AddTestStates.waiting_for_test_category)
    
    # To'g'ri javobni qabul qilish (bitta test uchun)
    @dp.message(AddTestStates.waiting_for_correct_answer)
    async def process_correct_answer(message: Message, state: FSMContext):
        answer = message.text.strip().lower()
        
        if answer not in ['a', 'b', 'c', 'd']:
            await message.answer("❌ To'g'ri javob a, b, c yoki d bo'lishi kerak!")
            return
        
        await state.update_data(correct_answer=answer)
        
        # Kategoriyalarni olish
        categories = db.get_all_categories()
        if not categories:
            await message.answer(
                "❌ Hozircha kategoriyalar mavjud emas!\n"
                "Avval kategoriya qo'shing yoki kategoriya qo'shish uchun /admin_categories buyrug'ini bosing.",
                reply_markup=get_admin_panel_keyboard()
            )
            await state.clear()
            return
        
        await message.answer(
            f"✅ To'g'ri javob: {answer.upper()}\n\n"
            "Endi test kategoriyasini tanlang:",
            reply_markup=get_categories_keyboard(categories, for_admin=True)
        )
        await state.set_state(AddTestStates.waiting_for_test_category)

    @dp.callback_query(F.data.startswith("admin_select_category_"), AddTestStates.waiting_for_test_category)
    async def add_test_category_selected(callback: CallbackQuery, state: FSMContext):
        if not is_admin(callback.from_user.id):
            await callback.answer("❌ Siz admin emassiz!", show_alert=True)
            return
        
        try:
            category_id = int(callback.data.split("_")[3])
        except (ValueError, IndexError):
            await callback.answer("❌ Xatolik: Noto'g'ri kategoriya ID!", show_alert=True)
            await callback.message.edit_text(
                "❌ Xatolik yuz berdi!\n\nQayta urinib ko'ring:",
                reply_markup=get_admin_panel_keyboard()
            )
            await state.clear()
            return
        category = db.get_category(category_id)
        
        # Kategoriya topilganini tekshirish
        if not category:
            # Debug: kategoriyalarni ko'rsatish
            all_categories = db.get_all_categories()
            debug_text = f"❌ Kategoriya topilmadi! (ID: {category_id})\n\n"
            if all_categories:
                debug_text += "Mavjud kategoriyalar:\n"
                for cat in all_categories:
                    debug_text += f"- ID: {cat['category_id']}, Nomi: {cat['category_name']}\n"
            else:
                debug_text += "⚠️ Hozircha kategoriyalar mavjud emas!\n"
                debug_text += "Iltimos, avval kategoriya qo'shing."
            
            await callback.answer("❌ Kategoriya topilmadi!", show_alert=True)
            await callback.message.edit_text(
                debug_text,
                reply_markup=get_admin_panel_keyboard()
            )
            await state.clear()
            return
        
        # Oson/O'rtacha/Qiyin map qilish
        level_map = {
            "oson": "easy",
            "o'rtacha": "medium",
            "qiyin": "hard"
        }
        level = level_map.get(category['category_name'].lower(), "easy")
        
        data = await state.get_data()
        answers = data.get('answers', [])
        image_path = data.get('question_image')
        question_text = data.get('question_text', '')
        option_a = data.get('option_a', '')
        option_b = data.get('option_b', '')
        option_c = data.get('option_c', '')
        option_d = data.get('option_d', '')
        correct_answer = data.get('correct_answer', '')
        
        # Agar bir nechta javob bo'lsa (ko'p test)
        if answers:
            count = 0
            for i, ans in enumerate(answers, 1):
                db.add_test(
                    category_id=category_id,
                    level=level,
                    question_text=f"Savol {i}",
                    question_image=image_path,
                    option_a="",
                    option_b="",
                    option_c="",
                    option_d="",
                    correct_answer=ans
                )
                count += 1
            
            await callback.message.edit_text(
                f"✅ {count} ta test muvaffaqiyatli qo'shildi!\n"
                f"Kategoriya: {category['category_name']}",
                reply_markup=get_admin_panel_keyboard()
            )
        # Agar bitta test bo'lsa
        elif correct_answer:
            test_id = db.add_test(
                category_id=category_id,
                level=level,
                question_text=question_text,
                question_image=image_path,
                option_a=option_a,
                option_b=option_b,
                option_c=option_c,
                option_d=option_d,
                correct_answer=correct_answer
            )
            
            await callback.message.edit_text(
                f"✅ Test muvaffaqiyatli qo'shildi!\n"
                f"Test ID: {test_id}\n"
                f"Kategoriya: {category['category_name']}",
                reply_markup=get_admin_panel_keyboard()
            )
        else:
            await callback.message.edit_text(
                "❌ Xatolik: Test ma'lumotlari topilmadi!",
                reply_markup=get_admin_panel_keyboard()
            )
        
        await state.clear()
        await callback.answer()


    
    # Test o'chirish
    @dp.callback_query(F.data == "admin_delete_test")
    async def admin_delete_test_callback(callback: CallbackQuery):
        if not is_admin(callback.from_user.id):
            await callback.answer("❌ Siz admin emassiz!", show_alert=True)
            return
        
        tests = db.get_all_tests()
        if not tests:
            await callback.message.edit_text(
                "❌ Hozircha testlar mavjud emas!",
                reply_markup=get_admin_panel_keyboard()
            )
            await callback.answer()
            return
        
        await callback.message.edit_text(
            "🗑️ Test o'chirish\n\nO'chirmoqchi bo'lgan testni tanlang:",
            reply_markup=get_delete_test_keyboard(tests)
        )
        await callback.answer()
    
    @dp.callback_query(F.data.startswith("delete_test_"))
    async def delete_test_confirm(callback: CallbackQuery):
        if not is_admin(callback.from_user.id):
            await callback.answer("❌ Siz admin emassiz!", show_alert=True)
            return
        
        test_id = int(callback.data.split("_")[2])
        deleted = db.delete_test(test_id)
        
        if deleted:
            await callback.answer("✅ Test o'chirildi!", show_alert=True)
            await callback.message.edit_text(
                "✅ Test muvaffaqiyatli o'chirildi!",
                reply_markup=get_admin_panel_keyboard()
            )
        else:
            await callback.answer("❌ Test topilmadi!", show_alert=True)
    
    # Bloklash
    @dp.callback_query(F.data == "admin_block_user")
    async def admin_block_user_callback(callback: CallbackQuery, state: FSMContext):
        if not is_admin(callback.from_user.id):
            await callback.answer("❌ Siz admin emassiz!", show_alert=True)
            return
        
        await state.set_state(BlockUserStates.waiting_for_username)
        await callback.message.edit_text(
            "🚫 Foydalanuvchini bloklash\n\n"
            "Foydalanuvchi username ni yuboring (masalan: @username yoki username):"
        )
        await callback.answer()
    
    @dp.message(BlockUserStates.waiting_for_username)
    async def process_block_username(message: Message, state: FSMContext):
        username = message.text.strip().lstrip('@')
        blocked = db.block_user(username=username, reason="Admin tomonidan bloklangan")
        
        if blocked:
            await message.answer(
                f"✅ Foydalanuvchi bloklandi! (Username: @{username})",
                reply_markup=get_admin_panel_keyboard()
            )
        else:
            await message.answer(
                f"❌ Foydalanuvchi topilmadi! (Username: @{username})",
                reply_markup=get_admin_panel_keyboard()
            )
        await state.clear()
    
    # Blokdan chiqarish
    @dp.callback_query(F.data == "admin_unblock_user")
    async def admin_unblock_user_callback(callback: CallbackQuery, state: FSMContext):
        if not is_admin(callback.from_user.id):
            await callback.answer("❌ Siz admin emassiz!", show_alert=True)
            return
        
        await state.set_state(UnblockUserStates.waiting_for_username)
        await callback.message.edit_text(
            "✅ Foydalanuvchini blokdan chiqarish\n\n"
            "Foydalanuvchi username ni yuboring (masalan: @username yoki username):"
        )
        await callback.answer()
    
    @dp.message(UnblockUserStates.waiting_for_username)
    async def process_unblock_username(message: Message, state: FSMContext):
        username = message.text.strip().lstrip('@')
        unblocked = db.unblock_user(username=username)
        
        if unblocked:
            await message.answer(
                f"✅ Foydalanuvchi blokdan chiqarildi! (Username: @{username})",
                reply_markup=get_admin_panel_keyboard()
            )
        else:
            await message.answer(
                f"❌ Foydalanuvchi topilmadi yoki bloklanmagan! (Username: @{username})",
                reply_markup=get_admin_panel_keyboard()
            )
        await state.clear()
    
    # Statistika
    @dp.callback_query(F.data == "admin_stats")
    async def admin_stats(callback: CallbackQuery):
        if not is_admin(callback.from_user.id):
            await callback.answer("❌ Siz admin emassiz!", show_alert=True)
            return
        
        await callback.message.edit_text(
            "📊 Statistika",
            reply_markup=get_admin_stats_keyboard()
        )
        await callback.answer()
    
    @dp.callback_query(F.data.startswith("stats_test_"))
    async def show_test_stats(callback: CallbackQuery):
        if not is_admin(callback.from_user.id):
            await callback.answer("❌ Siz admin emassiz!", show_alert=True)
            return
        
        period = callback.data.split("_")[2]
        count = db.get_user_stats(period)
        
        period_names = {
            "week": "1 Hafta",
            "month": "1 Oy",
            "year": "1 Yil"
        }
        
        await callback.message.edit_text(
            f"📊 Botga kirgan foydalanuvchilar: {period_names.get(period, period)}\n\n"
            f"👥 Soni: {count}",
            reply_markup=get_admin_stats_keyboard()
        )
        await callback.answer()
    
    @dp.callback_query(F.data == "stats_total_users")
    async def show_total_users(callback: CallbackQuery):
        if not is_admin(callback.from_user.id):
            await callback.answer("❌ Siz admin emassiz!", show_alert=True)
            return
        
        count = db.get_total_users_count()
        await callback.message.edit_text(
            f"👥 Jami foydalanuvchilar soni: {count}",
            reply_markup=get_admin_stats_keyboard()
        )
        await callback.answer()
    
    @dp.callback_query(F.data == "stats_general")
    async def show_general_stats(callback: CallbackQuery):
        if not is_admin(callback.from_user.id):
            await callback.answer("❌ Siz admin emassiz!", show_alert=True)
            return
        
        stats = db.get_general_stats()
        text = "📊 Umumiy statistika:\n\n"
        text += f"👥 Jami foydalanuvchilar: {stats['total_users']}\n"
        text += f"📝 Ro'yxatdan o'tganlar: {stats['registered_users']}\n"
        text += f"📚 Jami testlar: {stats['total_tests']}\n"
        text += f"📁 Jami kategoriyalar: {stats['total_categories']}\n"
        text += f"📊 Jami test natijalari: {stats['total_results']}\n"
        text += f"📅 Oxirgi hafta test topshirganlar: {stats['week_completions']}\n"
        text += f"🔄 Oxirgi hafta faol foydalanuvchilar: {db.get_active_users_count(7)}"
        
        await callback.message.edit_text(text, reply_markup=get_admin_stats_keyboard())
        await callback.answer()
    
    # Kategoriya qo'shish
    @dp.callback_query(F.data == "admin_add_category")
    async def admin_add_category_start(callback: CallbackQuery, state: FSMContext):
        if not is_admin(callback.from_user.id):
            await callback.answer("❌ Siz admin emassiz!", show_alert=True)
            return
        
        await state.set_state(AddCategoryStates.waiting_for_name)
        await callback.message.edit_text(
            "➕ Kategoriya qo'shish\n\n"
            "Kategoriya nomini yuboring (masalan: Oson, O'rtacha, Qiyin):"
        )
        await callback.answer()
    
    @dp.message(AddCategoryStates.waiting_for_name)
    async def process_category_name(message: Message, state: FSMContext):
        if not is_admin(message.from_user.id):
            await message.answer("❌ Siz admin emassiz!")
            return
        
        category_name = message.text.strip()
        
        if len(category_name) < 2:
            await message.answer("❌ Kategoriya nomi juda qisqa! Qayta yuboring:")
            return
        
        await state.update_data(category_name=category_name)
        await state.set_state(AddCategoryStates.waiting_for_description)
        await message.answer(
            f"✅ Kategoriya nomi: {category_name}\n\n"
            "Kategoriya tavsifini yuboring (ixtiyoriy, yoki 'skip' yozib o'tib ketishingiz mumkin):"
        )
    
    @dp.message(AddCategoryStates.waiting_for_description)
    async def process_category_description(message: Message, state: FSMContext):
        if not is_admin(message.from_user.id):
            await message.answer("❌ Siz admin emassiz!")
            return
        
        description = message.text.strip()
        if description.lower() == 'skip':
            description = None
        
        data = await state.get_data()
        category_name = data['category_name']
        
        # Kategoriyani bazaga qo'shish
        category_id = db.add_category(category_name, description)
        
        await message.answer(
            f"✅ Kategoriya muvaffaqiyatli qo'shildi!\n\n"
            f"📁 Kategoriya ID: {category_id}\n"
            f"📝 Nomi: {category_name}\n"
            f"📄 Tavsifi: {description if description else 'Tavsif yo\'q'}",
            reply_markup=get_admin_panel_keyboard()
        )
        await state.clear()