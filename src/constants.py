from dotenv import load_dotenv
from typing import Final
import os

load_dotenv()  # take environment variables from .env.

POSTGRES_DB: Final = os.getenv("POSTGRES_DB", "")
POSTGRES_USER: Final = os.getenv("POSTGRES_USER", "")
POSTGRES_PASSWORD: Final = os.getenv("POSTGRES_PASSWORD", "")
POSTGRES_HOST: Final = os.getenv("POSTGRES_HOST", "")
POSTGRES_PORT: Final = os.getenv("POSTGRES_PORT", "")
CHANELL_USERNAME: Final = os.getenv("CHANELL_USERNAME", "")
SUPPORT_USERNAME: Final = os.getenv("SUPPORT_USERNAME", "")
BOT_TOKEN: Final = os.getenv("TOKEN", "")

MY_ADVERTISMENT_LIST_TEXT_BUTTON: Final = 'لیست آگهی های من'
HELP_TEXT_BUTTON: Final = 'راهنما'
RETURN_MESSAGE_BUTTON: Final = '🔙 بازگشت'
SUBMIT_NEW_USER_BUTTON: Final = 'ایجاد حساب کاربری'

NOT_FOUND_ANY_ADVERTISEMENT_TEXT: Final = 'شما هنوز آگهی ثبت نکرده اید'
UNREGISTERED_USER_TEXT: Final = "شما هنوز ثبت نام نکرده اید، لطفا اول ثبت نام کنید."
START_TEXT: Final = (
    "سلام! 👋\n\n"
    "به ربات ثبت آگهی خوش ‌اومدی 🙌\n\n"
    "برای ثبت آگهی جدید، دکمه‌ی «ثبت تبلیغ جدید» رو بزن ✅\n\n"
    "برای دریافت راهنما، از دکمه‌ی «راهنما» استفاده کن یا دستور /help رو وارد کن \n\n"
    "⚠️ توجه: برای ثبت آگهی، داشتن حساب کاربری الزامی‌ست،"
    "اگر هنوز حساب نساختی، از بخش تنظیمات کاربری اقدام کن.")

HELP_TEXT: Final = """
\u202B
📚 راهنمای استفاده از ربات:

🔹 الزامات:
- هر کاربر باید ابتدا در ربات ثبت نام کند

🔹 راهنما:
1️⃣ برای ثبت نام:
   - به بخش «تنظیمات کاربری» > «ثبت اطلاعات جدید» مراجعه کنید

2️⃣ برای ثبت آگهی جدید:
   - روی دکمه «ثبت تبلیغ جدید» کلیک کنید

3️⃣ برای مشاهده آگهی‌های خود:
   - گزینه «آگهی‌های من» را انتخاب کنید

🔹 تنظیمات کاربری شامل:
- ثبت اطلاعات کاربری جدید
- مشاهده اطلاعات کاربری
- ویرایش اطلاعات قبلی

🔸 نکته:
- در هر مرحله با فشردن دکمه «بازگشت» می‌توانید به مرحله قبل برگردید

📌 کانال ما:
{CHANELL_USERNAME}

🛟 پشتیبانی:
در صورت مشکل به آی دی {SUPPORT_USERNAME} پیام دهید
\u202C
""".format(
    CHANELL_USERNAME=CHANELL_USERNAME,
    SUPPORT_USERNAME=SUPPORT_USERNAME
)
