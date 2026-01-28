"""FSM States"""
from aiogram.fsm.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    waiting_for_full_name = State()
    waiting_for_phone = State()

class AddTestStates(StatesGroup):
    waiting_for_image = State()
    waiting_for_answers = State()
    waiting_for_test_category = State()
    waiting_for_category = State() # This seems to be used for something else or duplicate, but keeping for safety. Wait, based on previous edits, waiting_for_category was used for Level selection? Let's check admin_handlers.py. Ah, `add_test_level_selected` uses `waiting_for_category`. This naming is confusing. Level selection uses `waiting_for_category`. I will add `waiting_for_test_category` for actual Category selection.
    # Old states kept for compatibility if needed, but we essentially replace the flow
    waiting_for_option_a = State()
    waiting_for_option_b = State()
    waiting_for_option_c = State()
    waiting_for_option_d = State()
    waiting_for_correct_answer = State()

class EditTestStates(StatesGroup):
    waiting_for_test_id = State()
    waiting_for_field = State()
    waiting_for_value = State()

class AddCategoryStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()

class EditCategoryStates(StatesGroup):
    waiting_for_category_id = State()
    waiting_for_field = State()
    waiting_for_value = State()

class TestTakingStates(StatesGroup):
    taking_test = State()

class BroadcastStates(StatesGroup):
    waiting_for_message = State()

class BlockUserStates(StatesGroup):
    waiting_for_username = State()

class UnblockUserStates(StatesGroup):
    waiting_for_username = State()

class AddAdminStates(StatesGroup):
    waiting_for_admin_id = State()

class RemoveAdminStates(StatesGroup):
    waiting_for_admin_id = State()
