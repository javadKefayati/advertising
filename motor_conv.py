
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardButton,InlineKeyboardMarkup
import os
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    filters,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler
)
from dotenv import load_dotenv

from db import adv_db

load_dotenv()  # take environment variables from .env.

PHOTO_MOTOR, BRAND_MOTOR, MODEL_MOTOR, COLOR_MOTOR, FUNCTION_MOTOR, INSURANCE_MOTOR ,EXCHANGE_MOTOR = range(7)
CHANELL_ID = os.getenv("CHANELL_ID")


async def motor_init_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    # write your code here
    """Starts the conversation and asks the user about their category."""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="لطفا تصویر آگهی خود را بارگذاری کنید",
        reply_to_message_id=update.effective_message.id,
        reply_markup=ReplyKeyboardRemove(),

    )
    return PHOTO_MOTOR


async def photo_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    context.user_data["photo_url"] = update.effective_message.photo[-1].file_id

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="لطفا برند موتور خود را وارد کنید(برای مثال هوندا)",
        reply_to_message_id=update.effective_message.id,
    )

    return BRAND_MOTOR   
    
async def brand_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    context.user_data["brand"] = update.effective_message.text
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="لطفا سال ساخت را تایپ کنید(به عدد وارد کنید)",
        reply_to_message_id=update.effective_message.id,
    )
    return MODEL_MOTOR

async def model_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    context.user_data["model"] = update.effective_message.text
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="لطفا رنگ موتور را تایپ کنید",
        reply_to_message_id=update.effective_message.id,
    )
    return COLOR_MOTOR


async def color_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    context.user_data["color"] = update.effective_message.text
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="لطفا کارکرد را تایپ کنید(مثال ۲۰ هزار)",
        reply_to_message_id=update.effective_message.id,
    )
    return FUNCTION_MOTOR

async def function_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    context.user_data["function"] = update.effective_message.text
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="لطفا تعداد ماه بیمه را تایپ کنید(مثال ۲ ماه)",
        reply_to_message_id=update.effective_message.id,
    )
    return INSURANCE_MOTOR

async def insurance_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    context.user_data["insurance"] = update.effective_message.text
    keyboard = [
        [
            InlineKeyboardButton("دارد", callback_data="دارد"),
            InlineKeyboardButton("ندارد", callback_data="ندارد"),
        ]
                ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("معاوضه ؟", reply_markup=reply_markup)
    return EXCHANGE_MOTOR

async def choice_exchange_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    adv = adv_db()
    query = update.callback_query
    await query.answer()

    # write your code here
    context.user_data["exchange"] = query.data
    await query.edit_message_text(text=f"{query.data}")
    adv_id = adv.insert_new_adver(
        user_id=update.effective_user.id,
        username=update.effective_user.username,
        first_name=update.effective_user.first_name,
        last_name=update.effective_user.last_name
        )

    description = f"آگهی شماره : {adv_id}\n\n\n"\
        f"نوع : \nموتور \n\n"\
        f"برند: {context.user_data['brand']}\n\n"\
        f"مدل: {context.user_data['model']}\n\n"\
        f"کارکرد: {context.user_data['function']}\n\n"\
        f"بیمه: {context.user_data['insurance']}\n\n"\
        f"معاوضه: {context.user_data['exchange']}\n\n\n\n"\
        f"آدرس کانال: kanal@\n\n"\
        f"آدرس پشتیبان: posht@df\n\n"
    print(CHANELL_ID)
    await context.bot.send_photo(
        chat_id=CHANELL_ID,
        caption= description,
        photo=context.user_data["photo_url"],
    )    

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="آگهی شما با موفقیت ثبت شد.",
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


Motor_conv = ConversationHandler(
            entry_points=[
                    MessageHandler(
                        filters.Regex("^ثبت موتور$"), motor_init_message_handler
                    )
            ],
            states={
                PHOTO_MOTOR: [
                    MessageHandler(filters.PHOTO, photo_message_handler),
                ],
                BRAND_MOTOR: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, brand_message_handler
                    )
                ],
                MODEL_MOTOR: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, model_message_handler
                    )
                ],
                COLOR_MOTOR: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, color_message_handler
                    )
                ],
                FUNCTION_MOTOR: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, function_message_handler
                    )
                ],
                INSURANCE_MOTOR: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, insurance_message_handler
                    )
                ],
                EXCHANGE_MOTOR: [
                    CallbackQueryHandler(
                        choice_exchange_message_handler
                    )
                ],

            },
            fallbacks=[
                CommandHandler("cancel", cancel_command_handler),
            ],
            allow_reentry=True,
        )

