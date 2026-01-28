"""Helper funksiyalar"""
import re
import logging

logger = logging.getLogger(__name__)

# Global database instance (handlerlar tomonidan o'rnatiladi)
_db_instance = None

def set_db_instance(db):
    """Database instance ni o'rnatish"""
    global _db_instance
    _db_instance = db

def is_admin(user_id: int) -> bool:
    """Foydalanuvchi admin ekanligini tekshirish"""
    if _db_instance is None:
        raise RuntimeError("Database instance o'rnatilmagan! set_db_instance() ni chaqiring.")
    return _db_instance.is_admin(user_id)

def is_user_blocked(user_id: int) -> bool:
    """Foydalanuvchi bloklanganmi"""
    if _db_instance is None:
        raise RuntimeError("Database instance o'rnatilmagan! set_db_instance() ni chaqiring.")
    return _db_instance.is_user_blocked(user_id)

# OCR reader (global)
reader = None
OCR_AVAILABLE = False

def init_ocr():
    """OCR ni ishga tushirish"""
    global reader, OCR_AVAILABLE
    try:
        import easyocr
        reader = easyocr.Reader(['en', 'ru'], gpu=False)
        OCR_AVAILABLE = True
    except Exception as e:
        logger.warning(f"OCR o'rnatilmagan: {e}")
        OCR_AVAILABLE = False
        reader = None

async def process_image_with_ocr(image_path: str):
    """Rasmni OCR bilan qayta ishlash"""
    global reader, OCR_AVAILABLE
    if not OCR_AVAILABLE or not reader:
        return None
    try:
        results = reader.readtext(image_path)
        full_text = ' '.join([result[1] for result in results])
        return full_text
    except Exception as e:
        logger.error(f"OCR xatolik: {e}")
        return None

def extract_options_from_text(text: str):
    """Matndan variantlarni ajratib olish (yaxshilangan)"""
    options = {}
    
    # Turli formatlarni qidirish
    patterns = [
        r'([ABCD])\)\s*([^\n]+)',  # A) variant
        r'([ABCD])\.\s*([^\n]+)',  # A. variant
        r'([ABCD])\s+([^\n]+)',    # A variant (bo'sh joy bilan)
        r'([ABCD]):\s*([^\n]+)',   # A: variant
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            for match in matches:
                option_key = match[0].upper()
                option_value = match[1].strip()
                # Faqat bo'sh bo'lmagan variantlarni qo'shish
                if option_value and len(option_value) > 1:
                    options[option_key] = option_value
            break  # Birinchi topilgan pattern yetarli
    
    # Agar hech narsa topilmasa, qo'shimcha qidiruv
    if not options:
        # Satrlar bo'yicha qidirish
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            # A) yoki A. formatini qidirish
            for letter in ['A', 'B', 'C', 'D']:
                if line.upper().startswith(f'{letter})') or line.upper().startswith(f'{letter}.'):
                    value = re.sub(rf'^{letter}[).]\s*', '', line, flags=re.IGNORECASE).strip()
                    if value and len(value) > 1:
                        options[letter] = value
    
    return options
