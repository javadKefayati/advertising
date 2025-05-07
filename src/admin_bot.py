from telegram.ext import ApplicationBuilder, ContextTypes
# import asyncio
# import aiohttp

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    InputMediaPhoto
)
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    filters,
    MessageHandler
)
from db.advertisement_service import AdvertisementDb
from db.models import AdminApprovalStatus

from constants import (
    TOKEN_ADMIN,
    UNREGISTERED_USER_TEXT,
    NOT_FOUND_ANY_ADVERTISEMENT_TEXT,
    PENDING_ADVERTISMENT_TEXT_BUTTON,
    APPROVED_ADVERTISMENT_TEXT_BUTTON,
    REJECTED_ADVERTISMENT_TEXT_BUTTON,
    CHANELL_USERNAME
)
from keyboards import ADMIN_KEYBOARD
from vehicle import Vehicle

vehicle = Vehicle()


async def start_command_handler(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        text='خوش آمدید',
        reply_markup=ADMIN_KEYBOARD
    )


async def unapproved_advertisement_command_handler(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE):


    if not vehicle.adv_db.check_exist_user(user_id=update.effective_user.id):
        await vehicle.send_unregistered_user_message(
            update=update,
            context=context,
            text=UNREGISTERED_USER_TEXT
        )
        return False
    advertisements = vehicle.adv_db.get_advertisements_with_photos(
        admin_approved_status=AdminApprovalStatus.PENDING
    )
    if advertisements:
        for advertisement in advertisements:
            await vehicle.send_advertisement_info_to_user(
                update=update,
                context=context,
                user_id=update.effective_user.id,
                adv_obj=advertisement
            )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=NOT_FOUND_ANY_ADVERTISEMENT_TEXT,
            reply_to_message_id=update.effective_message.id,
            reply_markup=ADMIN_KEYBOARD
        )


async def start_approved_advertisment_conv(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        text="لطفا شماره آگهی را برای ثبت در کانال بفرستید",
        reply_to_message_id=update.effective_message.id,
    )
    return 1

async def change_status_advertisement_and_send_to_chanel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    adv_id = update.effective_message.text
    # TODO clean code
    adv_obj = vehicle.adv_db.get_advertisements_with_photos(adv_id=adv_id,admin_approved_status=AdminApprovalStatus.PENDING )
    if adv_obj:
        if AdminApprovalStatus.PENDING == adv_obj[0].admin_approved_status:
            vehicle.adv_db.update_advertisment_info(
                adv_id=adv_id,
                admin_approved_status=AdminApprovalStatus.APPROVED
            )
            # TODO change [0]
            advertisement = vehicle.adv_db.get_advertisements_with_photos(
                adv_id=adv_id
            )[0]
            
            # TODO convert func name and set common usage for chanel and user
            # TODO error handel of all output
            await vehicle.send_advertisement_info_to_user(
                            update=update,
                            context=context,
                            user_id=CHANELL_USERNAME,
                            adv_obj=advertisement
                        )
            await update.message.reply_text(
                text="آگهی با موفقیت در کانال قرار گرفت",
                reply_to_message_id=update.effective_message.id,
            )
        else:
            await update.message.reply_text(
                text="چنین آگهی وجود ندارد یا در وضعیت تایید نشده نیست",
                reply_to_message_id=update.effective_message.id,
            )
    else:
        await update.message.reply_text(
            text="چنین آگهی وجود ندارد یا در وضعیت تایید نشده نیست",
            reply_to_message_id=update.effective_message.id,
        )
    return ConversationHandler.END



async def start_reject_advertisment_conv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        text="لطفا شماره آگهی را برای  رد کردن در کانال بفرستید",
        reply_to_message_id=update.effective_message.id,
    )
    return 1

async def reject_advertisement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    adv_id = update.effective_message.text
    # TODO 
    if AdminApprovalStatus.PENDING == vehicle.adv_db.get_advertisements_with_photos(
        adv_id=adv_id
    )[0].admin_approved_status:
        vehicle.adv_db.update_advertisment_info(
            adv_id=adv_id,
            admin_approved_status=AdminApprovalStatus.REJECTED
        )
        # TODO send for user, your adv is rejected
        await update.message.reply_text(
            text="آگهی با موفقیت رد شد",
            reply_to_message_id=update.effective_message.id,
        )

    else:
        await update.message.reply_text(
            text="چنین آگهی وجود ندارد یا در وضعیت تایید نشده نیست",
            reply_to_message_id=update.effective_message.id,
        )
    return ConversationHandler.END

async def cancel_command_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="فرآیند کنسل شد",
        reply_to_message_id=update.effective_message.id,
    )
    return ConversationHandler.END




async def start_admin_conv(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        text="برای گرفتن اطلاعات فرستنده آگهی ، لطفا شماره آگهی را وارد کنید",
        reply_to_message_id=update.effective_message.id,
    )
    return 1


async def adv_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    adv_id = update.effective_message.text
    adv_info = vehicle.adv_db   .get_adv_info(adv_id=int(adv_id))

    if adv_info is None:
        text = "چنین آگهی وجود ندارد"
    else:
        adv_user_id = adv_info['user_id']
        user_info = vehicle.adv_db.get_user_info(user_id=adv_user_id)

        if user_info is not None:
            text = (f"adv_id : {adv_id}\n"
                    f"telegram_username : @{user_info['username']}\n"
                    f"submit_username : @{user_info['submit_username']}\n"
                    f"first_name : {user_info['first_name']}\n"
                    f"last_name: {user_info['last_name']}\n"
                    f"phone_number: {user_info['phone_number']}\n"
                    )
        else:
            text = ""

    await update.message.reply_text(
        text=text,
        reply_to_message_id=update.effective_message.id,
    )
    return ConversationHandler.END

# async def check_bot(context: ContextTypes.DEFAULT_TYPE):
#     url = f"https://t.me/{TARGET_BOT}"
#     try:
#         async with aiohttp.ClientSession() as session:
#             async with session.get(url) as resp:
#                 if resp.status != 200:
#                     await context.bot.send_message(USER_ID, f"⚠️ @{TARGET_BOT} is down!")
#     except:
#         await context.bot.send_message(USER_ID, f"❌ Error connecting to @{TARGET_BOT}")

# async def startup(app):
#     # Every 1 hour
#     app.job_queue.run_repeating(check_bot, interval=3600, first=10)

app = ApplicationBuilder().token(TOKEN_ADMIN).build()
app.add_handler(CommandHandler("start", start_command_handler))
app.add_handler(
    MessageHandler(
        filters.Regex(fr"^{PENDING_ADVERTISMENT_TEXT_BUTTON}$"),
        unapproved_advertisement_command_handler)
)

approved_adv_conv = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex(fr"^{APPROVED_ADVERTISMENT_TEXT_BUTTON}$"), start_approved_advertisment_conv)
    ],
    states={
        1: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, change_status_advertisement_and_send_to_chanel),
        ],
    },
    fallbacks=[
        CommandHandler("cancel", cancel_command_handler),
    ],
    allow_reentry=True,
)
app.add_handler(approved_adv_conv)


reject_adv_conv = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex(fr"^{REJECTED_ADVERTISMENT_TEXT_BUTTON}$"), start_reject_advertisment_conv)
    ],
    states={
        1: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, reject_advertisement),
        ],
    },
    fallbacks=[
        CommandHandler("cancel", cancel_command_handler),
    ],
    allow_reentry=True,
)
app.add_handler(reject_adv_conv)

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
# app.job_queue.run_once(startup, 0)
app.run_polling()
