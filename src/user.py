from db.advertisement_service import AdvertisementDb
from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    filters,
    MessageHandler,
)
from constants import (
    RETURN_MESSAGE_BUTTON,
    SUBMIT_NEW_USER_BUTTON
)
from keyboards import (
    USER_KEYBOARD,
    BACK_KEYBOARD,
    CHANGE_USER_INFO_KEYBOARD
)

FIRST_NAME, LAST_NAME, PHONE_NUMBER = range(3)
CHANGE_FIRST_NAME, CHANGE_LAST_NAME = range(2)
CHANGE_PHONE_NUMBER = range(1)

db = AdvertisementDb()


async def user_command_handler(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE):
    context.user_data["last_menu"] = "home_menu"
    await update.message.reply_text(
        "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=USER_KEYBOARD
    )


def format_iranian_phone(phone_number: str) -> str:
    if phone_number.startswith("98"):
        return "0" + phone_number[2:]
    return phone_number


async def show_user_info_handler(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE):
    context.user_data["last_menu"] = "home_menu"
    user_id = int(update.effective_user.id)
    user = db.get_user_by_id(user_id=user_id)
    if user:
        formatted_phone = format_iranian_phone(user.phone_number)

        user_info = f"""
        🧾 اطلاعات حساب کاربری شما:

        👤 نام کاربری: {user.username}
        🪪 نام و نام‌خانوادگی: {user.first_name} {user.last_name}
        📱 شماره تلفن: {formatted_phone}
        🗓 تاریخ عضویت: {user.inserted_at.strftime('%Y/%m/%d')}

    در صورتی که نیاز به ویرایش اطلاعات دارید، به بخش تغییر اطلاعات در تنظیمات کاربری مراجعه کنید.
        """

        await update.message.reply_text(user_info.strip())
    else:
        await update.message.reply_text("❌ هیچ اطلاعاتی با شناسه شما پیدا نشد. لطفاً ابتدا ثبت‌نام کنید.")


# region submit user

async def start_conv_handler(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE):
    if db.check_exist_user(
        user_id=update.effective_user.id
    ):
        context.user_data["last_menu"] = "home_menu"
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="اطلاعات شما قبلا ثبت شده است، برای تغییر آن از دکمه تغییر اطلاعات استفاده کنید",
            reply_to_message_id=update.effective_message.id,
            reply_markup=USER_KEYBOARD
        )
        return ConversationHandler.END
    context.user_data["last_menu"] = "user_menu"
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="لطفا اسم کوچک خود را وارد کنید(برای مثال: علی)",
        reply_to_message_id=update.effective_message.id,
        reply_markup=BACK_KEYBOARD
    )
    return FIRST_NAME


async def first_name_conv_handler(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE):
    context.user_data["first_name"] = update.effective_message.text
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="لطفا نام خانوادگی خود را وارد کنید(برای مثال: اکبری)",
        reply_to_message_id=update.effective_message.id
    )
    return LAST_NAME


async def last_name_conv_handler(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE):
    context.user_data["last_name"] = update.effective_message.text
    phone_keyboard = ReplyKeyboardMarkup(
        [
            [KeyboardButton("📱 ارسال شماره تلفن", request_contact=True)]
        ],
        resize_keyboard=True, one_time_keyboard=True
    )
    await update.message.reply_text(
        "لطفاً برای ادامه، شماره تلفن خود را ارسال کنید.\n"
        "از دکمه‌ای که در منو می‌بینید استفاده کنید و دسترسی لازم را به تلگرام بدهید تا شماره ثبت‌شده‌تان به‌صورت خودکار برای ما ارسال شود.",
        reply_markup=phone_keyboard
    )
    return PHONE_NUMBER


async def phone_number_conv_handler(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    context.user_data["last_menu"] = "home_menu"
    db.insert_new_user(
        user_id=update.effective_user.id,
        first_name=context.user_data["first_name"],
        last_name=context.user_data["last_name"],
        username=update.effective_user.username,
        phone_number=contact.phone_number
    )
    await update.message.reply_text(
        "اطلاعات شما با موفقیت ثبت شد",
        reply_markup=USER_KEYBOARD
    )
    return ConversationHandler.END
# endregion

# region change name and last_name user


async def start_change_name_conv_handler(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE):
    context.user_data["last_menu"] = "user_menu"
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="لطفا اسم کوچک جدید خود را وارد کنید(برای مثال: علی)",
        reply_to_message_id=update.effective_message.id,
        reply_markup=BACK_KEYBOARD
    )
    return CHANGE_FIRST_NAME


async def change_first_name_conv_handler(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE):
    context.user_data["change_first_name"] = update.effective_message.text
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="لطفا نام خانوادگی جدید خود را وارد کنید(برای مثال: اکبری)",
        reply_to_message_id=update.effective_message.id
    )
    return CHANGE_LAST_NAME


