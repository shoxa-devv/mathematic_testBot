# Matematik Testlar Boti

To'liq funksional Telegram boti - matematik testlar, admin panel va foydalanuvchi boshqaruvi bilan.

## O'rnatish

1. Kerakli kutubxonalarni o'rnating:
```bash
pip install -r requirements.txt
```

2. `.env` faylini tahrirlang va bot token va admin ID ni kiriting:
```
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_admin_id_here
```

3. Botni ishga tushiring:
```bash
python main.py
```

## Funksiyalar

### Foydalanuvchi funksiyalari:

#### Ro'yxatdan o'tish:
- Ism
- Familiya
- Otasining ismi
- Telefon raqami

#### Asosiy menyu:
- 📝 Test topshirish
- 💬 Qo'llab-quvvatlash
- ℹ️ Bot haqida

#### Test topshirish:
- Kategoriya tanlash
- 20 ta savol (bitta-bitta ko'rsatiladi)
- Har bir savolda:
  - Savol matni
  - Rasm (agar mavjud bo'lsa)
  - Inline buttonlar orqali javob variantlari
- Test yakuni:
  - Natija foizda ko'rsatiladi
  - Qaysi savollarga qanday javob bergani ko'rsatiladi

### Admin funksiyalari:

#### Testlar bilan ishlash:
- ➕ Test qo'shish (rasm yuborilganda OCR bilan avtomatik tahlil)
- ✏️ Test tahrirlash
- 🗑️ Test o'chirish

#### Kategoriyalar bilan ishlash:
- ➕ Kategoriya yaratish
- ✏️ Kategoriya tahrirlash
- 🗑️ Kategoriya o'chirish
- 🔗 Testlarni kategoriyaga biriktirish

#### Foydalanuvchilar bilan ishlash:
- 🚫 Foydalanuvchini telefon raqami orqali bloklash
- ✅ Foydalanuvchini blokdan chiqarish
- 👥 Adminlar boshqaruvi (qo'shish/o'chirish)

#### Ommaviy xabar:
- 📢 Botdagi barcha foydalanuvchilarga xabar yuborish

#### Statistika:
- 📅 1 hafta/oy/yil davomida test topshirgan foydalanuvchilar soni
- 👥 Botdagi jami foydalanuvchilar soni
- 🔄 Oxirgi hafta davomida botdan foydalangan foydalanuvchilar soni
- 📊 Umumiy statistika (to'liq hisobot)

#### Admin xabardorligi:
- Test tugagach adminlarga avtomatik xabar:
  - Foydalanuvchi ismi
  - Kategoriya
  - Natija (foiz)

## Test qo'shish jarayoni

1. Admin Panel → Testlar → Test qo'shish
2. Kategoriyani tanlang
3. Test savolini rasm sifatida yuboring
4. Bot avtomatik OCR bilan rasmni tahlil qiladi va variantlarni ajratib oladi
5. Agar OCR to'liq ishlamasa, variantlarni qo'lda kiriting
6. To'g'ri javobni yuboring (a, b, c yoki d)

## Kategoriya yaratish

1. Admin Panel → Kategoriyalar → Kategoriya qo'shish
2. Kategoriya nomini yuboring
3. Kategoriya tavsifini yuboring (ixtiyoriy)

## Foydalanuvchi bloklash

1. Admin Panel → Foydalanuvchilar → Bloklash
2. Telefon raqamini yuboring
3. Foydalanuvchi bloklanadi

## Ommaviy xabar yuborish

1. Admin Panel → Ommaviy xabar
2. Xabarni yuboring
3. Barcha foydalanuvchilarga yuboriladi (bloklanganlar bundan mustasno)

## Fayl strukturası

- `main.py` - Asosiy bot fayli (barcha funksiyalar)
- `database.py` - Database funksiyalari (SQLite)
- `keyboards.py` - Inline va Reply keyboardlar
- `config.py` - Konfiguratsiya
- `.env` - Environment variables
- `tests/` - Test rasmlari papkasi (avtomatik yaratiladi)

## Database strukturası

- `users` - Foydalanuvchilar
- `user_profiles` - Foydalanuvchi profillari (ism, familiya, telefon)
- `blocked_users` - Bloklangan foydalanuvchilar
- `admins` - Adminlar
- `categories` - Kategoriyalar
- `tests` - Testlar
- `test_results` - Test natijalari
- `test_answers` - Har bir savolga berilgan javoblar

## Eslatmalar

- Bot tokenni [@BotFather](https://t.me/BotFather) dan olishingiz mumkin
- Admin ID ni olish uchun [@userinfobot](https://t.me/userinfobot) dan foydalaning
- EasyOCR birinchi marta ishga tushganda modellarni yuklaydi (bir necha daqiqa vaqt olishi mumkin)
- Bloklangan foydalanuvchilar botdan foydalana olmaydi va ommaviy xabarlarni olmaydi

## Texnik ma'lumotlar

- **Python 3.8+**
- **aiogram 3.3.0** - Telegram Bot API
- **SQLite** - Database
- **EasyOCR** - Rasm tahlil qilish (OCR)
- **python-dotenv** - Environment variables