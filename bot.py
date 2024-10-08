from typing import Final
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CommandHandler,
)
import os

import motor_conv
import car_conv


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



if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command_handler))
    # app.add_handler(CallbackQueryHandler(button))

    app.add_handler(motor_conv.Motor_conv)
    app.add_handler(car_conv.Car_conv)

    app.run_polling()
