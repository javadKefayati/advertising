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
SUPPORT_USERNAMES: Final = [u.strip() for u in os.getenv("SUPPORT_USERNAMES", "").split(",") if u.strip()]
SUPPORT_PHONE_NUMBERS: Final = [u.strip() for u in os.getenv("SUPPORT_PHONE_NUMBERS", "").split(",") if u.strip()]

SUPPORT_USERNAME_DEVELOPER:Final = os.getenv("SUPPORT_USERNAME_DEVELOPER", "")
BOT_TOKEN: Final = os.getenv("TOKEN", "")
TOKEN_ADMIN: Final = os.getenv("TOKEN_ADMIN", "")
BOT_USERNAME: Final = os.getenv("BOT_USERNAME", "")
MY_ADVERTISMENT_LIST_TEXT_BUTTON: Final = 'لیست آگهی های من'
HELP_TEXT_BUTTON: Final = 'راهنما'
RETURN_MESSAGE_BUTTON: Final = '🔙 بازگشت'
ADV_PICTURE_LIMIT: Final = os.getenv("ADV_PICTURE_LIMIT", 7)

SKIP_MESSAGE_BUTTON: Final = 'ادامه'

SUBMIT_NEW_USER_BUTTON: Final = 'ایجاد حساب کاربری'
DEFAULT_PICT_PATH:Final = os.getenv("DEFAULT_PICT_PATH", "")
DEFAULT_MOTOR_PICT_PATH:Final = os.getenv("DEFAULT_MOTOR_PICT_PATH", "")
DEFAULT_CAR_PICT_PATH:Final = os.getenv("DEFAULT_CAR_PICT_PATH", "")

DEFAULT_ADMIN_PANEL_USERNAME = os.getenv("DEFAULT_ADMIN_PANEL_USERNAME", "")
DEFAULT_ADMIN_PANEL_PASSWORD = os.getenv("DEFAULT_ADMIN_PANEL_PASSWORD", "")
SECRET_KEY = os.getenv("SECRET_KEY", "")
# region admin 
TOKEN_ADMIN: Final = os.getenv("TOKEN_ADMIN", "")
PENDING_ADVERTISMENT_TEXT_BUTTON:Final = "مشاهده آگهی های غیر فعال"
APPROVED_ADVERTISMENT_TEXT_BUTTON:Final = 'تایید کردن آگهی'
REJECTED_ADVERTISMENT_TEXT_BUTTON:Final = 'رد کردن آگهی'

# endregion
NOT_FOUND_ANY_ADVERTISEMENT_TEXT: Final = 'شما هنوز آگهی ثبت نکرده اید'
UNREGISTERED_USER_TEXT: Final = "شما هنوز ثبت نام نکرده اید، لطفا اول ثبت نام کنید."
START_TEXT: Final = (
   "خوش اومدی 👋 \n\n"
    "اگه می‌خوای یه آگهی جدید ثبت کنی، دکمه‌ی «ثبت آگهی جدید» رو بزن ✅\n\n"
    "اگه دکمه‌ها رو نمی‌بینی، روی آیکن چهار مربع پایین صفحه کلیک کن. \n\n"
    "⚠️ توجه: برای ثبت آگهی، باید حساب کاربری داشته باشی. "
    "اگه هنوز ثبت‌نام نکردی، از بخش «تنظیمات کاربری» شروع کن."
)

HELP_TEXT: Final = """
\u202B
📚 راهنمای استفاده از ربات:

🔹 الزامات:
- هر کاربر باید ابتدا در ربات ثبت نام کند

🔹 راهنما:
1️⃣ برای ثبت نام:
   - به بخش «تنظیمات کاربری» > «ثبت اطلاعات جدید» مراجعه کنید

2️⃣ برای ثبت آگهی جدید:
   - روی دکمه «ثبت آگهی جدید» کلیک کنید

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
در صورت مشکل به آی دی {SUPPORT_USERNAME_DEVELOPER} پیام دهید
\u202C
""".format(
    CHANELL_USERNAME=CHANELL_USERNAME,
    SUPPORT_USERNAME_DEVELOPER=SUPPORT_USERNAME_DEVELOPER
)