async def change_last_name_conv_handler(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE):
    context.user_data["change_last_name"] = update.effective_message.text
    context.user_data["last_menu"] = "home_menu"
    db.update_user_info(
        user_id=update.effective_user.id,
        first_name=context.user_data["change_first_name"],
        last_name=context.user_data["change_last_name"],
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="نام و نام خانوادگی شما با موفقیت تغییر یافت",
        reply_to_message_id=update.effective_message.id,
        reply_markup=USER_KEYBOARD
    )
    return ConversationHandler.END

# endregion

# region change phone_number of user


async def start_change_phone_number_conv_handler(
        update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["last_menu"] = "user_menu"
    phone_keyboard = ReplyKeyboardMarkup(
        [
            [KeyboardButton("📱 ارسال شماره تلفن", request_contact=True)]
        ],
        resize_keyboard=True, one_time_keyboard=True
    )
    await update.message.reply_text(
        "لطفاً شماره تلفن جدید خود را ارسال کنید:", reply_markup=phone_keyboard
    )
    return CHANGE_PHONE_NUMBER


async def change_phone_number_conv_handler(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    context.user_data["last_menu"] = "home_menu"

    db.update_user_info(
        user_id=update.effective_user.id,
        phone_number=contact.phone_number
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="تلفن همراه شما با موفقیت تغییر یافت",
        reply_to_message_id=update.effective_message.id,
        reply_markup=USER_KEYBOARD
    )
    return ConversationHandler.END

# endregion

# region username of user


async def change_username_handler(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE):
    context.user_data["last_menu"] = "home_menu"
    db.update_user_info(
        user_id=update.effective_user.id,
        username=update.effective_user.username
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="نام کاربری شما به صورت خودکار از روی اکانت شما تغییر یافت",
        reply_to_message_id=update.effective_message.id,
        reply_markup=USER_KEYBOARD
    )
# endregion


async def init_change_info_command_handler(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE):
    context.user_data["last_menu"] = "user_menu"
    await update.message.reply_text(
        "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=CHANGE_USER_INFO_KEYBOARD
    )


async def cancel_command_handler(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["last_menu"] = "home_menu"
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="فرآیند ثبت پایان یافت",
        reply_to_message_id=update.effective_message.id,
        reply_markup=USER_KEYBOARD,
    )
    return ConversationHandler.END


def get_user_handlers():
    RETURN_FILTER = filters.Regex(r"^" + RETURN_MESSAGE_BUTTON + "$")

    return [
        MessageHandler(
            filters.Regex(r"^تنظیمات کاربری$"),
            user_command_handler),
        MessageHandler(
            filters.Regex(r"^مشاهده اطلاعات پروفایل$"),
            show_user_info_handler),
        MessageHandler(
            filters.Regex(r"^تغییر نام‌کاربری$"),
            change_username_handler),
        MessageHandler(
            filters.Regex(r"^تغییر اطلاعات$"),
            init_change_info_command_handler),
        # submit user info
        ConversationHandler(
            entry_points=[
                MessageHandler(
                    filters.Regex(r"^" + SUBMIT_NEW_USER_BUTTON + "$"),
                    start_conv_handler
                )
            ],
            states={
                FIRST_NAME: [
                    MessageHandler(
                        ~RETURN_FILTER & filters.TEXT & ~filters.COMMAND, first_name_conv_handler
                    )
                ],
                LAST_NAME: [
                    MessageHandler(
                        ~RETURN_FILTER & filters.TEXT & ~filters.COMMAND, last_name_conv_handler
                    )
                ],
                PHONE_NUMBER: [
                    MessageHandler(
                        (~RETURN_FILTER) & filters.CONTACT, phone_number_conv_handler
                    )
                ]
            },
            fallbacks=[
                MessageHandler(
                    RETURN_FILTER, cancel_command_handler
                )

            ],
            allow_reentry=True,
            per_message=True

        ),
        # change first name and last_name of user
        ConversationHandler(
            entry_points=[
                MessageHandler(
                    filters.Regex("^تغییر نام و نام خانوادگی$"),
                    start_change_name_conv_handler
                )
            ],
            states={
                CHANGE_FIRST_NAME: [
                    MessageHandler(
                        (~RETURN_FILTER) & (filters.PHOTO |
                                            filters.TEXT | filters.COMMAND),
                        change_first_name_conv_handler
                    )
                ],
                CHANGE_LAST_NAME: [
                    MessageHandler(
                        (~RETURN_FILTER) & (filters.TEXT & ~filters.COMMAND),
                        change_last_name_conv_handler
                    )
                ]
            },
            fallbacks=[
                MessageHandler(
                    RETURN_FILTER, cancel_command_handler
                )

            ],
            allow_reentry=True,
        ),
        # change phone_number of user
        ConversationHandler(
            entry_points=[
                MessageHandler(
                    filters.Regex("^تغییر تلفن همراه$"),
                    start_change_phone_number_conv_handler
                )
            ],
            states={
                CHANGE_PHONE_NUMBER: [
                    MessageHandler(
                        (~RETURN_FILTER) & filters.CONTACT,
                        change_phone_number_conv_handler
                    )
                ],

            },
            fallbacks=[
                MessageHandler(
                    RETURN_FILTER, cancel_command_handler
                )

            ],
            allow_reentry=True,
        )
    ]
