"""Inline keyboardlar"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import MATH_LEVELS

def get_main_menu_keyboard(is_admin: bool = False):
    """Asosiy menyu keyboard (Inline)"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Test topshirish", callback_data="take_test")
        ],
        [
            InlineKeyboardButton(text="💬 Qo'llab-quvvatlash", callback_data="support"),
            InlineKeyboardButton(text="ℹ️ Bot haqida", callback_data="about")
        ]
    ])
    
    if is_admin:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text="🔐 Admin Panel", callback_data="admin_panel")
        ])
    
    return keyboard

def get_admin_panel_keyboard():
    """Admin panel keyboard (Inline)"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Test qo'shish", callback_data="admin_add_test"),
            InlineKeyboardButton(text="🗑️ Test o'chirish", callback_data="admin_delete_test")
        ],
        [
            InlineKeyboardButton(text="📁 Kategoriya qo'shish", callback_data="admin_add_category")
        ],
        [
            InlineKeyboardButton(text="🚫 Bloklash", callback_data="admin_block_user"),
            InlineKeyboardButton(text="✅ Blokdan chiqarish", callback_data="admin_unblock_user")
        ],
        [
            InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")
        ],
        [
            InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="back_to_main")
        ]
    ])
    return keyboard

def get_registration_keyboard():
    """Ro'yxatdan o'tish keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Ro'yxatdan o'tish", callback_data="register")]
    ])
    return keyboard

def get_test_keyboard(test_id: int, question_num: int, total: int, has_option_d: bool = False):
    """Test javoblarini tanlash uchun keyboard"""
    buttons = [
        [
            InlineKeyboardButton(text="A", callback_data=f"test_answer_{test_id}_a"),
            InlineKeyboardButton(text="B", callback_data=f"test_answer_{test_id}_b"),
            InlineKeyboardButton(text="C", callback_data=f"test_answer_{test_id}_c")
        ]
    ]
    
    if has_option_d:
        buttons[0].append(InlineKeyboardButton(text="D", callback_data=f"test_answer_{test_id}_d"))
    
    buttons.append([
        InlineKeyboardButton(text=f"❓ {question_num}/{total}", callback_data="question_info")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_admin_keyboard():
    """Admin panel uchun keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Testlar", callback_data="admin_tests")
        ],
        [
            InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="admin_users"),
            InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")
        ],
        [
            InlineKeyboardButton(text="📢 Ommaviy xabar", callback_data="admin_broadcast")
        ]
    ])
    return keyboard

def get_admin_tests_keyboard():
    """Admin testlar boshqaruvi"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Test qo'shish", callback_data="admin_add_test")
        ],
        [
            InlineKeyboardButton(text="✏️ Test tahrirlash", callback_data="admin_edit_test")
        ],
        [
            InlineKeyboardButton(text="🗑️ Test o'chirish", callback_data="admin_delete_test")
        ],
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_panel")
        ]
    ])
    return keyboard



def get_admin_categories_keyboard():
    """Admin kategoriyalar boshqaruvi"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Kategoriya qo'shish", callback_data="admin_add_category")
        ],
        [
            InlineKeyboardButton(text="✏️ Kategoriya tahrirlash", callback_data="admin_edit_category")
        ],
        [
            InlineKeyboardButton(text="🗑️ Kategoriya o'chirish", callback_data="admin_delete_category")
        ],
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_panel")
        ]
    ])
    return keyboard

def get_admin_users_keyboard():
    """Admin foydalanuvchilar boshqaruvi"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🚫 Bloklash", callback_data="admin_block_user")
        ],
        [
            InlineKeyboardButton(text="✅ Blokdan chiqarish", callback_data="admin_unblock_user")
        ],
        [
            InlineKeyboardButton(text="👥 Adminlar", callback_data="admin_manage")
        ],
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_panel")
        ]
    ])
    return keyboard

