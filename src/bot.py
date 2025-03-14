from typing import Final
from dotenv import load_dotenv
from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    InlineKeyboardButton
)
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    filters,
    MessageHandler,
    CommandHandler,
)
import os

import motor_conv
import car_conv

from db import AdvDB
load_dotenv()  # take environment variables from .env.

BOT_TOKEN:Final = os.getenv("TOKEN")

# CATEGORY,EXCHANGE, PHOTO, DESCRIPTION = range(4)

# db connection
# add your user ids here, you can use @userinfobot to get your user id
# DO NOT REMOVE EXISTING IDs
chanell_id = os.getenv("chanell_id")


async def help_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
    🤖 راهنمای استفاده از ربات ثبت آگهی

    با استفاده از این ربات، می‌توانید آگهی‌های خود را به سادگی ثبت و مدیریت کنید. در ادامه، راهنمای کامل استفاده از ربات را مشاهده می‌کنید:

    ---

    🔹 دستورات اصلی:

    - /start  
    شروع مجدد ربات و نمایش پیام راهنما.

    - /cancel  
    لغو عملیات جاری و بازگشت به منوی اصلی.

    - /admin  
    دسترسی به پنل مدیریت (فقط برای ادمین‌ها).

    ---

    🔸 نکات مهم:

    - برای استفاده از ربات، **حتماً باید username داشته باشید**. در غیر این صورت، امکان شناسایی صاحب آگهی وجود نخواهد داشت.
    - تمامی ارتباطات و پیگیری‌های مربوط به آگهی‌ها از طریق **username** انجام می‌شود.
    - لطفاً قبل از ثبت آگهی، از داشتن **username** اطمینان حاصل کنید.

    ---

    با تشکر از همراهی شما  
    تیم پشتیبانی ربات آگهی
    """

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text
    )

async def check_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username

    if not username:  # This checks both None and empty string
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                "شما به علت نداشتن username توانایی دسترسی به ربات را ندارید. \n"
                "لطفا username ساخته سپس به ربات مراجعه کنید."
            ),
            reply_to_message_id=update.effective_message.id,
        )
        return False  # Indicate that the user doesn't have access

    return True  # Indicate that the user has a username


async def start_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    adv = AdvDB()
    if not await check_username(update, context):
        return  # Stop processing if the user doesn't have a username

    if not adv.check_exist_user(
        user_id=update.effective_user.id
    ):
        adv.insert_new_user(
            user_id=update.effective_user.id,
            username=update.effective_user.username,
            first_name=update.effective_user.first_name,
            last_name=update.effective_user.last_name
        )

    # Define the inline keyboard buttons
    reply_keyboard = [
        [
            InlineKeyboardButton(text="ثبت موتور", callback_data='submit_motor'),
            InlineKeyboardButton(text="ثبت ماشین", callback_data='submit_car')
        ]
    ]

    # Send the message with the inline keyboard
    await update.message.reply_text(
        text=(
            "برای شروع ثبت آگهی، لطفاً یکی از گزینه‌های زیر را انتخاب کنید. در غیر این صورت، از دستور /help استفاده نمایید.\n\n"
            "⚠️ نکته: داشتن username اجباری است.\n\n"
            ),
        reply_markup=ReplyKeyboardMarkup(reply_keyboard)
    )

async def start_admin_conv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_users = os.getenv("ADMIN_USERS")
    if admin_users:
        admin_users =  admin_users.split(',')
        print(update.effective_user.username, admin_users)
        print(not update.effective_user.username in admin_users)

        if not update.effective_user.username in admin_users:
            await update.message.reply_text(
                text="شما ادمین نیستید",
                reply_to_message_id=update.effective_message.id,
            )
            return ConversationHandler.END

    await update.message.reply_text(
        text="برای گرفتن اطلاعات فرستنده آگهی ، لطفا شماره آگهی را وارد کنید",
        reply_to_message_id=update.effective_message.id,
    )
    return 1

async def adv_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    adv_id = update.effective_message.text
    db = AdvDB()
    adv_info = db.get_adv_info(adv_id=int(adv_id))
    adv_user_id = adv_info['user_id']
    user_info = db.get_user_info(user_id=adv_user_id)

    if user_info != None:
        text = f"شماره آگهی  : {adv_id}\n"\
            f"نام‌کاربری : @{user_info['username']}\n"\
            f"نام : {user_info['first_name']}\n"\
            f"نام خانوادگی : {user_info['last_name']}\n"
    else:
        text = "چنین آگهی وجود ندارد"

    await update.message.reply_text(
        text=text,
        reply_to_message_id=update.effective_message.id,
    )
    return  ConversationHandler.END

async def cancel_command_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="عملیات ثبت آگهی لغو شد. برای ثبت آگهی جدید از دستور /add_category استفاده کنید.",
        reply_to_message_id=update.effective_message.id,
    )
    return ConversationHandler.END


if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command_handler))
    app.add_handler(CommandHandler("help", help_command_handler))
    app.add_handler(CommandHandler("cancel", cancel_command_handler))

    app.add_handler(motor_conv.Motor_conv)
    app.add_handler(car_conv.Car_conv)

    admin_conv = ConversationHandler(
                entry_points=[
                        CommandHandler("admin", start_admin_conv)
                ],
                states={
                1: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, adv_info),
                ],
                },
            fallbacks=[
                CommandHandler("cancel", cancel_command_handler),
            ],
            allow_reentry=True,
        )
    app.add_handler(admin_conv)

    app.run_polling()