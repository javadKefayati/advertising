from telegram import (
    ReplyKeyboardRemove,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    InputMediaPhoto
)
import os
from dotenv import load_dotenv
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    filters,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler
)

from dotenv import load_dotenv

from db import AdvDB

load_dotenv()  # take environment variables from .env.

PHOTO_MOTOR, BRAND_MOTOR, MODEL_MOTOR, COLOR_MOTOR, FUNCTION_MOTOR, INSURANCE_MOTOR ,EXCHANGE_MOTOR, MONEY_MOTOR = range(8)
CHANELL_ID = os.getenv("CHANELL_ID")


async def motor_init_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    context.user_data["photo_urls"] = []  # Initialize an empty list for photos
    keyboard = [[KeyboardButton("تمام")]]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       resize_keyboard=True,
                                       one_time_keyboard=True)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="لطفا تصاویر آگهی خود را بارگذاری کنید. پس از اتمام بارگذاری تصاویر، لطفا دکمه 'تمام' را فشار دهید.",
        reply_to_message_id=update.effective_message.id,
        reply_markup=reply_markup,
    )
    return PHOTO_MOTOR


async def photo_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    if update.message.text == 'تمام':
        if not context.user_data["photo_urls"]:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="شما هیچ تصویری بارگذاری نکرده‌اید. لطفا حداقل یک تصویر بارگذاری کنید.",
                reply_to_message_id=update.effective_message.id,
            )
            return PHOTO_MOTOR
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="لطفا برند موتور خود را وارد کنید(برای مثال هوندا)",
            reply_to_message_id=update.effective_message.id,
            reply_markup=ReplyKeyboardRemove(),
        )
        return BRAND_MOTOR
    
    if update.message.photo:
        photo_file_id = update.message.photo[-1].file_id
        context.user_data["photo_urls"].append(photo_file_id)
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="لطفا یک تصویر ارسال کنید یا دکمه 'تمام' را برای ادامه فشار دهید.",
            reply_to_message_id=update.effective_message.id,
        )
    return PHOTO_MOTOR 
    
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
        text="🔹 لطفاً میزان کارکرد را به هزار کیلومتر وارد کنید.\n✔ فقط عدد بنویسید.\n(مثال: ۲۰ یعنی ۲۰,۰۰۰ کیلومتر)\n\n📌 نمونه درست: 20 \n🚫 نمونه نادرست: ۲۰ هزار یا بیست هزار کیلومتر\n\n✅ نیازی به نوشتن 'هزار' یا 'کیلومتر' نیست، فقط عدد را وارد کنید.",
        reply_to_message_id=update.effective_message.id,
    )
    return FUNCTION_MOTOR 

async def function_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    context.user_data["function"] = update.effective_message.text
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🔹 لطفاً تعداد ماه‌های بیمه را وارد کنید.\n✔ فقط عدد بنویسید.\n(مثال: ۲ یعنی ۲ ماه بیمه)\n\n📌 نمونه درست: 2 \n🚫 نمونه نادرست: ۲ ماه یا دو ماه\n\n✅ نیازی به نوشتن 'ماه' نیست، فقط عدد را وارد کنید.",
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
    query = update.callback_query
    await query.answer()

    # write your code here
    context.user_data["exchange"] = query.data
    await query.edit_message_text(text=f"{query.data}")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🔹 لطفاً قیمت را به تومان وارد کنید.\n✔ فقط عدد بنویسید.\n(مثال: ۲۰۰ یعنی ۲۰۰,۰۰۰,۰۰۰ تومان)\n\n📌 نمونه درست: 200 \n🚫 نمونه نادرست: ۲۰۰ میلیون یا دویست میلیون\n\n✅ نیازی به نوشتن 'میلیون' یا 'تومان' نیست، فقط عدد را وارد کنید.",
        reply_to_message_id=update.effective_message.id,
        reply_markup=ReplyKeyboardRemove(),

    )
    return MONEY_MOTOR



async def money_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    adv = AdvDB()
    context.user_data["money"] = update.effective_message.text

    description = \
        f"🛵 نوع: موتور\n"\
        f"🏷 برند: {context.user_data['brand']}\n"\
        f"📅 مدل: {context.user_data['model']}\n"\
        f"🔄 کارکرد: {context.user_data['function']} کیلومتر\n"\
        f"🛡 بیمه: {context.user_data['insurance']}\n"\
        f"🔄 معاوضه: {context.user_data['exchange']}\n"\
        f"💰 قیمت: {context.user_data['money']} تومان\n\n"\
        f"📢 برای اطلاعات بیشتر:\n"\
        f"📌 آدرس کانال: @kanal\n"\


    adv = AdvDB()
    adv_id = adv.insert_new_adver(
        user_id=update.effective_user.id,
        description= description
        )
    # ADD Header
    description = f"🔹 آگهی شماره: {adv_id}\n\n" + description
    media_group = [
        InputMediaPhoto(context.user_data["photo_urls"][0], caption=description)
    ]
    media_group.extend([InputMediaPhoto(url) for url in context.user_data["photo_urls"][1:]])
    await context.bot.send_media_group(chat_id=CHANELL_ID, media=media_group)

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
                MessageHandler(
                        filters.PHOTO | filters.TEXT | filters.Command, photo_message_handler
                        )                ],
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
                MONEY_MOTOR:[
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, money_message_handler
                    )
                ]
            },
            fallbacks=[
                CommandHandler("cancel", cancel_command_handler),
            ],
            allow_reentry=True,
        )

