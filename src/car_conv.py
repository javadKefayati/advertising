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

load_dotenv()  # take environment variables from .env.

PHOTO_CAR, BRAND_CAR, MODEL_CAR, COLOR_CAR, FUNCTION_CAR, INSURANCE_CAR ,EXCHANGE_CAR, BODY_CAR, CHASSIS_CAR, TECHNICAL_CAR, MOTOR_CAR, GEARBOX_CAR, MONEY_CAR = range(13)
CHANELL_ID = os.getenv("CHANELL_ID")

from db import AdvDB

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
    return PHOTO_CAR

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
            return PHOTO_CAR
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="لطفا برند ماشین خود را وارد کنید(برای مثال سمند)",
            reply_to_message_id=update.effective_message.id,
            reply_markup=ReplyKeyboardRemove(),
        )
        return BRAND_CAR
    
    if update.message.photo:
        photo_file_id = update.message.photo[-1].file_id
        context.user_data["photo_urls"].append(photo_file_id)
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="لطفا یک تصویر ارسال کنید یا دکمه 'تمام' را برای ادامه فشار دهید.",
            reply_to_message_id=update.effective_message.id,
        )
    return PHOTO_CAR
    
async def brand_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    context.user_data["brand"] = update.effective_message.text
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="لطفا سال ساخت را تایپ کنید(به عدد وارد کنید)",
        reply_to_message_id=update.effective_message.id,
    )
    return MODEL_CAR 

async def model_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    context.user_data["model"] = update.effective_message.text
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="لطفا رنگ ماشین را تایپ کنید",
        reply_to_message_id=update.effective_message.id,
    )
    return COLOR_CAR 


async def color_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    context.user_data["color"] = update.effective_message.text
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🔹 لطفاً میزان کارکرد را به هزار کیلومتر وارد کنید.\n✔ فقط عدد بنویسید.\n(مثال: ۲۰ یعنی ۲۰,۰۰۰ کیلومتر)\n\n📌 نمونه درست: 20 \n🚫 نمونه نادرست: ۲۰ هزار یا بیست هزار کیلومتر\n\n✅ نیازی به نوشتن 'هزار' یا 'کیلومتر' نیست، فقط عدد را وارد کنید.",
        reply_to_message_id=update.effective_message.id,
    )
    return FUNCTION_CAR 

async def function_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    context.user_data["function"] = update.effective_message.text
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🔹 لطفاً تعداد ماه‌های بیمه را وارد کنید.\n✔ فقط عدد بنویسید.\n(مثال: ۲ یعنی ۲ ماه بیمه)\n\n📌 نمونه درست: 2 \n🚫 نمونه نادرست: ۲ ماه یا دو ماه\n\n✅ نیازی به نوشتن 'ماه' نیست، فقط عدد را وارد کنید.",
        reply_to_message_id=update.effective_message.id,
    )
    return INSURANCE_CAR 

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
    return EXCHANGE_CAR 

async def choice_exchange_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()

    # write your code here
    context.user_data["exchange"] = query.data
    await query.edit_message_text(text=f"{query.data}")

    keyboard = [[
     InlineKeyboardButton("سالم", callback_data="سالم"),
        InlineKeyboardButton("نیاز به تعمیر", callback_data="نیاز به تعمیر"),
        InlineKeyboardButton("تعویض شده", callback_data="تعویض شده")]
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="وضعیت موتور ماشین؟",
        reply_markup=reply_markup
    )

    return  MOTOR_CAR  

async def motor_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
    query = update.callback_query
    await query.answer()
    context.user_data["motor"] = query.data
    await query.edit_message_text(text=f"{query.data}")

    keyboard = [
        [InlineKeyboardButton("سالم و بی‌خط و خش", callback_data="سالم")],
        [InlineKeyboardButton("خط و خش جزیی", callback_data="نیاز به تعمیر")],
        [InlineKeyboardButton("صافکاری بی‌رنگ", callback_data="تعویض شده")],
        [InlineKeyboardButton("رنگ شدگی", callback_data="رنگ شدگی")],
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="وضعیت بدنه ؟",
        reply_markup=reply_markup
    )
    return BODY_CAR

async def body_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
    query = update.callback_query
    await query.answer()
    context.user_data["body"] = query.data
    await query.edit_message_text(text=f"{query.data}")

    keyboard = [
        [InlineKeyboardButton("هر دو سالم و پلمپ", callback_data="هر دو سالم و پلمپ")],
        [InlineKeyboardButton("عقب ضربه خورده", callback_data="عقب ضربه خورده")],
        [InlineKeyboardButton("جلو ضربه خورده", callback_data="جلو ضربه خورده")],
        [InlineKeyboardButton("هر دو ضربه خورده", callback_data="هر دو ضربه خورده")],
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="وضعیت شاسی؟",
        reply_markup=reply_markup
    )
    return CHASSIS_CAR

