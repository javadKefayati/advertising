from telegram import (
    Update
)
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    filters,
    MessageHandler
)
from keyboards import (
    HOME_BOT_KEYBOARD,
    USER_KEYBOARD,
    VEHICLE_KEYBOARD
)
from constants import (
    RETURN_MESSAGE_BUTTON,
    HELP_TEXT,
    BOT_TOKEN,
    HELP_TEXT_BUTTON,
    MY_ADVERTISMENT_LIST_TEXT_BUTTON,
    START_TEXT,
    UNREGISTERED_USER_TEXT,
    NOT_FOUND_ANY_ADVERTISEMENT_TEXT
)
from vehicle import Vehicle
from car_conv import Car
from motor_conv import Motor
from user import get_user_handlers
from db.advertisement_service import AdvertisementDb

db = AdvertisementDb()


async def help_command_handler(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE):
    text = HELP_TEXT

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text
    )


async def start_command_handler(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        text=START_TEXT,
        reply_markup=HOME_BOT_KEYBOARD
    )


async def start_admin_conv(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        text="برای گرفتن اطلاعات فرستنده آگهی ، لطفا شماره آگهی را وارد کنید",
        reply_to_message_id=update.effective_message.id,
    )
    return 1


async def adv_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    adv_id = update.effective_message.text
    adv_info = db.get_adv_info(adv_id=int(adv_id))

    if adv_info is None:
        text = "چنین آگهی وجود ندارد"
    else:
        adv_user_id = adv_info['user_id']
        user_info = db.get_user_info(user_id=adv_user_id)

        if user_info is not None:
            text = (f"adv_id : {adv_id}\n"
                    f"username : @{user_info['username']}\n"
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


async def send_all_advertisement_info_to_user_handler(
        update: Update, context: ContextTypes.DEFAULT_TYPE):
    vehicle = Vehicle()
    if not vehicle.adv_db.check_exist_user(user_id=update.effective_user.id):
        await vehicle.send_unregistered_user_message(
            update=update,
            context=context,
            text=UNREGISTERED_USER_TEXT
        )
        return False
    advertisements = vehicle.adv_db.get_all_advertisements_with_photos_by_user(
        user_id=update.effective_user.id
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
            reply_markup=HOME_BOT_KEYBOARD
        )


async def cancel_command_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="فرآیند کنسل شد",
        reply_to_message_id=update.effective_message.id,
    )
    return ConversationHandler.END


async def return_call_back_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    last_menu = context.user_data.get("last_menu", "")
    if last_menu == "":
        last_menu = 'home_menu'

    # Define menu to keyboard mapping
    menu_keyboards = {
        'home_menu': HOME_BOT_KEYBOARD,
        'user_menu': USER_KEYBOARD,
        'vehicle_menu': VEHICLE_KEYBOARD,
    }

    keyboard = menu_keyboards.get(last_menu)
    # set new keyboard
    if keyboard:
        await update.message.reply_text(
            "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
            reply_markup=keyboard
        )
    # Reset last menu for next return button
    if last_menu in ['user_menu', 'vehicle_menu']:
        context.user_data["last_menu"] = 'home_menu'

    return ConversationHandler.END

if __name__ == "__main__":
    vehicale = Vehicle()
    car = Car()
    motor = Motor()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start_command_handler))
    app.add_handler(CommandHandler("help", help_command_handler))
    app.add_handler(
        MessageHandler(
            filters.Regex(fr"^{HELP_TEXT_BUTTON}$"),
            help_command_handler)
    )
    app.add_handler(
        MessageHandler(
            filters.Regex(fr"^{MY_ADVERTISMENT_LIST_TEXT_BUTTON}$"),
            send_all_advertisement_info_to_user_handler)
    )

    # Set group for priority, 0 is hightest
    for handler in vehicale.get_handlers():
        app.add_handler(handler, group=0)

    for handler in car.get_handlers():
        app.add_handler(handler, group=0)

    for handler in motor.get_handlers():
        app.add_handler(handler, group=0)

    for handler in get_user_handlers():
        app.add_handler(handler, group=0)

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
    app.add_handler(
        MessageHandler(
            filters.Regex(fr"^{RETURN_MESSAGE_BUTTON}$"),
            return_call_back_handler),
        group=1)

    app.run_polling()
