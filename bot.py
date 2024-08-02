from typing import Final
from dotenv import load_dotenv


from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update

from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    filters,
    MessageHandler,
)
import os

load_dotenv()  # take environment variables from .env.


BOT_TOKEN: Final = os.getenv("TOKEN")

CATEGORY, PHOTO, DESCRIPTION = range(3)
# db connection
# add your user ids here, you can use @userinfobot to get your user id
# DO NOT REMOVE EXISTING IDs
chanell_id = os.getenv("chanell_id")


async def start_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="سلام عرض شد \n"
            "برای شروع فرآیند ثبت تبلیغات لطفا بر روی /add_advertising بزنید",
        reply_to_message_id=update.effective_message.id,
    )



async def add_advertising_command_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    # write your code here
    """Starts the conversation and asks the user about their category."""
    reply_keyboard = [["موتور", "ماشین"]]

    await update.message.reply_text(
        "لطفا بین ماشین و موتور یکی را انتخاب کنید",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="ماشین یا موتور ؟",
        ),
    )
    return CATEGORY


async def choice_category_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    # write your code here
    context.user_data["category"] = update.effective_message.text
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="لطفا عکس آگهی خود را ارسال کنید.",
        reply_to_message_id=update.effective_message.id,
        reply_markup=ReplyKeyboardRemove(),
    )
    return PHOTO        


async def photo_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    context.user_data["photo_url"] = update.effective_message.photo[-1].file_id
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="لطفا توضیحات آگهی خود را وارد کنید. در توضیحات می توانید اطلاعاتی مانند قیمت، شماره تماس و ... را وارد کنید.",
        reply_to_message_id=update.effective_message.id,
    )
    return DESCRIPTION          
    


async def description_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    description = f"نوع : \n{context.user_data['category']} \n\n"\
        "توضیحات : \n"\
        f"{update.effective_message.text}\n\n"\
        f"{chanell_id}"    
    
    await context.bot.send_photo(
                chat_id= chanell_id,
                photo=context.user_data["photo_url"],
                caption= description,
                )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="آگهی شما با موفقیت ثبت شد.",
        reply_to_message_id=update.effective_message.id,
    )

    return ConversationHandler.END   



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
    app.add_handler(
        ConversationHandler(
            entry_points=[
                CommandHandler("add_advertising", add_advertising_command_handler)
            ],
            states={
                CATEGORY: [
                    MessageHandler(
                        filters.Regex("^(ماشین|موتور)$"), choice_category_message_handler
                    )
                ],
                PHOTO: [
                    MessageHandler(filters.PHOTO, photo_message_handler),
                ],
                DESCRIPTION: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, description_message_handler
                    )
                ],
            },
            fallbacks=[
                CommandHandler("cancel", cancel_command_handler),
            ],
            allow_reentry=True,
        )
    )

    app.run_polling()