async def chassis_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
    query = update.callback_query
    await query.answer()
    context.user_data["chassis"] = query.data
    await query.edit_message_text(text=f"{query.data}")


    keyboard = [[
        InlineKeyboardButton("دارد", callback_data="دارد"),
        InlineKeyboardButton("ندارد", callback_data="ندارد"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="معاینه فنی؟",
        reply_markup=reply_markup
    )
    return TECHNICAL_CAR


async def technical_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
    query = update.callback_query
    await query.answer()
    context.user_data["technical"] = query.data
    await query.edit_message_text(text=f"{query.data}")

    keyboard = [[
        InlineKeyboardButton("دستی", callback_data="دستی"),
        InlineKeyboardButton("اتوماتیک", callback_data="اتوماتیک"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="نوع گیربکس؟",
        reply_markup=reply_markup
    )
    print("test")
    return GEARBOX_CAR

async def gearbox_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
    query = update.callback_query
    await query.answer()
    context.user_data["gearbox"] = query.data
    await query.edit_message_text(text=f"{query.data}")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🔹 لطفاً قیمت را به تومان وارد کنید.\n✔ فقط عدد بنویسید.\n(مثال: ۲۰۰ یعنی ۲۰۰,۰۰۰,۰۰۰ تومان)\n\n📌 نمونه درست: 200 \n🚫 نمونه نادرست: ۲۰۰ میلیون یا دویست میلیون\n\n✅ نیازی به نوشتن 'میلیون' یا 'تومان' نیست، فقط عدد را وارد کنید.",
        reply_to_message_id=update.effective_message.id,
        reply_markup=ReplyKeyboardRemove(),

    )

    return MONEY_CAR

async def money_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
    ):

    context.user_data["money"] = update.effective_message.text
    description = \
        f"🚗 نوع: ماشین\n"\
        f"🏷 برند: {context.user_data['brand']}\n"\
        f"📅 مدل: {context.user_data['model']}\n"\
        f"🔄 کارکرد: {context.user_data['function']} هزار کیلومتر\n"\
        f"🛡 بیمه: {context.user_data['insurance']} ماه\n"\
        f"🔄 معاوضه: {context.user_data['exchange']}\n"\
        f"🚗 وضعیت بدنه: {context.user_data['body']}\n"\
        f"🛠 وضعیت شاسی: {context.user_data['chassis']}\n"\
        f"⚙ وضعیت موتور: {context.user_data['motor']}\n"\
        f"✅ معاینه فنی: {context.user_data['technical']}\n"\
        f"⚡ نوع گیربکس: {context.user_data['gearbox']}\n"\
        f"💰 قیمت: {context.user_data['money']}  ملیون تومان\n\n"\
        f"📢 برای اطلاعات بیشتر:\n"\
        f"📌 آدرس کانال: {CHANELL_ID}\n"\

    adv = AdvDB()
    adv_id = adv.insert_new_adver(
        user_id=update.effective_user.id,
        description= description
        )

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

async def mo_init_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    # write your code here
    """Starts the conversation and asks the user about their category."""
 
async def cancel_command_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="عملیات ثبت آگهی لغو شد. برای ثبت آگهی جدید از دستور /add_category استفاده کنید.",
        reply_to_message_id=update.effective_message.id,
    )
    return ConversationHandler.END


Car_conv = ConversationHandler(
            entry_points=[
                    MessageHandler(
                        filters.Regex("^ثبت ماشین$"), motor_init_message_handler
                    )
            ],
            states={
                PHOTO_CAR : [
                    MessageHandler(
                        filters.PHOTO | filters.TEXT | filters.Command, photo_message_handler
                        )
                ],
                BRAND_CAR : [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, brand_message_handler
                    )
                ],
                MODEL_CAR : [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, model_message_handler
                    )
                ],
                COLOR_CAR : [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, color_message_handler
                    )
                ],
                FUNCTION_CAR : [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, function_message_handler
                    )
                ],
                INSURANCE_CAR : [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, insurance_message_handler
                    )
                ],
                EXCHANGE_CAR : [
                    CallbackQueryHandler(
                        choice_exchange_message_handler
                    )
                ],
                BODY_CAR: [
                   CallbackQueryHandler(
                        body_message_handler
                    )
                ],
                CHASSIS_CAR: [
                   CallbackQueryHandler(
                        chassis_message_handler
                    )
                ],
                TECHNICAL_CAR: [
                   CallbackQueryHandler(
                        technical_message_handler
                    )
                ],
                MOTOR_CAR: [
                   CallbackQueryHandler(
                        motor_message_handler
                    )
                ],
                GEARBOX_CAR: [
                   CallbackQueryHandler(
                        gearbox_message_handler
                    )
                ],
                MONEY_CAR:[
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

