from typing import Final
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardButton,InlineKeyboardMarkup

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

from db import adv_db
load_dotenv()  # take environment variables from .env.

BOT_TOKEN:Final = os.getenv("TOKEN")

# CATEGORY,EXCHANGE, PHOTO, DESCRIPTION = range(4)

# db connection
# add your user ids here, you can use @userinfobot to get your user id
# DO NOT REMOVE EXISTING IDs
chanell_id = os.getenv("chanell_id")


async def start_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [
        [InlineKeyboardButton(text="ثبت موتور", callback_data='submit_motor'),
        InlineKeyboardButton(text="ثبت ماشین", callback_data='submit_car')
        ],
        [InlineKeyboardButton(text='درباه ما', callback_data='about_us')]
    ]
    await update.message.reply_text(
        "لطفا بین دکمه های نمایش داده شده یکی را انتخاب کنید",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
        ),
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
    db = adv_db()
    user_info = db.get_user_info(adv_id=int(adv_id))
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
    # app.add_handler(CallbackQueryHandler(button))

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