def get_admin_stats_keyboard():
    """Admin statistika keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📅 1 Hafta", callback_data="stats_test_week"),
            InlineKeyboardButton(text="📅 1 Oy", callback_data="stats_test_month")
        ],
        [
            InlineKeyboardButton(text="📅 1 Yil", callback_data="stats_test_year")
        ],
        [
            InlineKeyboardButton(text="👥 Jami foydalanuvchilar", callback_data="stats_total_users")
        ],
        [
            InlineKeyboardButton(text="📊 Umumiy statistika", callback_data="stats_general")
        ],
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_panel")
        ]
    ])
    return keyboard

def get_categories_keyboard(categories: list, for_admin: bool = False):
    """Kategoriyalar keyboard"""
    buttons = []
    for category in categories[:10]:
        if for_admin:
            # Admin test qo'shish uchun alohida callback
            buttons.append([
                InlineKeyboardButton(
                    text=category['category_name'],
                    callback_data=f"admin_select_category_{category['category_id']}"
                )
            ])
        else:
            # Foydalanuvchi test topshirish uchun
            buttons.append([
                InlineKeyboardButton(
                    text=category['category_name'],
                    callback_data=f"category_{category['category_id']}"
                )
            ])
    
    if for_admin:
        buttons.append([InlineKeyboardButton(text="🔙 Admin Panel", callback_data="admin_panel")])
    else:
        buttons.append([InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="back_to_main")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_level_selection_keyboard():
    """Daraja tanlash keyboard (Qiyin, O'rtacha, Oson)"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Qiyin", callback_data="add_test_level_hard"),
            InlineKeyboardButton(text="O'rtacha", callback_data="add_test_level_medium")
        ],
        [
            InlineKeyboardButton(text="Oson", callback_data="add_test_level_easy")
        ],
        [
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_panel")
        ]
    ])
    return keyboard

def get_edit_test_keyboard(tests: list):
    """Test tahrirlash keyboard"""
    buttons = []
    for test in tests[:10]:
        buttons.append([
            InlineKeyboardButton(
                text=f"✏️ Test #{test['test_id']}",
                callback_data=f"edit_test_{test['test_id']}"
            )
        ])
    
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_tests")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_edit_category_keyboard(categories: list):
    """Kategoriya tahrirlash keyboard"""
    buttons = []
    for category in categories[:10]:
        buttons.append([
            InlineKeyboardButton(
                text=f"✏️ {category['category_name']}",
                callback_data=f"edit_category_{category['category_id']}"
            )
        ])
    
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_categories")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_delete_category_keyboard(categories: list):
    """Kategoriya o'chirish keyboard"""
    buttons = []
    for category in categories[:10]:
        buttons.append([
            InlineKeyboardButton(
                text=f"🗑️ {category['category_name']}",
                callback_data=f"delete_category_{category['category_id']}"
            )
        ])
    
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_categories")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_delete_test_keyboard(tests: list):
    """Test o'chirish keyboard"""
    buttons = []
    for test in tests[:10]:
        level_name = MATH_LEVELS.get(test.get('level', ''), test.get('level', 'Noma\'lum'))
        buttons.append([
            InlineKeyboardButton(
                text=f"🗑️ Test #{test['test_id']}",
                callback_data=f"delete_test_{test['test_id']}"
            )
        ])
    
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_tests")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_assign_tests_keyboard(categories: list):
    """Testlarni kategoriyaga biriktirish keyboard"""
    buttons = []
    for category in categories[:10]:
        buttons.append([
            InlineKeyboardButton(
                text=category['category_name'],
                callback_data=f"assign_category_{category['category_id']}"
            )
        ])
    
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_categories")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_back_to_admin_keyboard():
    """Admin panelga qaytish keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Admin Panel", callback_data="admin_panel")]
    ])
    return keyboard

def get_back_to_main_keyboard():
    """Asosiy menyuga qaytish keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="back_to_main")]
    ])
    return keyboard

def get_admin_manage_keyboard():
    """Admin boshqarish keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Admin qo'shish", callback_data="admin_add_admin")
        ],
        [
            InlineKeyboardButton(text="🗑️ Admin o'chirish", callback_data="admin_remove_admin")
        ],
        [
            InlineKeyboardButton(text="📋 Adminlar ro'yxati", callback_data="admin_list")
        ],
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_users")
        ]
    ])
    return keyboard

def get_cancel_keyboard():
    """Bekor qilish keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")]
    ])
    return keyboard
