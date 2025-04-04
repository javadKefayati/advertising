from abc import ABC
from typing import Optional
from enum import Enum, auto
import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    InputMediaPhoto
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    filters,
    MessageHandler,
    CallbackQueryHandler
)
from constants import (
    RETURN_MESSAGE_BUTTON,
    CHANELL_USERNAME,
    UNREGISTERED_USER_TEXT
)
from keyboards import (
    VEHICLE_KEYBOARD,
    BACK_KEYBOARD,
    HOME_BOT_KEYBOARD,
    USER_KEYBOARD
)
from db.advertisement_service import AdvertisementDb

BASE_PATH = "/app/"

FIRST_NAME, LAST_NAME, PHONE_NUMBER = range(3)
CHANGE_FIRST_NAME, CHANGE_LAST_NAME = range(2)
CHANGE_PHONE_NUMBER = range(1)

db = AdvertisementDb()


class Vehicle(ABC):
    adv_db = db
    RETURN_FILTER = filters.Regex(r"^" + RETURN_MESSAGE_BUTTON + "$")

    def __init__(self):
        self.vehicle_type = self.__class__.__name__

    class Step(Enum):
        PHOTO = auto()
        BRAND = auto()
        MODEL = auto()
        COLOR = auto()
        FUNCTION = auto()
        INSURANCE = auto()
        EXCHANGE = auto()
        MONEY = auto()
        BODY = auto()
        CHASSIS = auto()
        TECHNICAL = auto()
        MOTOR = auto()
        GEARBOX = auto()
        APPROVE = auto()

    def generate_advertisement_info_format(
        self,
        advertisement_id: Optional[int] = None,
        advertisement_type: Optional[str] = None,
        vehicle_type: Optional[str] = None,
        brand: Optional[str] = None,
        model: Optional[str] = None,
        function: Optional[str] = None,
        insurance: Optional[str] = None,
        exchange: Optional[str] = None,
        money: Optional[str] = None,
        body: Optional[str] = None,
        chassis: Optional[str] = None,
        motor: Optional[str] = None,
        technical: Optional[str] = None,
        gearbox: Optional[str] = None
    ) -> str:

        # Mapping of field names to their display format
        field_mapping = {
            'vehicle_type': {
                'Car': '🚗 نوع: ماشین',
                'Motor': '🛵 نوع: موتور'
            },
            'advertisement_type': {
                'shop': 'آگهی خرید',
                'sale': 'آگهی فروش'
            },
            'brand': '🏷  برند:  {}',
            'model': '📅  مدل:  {}',
            'function': '🔄  کارکرد:  {} هزار کیلومتر',
            'insurance': '🛡  بیمه:  {} ماه',
            'exchange': '🔄  معاوضه:  {}',
            'money': '💰  قیمت:  {}',
            'body': '🚗  وضعیت بدنه:  {}',
            'chassis': '🛠  وضعیت شاسی:  {}',
            'motor': '⚙  وضعیت موتور:  {}',
            'technical': '✅  معاینه فنی:  {}',
            'gearbox': '⚡  نوع گیربکس:  {}'
        }

        description_parts = []

        # Handle special cases first
        if advertisement_type and advertisement_type in field_mapping['advertisement_type']:
            description_parts.append(
                field_mapping['advertisement_type'][advertisement_type])

        if vehicle_type and vehicle_type in field_mapping['vehicle_type']:
            description_parts.append(
                field_mapping['vehicle_type'][vehicle_type])

        # Handle regular fields
        fields = {
            'brand': brand,
            'model': model,
            'function': function,
            'insurance': insurance,
            'exchange': exchange,
            'money': money,
            'body': body,
            'chassis': chassis,
            'motor': motor,
            'technical': technical,
            'gearbox': gearbox
        }

        for field, value in fields.items():
            if value:
                description_parts.append(field_mapping[field].format(value))

        description = '\n'.join(description_parts)

        if advertisement_id:
            description = f"🔹 آگهی شماره: {advertisement_id}\n\n" + description
        else:
            description = "    \n\n" + description
        description = description + f"\n\n\n📌 آدرس کانال: {CHANELL_USERNAME}"
        return description

    def check_sale_or_shop(self, text):
        if text and "فروش" in text:
            vehicle_type = "sale"
        else:
            vehicle_type = "shop"

        return vehicle_type

    async def send_unregistered_user_message(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE,
            text: str = ""):

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_to_message_id=update.effective_message.id,
            reply_markup=USER_KEYBOARD
        )

    async def start_init_vehicle_menue(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE):
        if not self.adv_db.check_exist_user(user_id=update.effective_user.id):
            await self.send_unregistered_user_message(
                update=update,
                context=context,
                text=UNREGISTERED_USER_TEXT
            )
            return False

        context.user_data["last_menu"] = 'home_menu'
        await update.message.reply_text(
            "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
            reply_markup=VEHICLE_KEYBOARD
        )

    # region common converstion handler
    async def vehicle_init_message_handler(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE) -> int:

        context.user_data["last_menu"] = "vehicle_menu"

        context.user_data["advertisement_type"] = self.check_sale_or_shop(
            text=update.message.text
        )

        context.user_data["photos"] = []

        photo_keyboard = [
            [
                InlineKeyboardButton(text="تمام", callback_data='submit_car'),
            ],
            [
                InlineKeyboardButton(text=RETURN_MESSAGE_BUTTON, callback_data='submit_motor')
            ]
        ]
        reply_markup = ReplyKeyboardMarkup(photo_keyboard,
                                           resize_keyboard=True
                                           )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                "📌 در فرآیند ثبت آگهی، برای بازگشت یا پایان دادن می‌توانید از دکمه «بازگشت» استفاده کنید.\n\n"
                "🖼 لطفاً تصاویر آگهی خود را بارگذاری کنید. پس از اتمام بارگذاری، دکمه «تمام» را فشار دهید."
            ),
            reply_to_message_id=update.effective_message.id,
            reply_markup=reply_markup,
        )
        return self.Step.PHOTO.value

    async def photo_message_handler(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE) -> int:
        if update.message.text == 'تمام':
            if not context.user_data["photos"]:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="شما هیچ تصویری بارگذاری نکرده‌اید. لطفا حداقل یک تصویر بارگذاری کنید.",
                    reply_to_message_id=update.effective_message.id,
                )
                return self.Step.PHOTO.value

            if self.vehicle_type == 'Car':
                text = "لطفا برند ماشین خود را وارد کنید(برای مثال پراید)"
            if self.vehicle_type == 'Motor':
                text = "لطفا برند موتور خود را وارد کنید(برای مثال هوندا)"

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text,
                reply_to_message_id=update.effective_message.id,
                reply_markup=BACK_KEYBOARD,
            )
            return self.Step.BRAND.value

        if update.message.photo:
            photo_file_id = update.message.photo[-1]
            context.user_data["photos"].append(photo_file_id)
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="لطفا یک تصویر ارسال کنید یا دکمه 'تمام' را برای ادامه فشار دهید.",
                reply_to_message_id=update.effective_message.id,
            )
        return self.Step.PHOTO.value

    async def brand_message_handler(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data["brand"] = update.effective_message.text
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="لطفا سال ساخت را تایپ کنید(به عدد وارد کنید)",
            reply_to_message_id=update.effective_message.id,
        )
        return self.Step.MODEL.value

    async def model_message_handler(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data["model"] = update.effective_message.text

        if self.vehicle_type == 'Car':
            text = "لطفا رنگ ماشین را تایپ کنید"
        if self.vehicle_type == 'Motor':
            text = "لطفا رنگ موتور را تایپ کنید"

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_to_message_id=update.effective_message.id,
        )
        return self.Step.COLOR.value

    async def color_message_handler(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data["color"] = update.effective_message.text
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🔹 لطفاً میزان کارکرد را به هزار کیلومتر وارد کنید.\n✔ فقط عدد بنویسید.\n(مثال: ۲۰ یعنی ۲۰,۰۰۰ کیلومتر)\n\n📌 نمونه درست: ۲۰ \n🚫 نمونه نادرست: ۲۰ هزار یا بیست هزار کیلومتر\n\n✅ نیازی به نوشتن 'هزار' یا 'کیلومتر' نیست، فقط عدد را وارد کنید.",
            reply_to_message_id=update.effective_message.id,
        )
        return self.Step.FUNCTION.value

    async def function_message_handler(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data["function"] = update.effective_message.text
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🔹 لطفاً تعداد ماه‌های بیمه را وارد کنید.\n✔ فقط عدد بنویسید.\n(مثال: ۲ یعنی ۲ ماه بیمه)\n\n📌 نمونه درست: ۲ \n🚫 نمونه نادرست: ۲ ماه یا دو ماه\n\n✅ نیازی به نوشتن 'ماه' نیست، فقط عدد را وارد کنید.",
            reply_to_message_id=update.effective_message.id,
        )
        return self.Step.INSURANCE.value

    async def insurance_message_handler(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data["insurance"] = update.effective_message.text
        keyboard = [
            [
                InlineKeyboardButton("دارد", callback_data="دارد"),
                InlineKeyboardButton("ندارد", callback_data="ندارد"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("معاوضه ؟", reply_markup=reply_markup)
        return self.Step.EXCHANGE.value

    async def choice_exchange_message_handler(
            self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()

        # write your code here
        context.user_data["exchange"] = query.data
        await query.edit_message_text(text=f"{query.data}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                "🔹 لطفاً قیمت را به تومان وارد کنید.\n"
                "✔ عدد را **همراه با واحد** بنویسید.\n\n"
                "مثلاً اگر قیمت ۲۰۰ میلیون تومان است، بنویسید:\n"
                "📌 ۲۰۰ میلیون تومان\n\n"
                "🚫 ننویسید فقط «۲۰۰» یا «۲۰۰۰۰۰۰۰۰» یا «دویست»\n\n"
                "✅ حتماً واحدی مثل «میلیون تومان» یا «تومان» را در عدد وارد کنید."
            ),
            reply_to_message_id=update.effective_message.id

        )
        return self.Step.MONEY.value

    # endregion

    async def send_advertisement_info_to_user(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE,
            user_id,
            adv_obj):
        description = self.generate_advertisement_info_format(
            advertisement_id=adv_obj.adv_id,
            advertisement_type=adv_obj.advertisement_type,
            vehicle_type=adv_obj.vehicle_type,
            brand=adv_obj.brand,
            model=adv_obj.model,
            function=adv_obj.function,
            insurance=adv_obj.insurance,
            exchange=adv_obj.exchange,
            money=adv_obj.money,
            body=adv_obj.body,
            chassis=adv_obj.chassis,
            motor=adv_obj.motor,
            technical=adv_obj.technical,
            gearbox=adv_obj.gearbox
        )
        # دریافت لیست عکس‌ها از مدل آگهی
        photos = [os.path.join(BASE_PATH, photo.photo_path)
                  for photo in adv_obj.photos]
        media_group = []

        # Add first photo with caption
        try:
            with open(photos[0], 'rb') as first_photo:
                media_group.append(
                    InputMediaPhoto(
                        media=first_photo,
                        caption=description,
                        parse_mode='HTML'  # Allows bold/formatting
                    )
                )
        except FileNotFoundError:
            await update.message.reply_text("Error: First photo not found!")
            return

        # Add remaining photos
        for path in photos[1:]:
            try:
                with open(path, 'rb') as photo:
                    media_group.append(InputMediaPhoto(media=photo))
            except FileNotFoundError:
                continue  # Skip missing photos

        # Send the media group
        await context.bot.send_media_group(
            chat_id=user_id,
            media=media_group
        )

    async def handle_approval_common(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        extra_fields: dict = None,
    ):
        query = update.callback_query
        await query.answer()
        response = query.data
        user_id = update.effective_user.id
        vehicle_type = self.vehicle_type
        advertisement_type = context.user_data['advertisement_type']

        non_descriptive_fields = {
            "user_id": user_id,
            "photos": context.user_data["photos"]
        }

        description_fields = {
            "vehicle_type": vehicle_type,
            "advertisement_type": advertisement_type,
            "brand": context.user_data["brand"],
            "model": context.user_data["model"],
            "function": context.user_data["function"],
            "insurance": context.user_data["insurance"],
            "exchange": context.user_data["exchange"],
            "money": context.user_data["money"],
        }

        advertisement_fields = {**description_fields, **non_descriptive_fields}
        if extra_fields:
            advertisement_fields.update(extra_fields)
            description_fields.update(extra_fields)

        if response == "✅ تأیید اطلاعات":
            new_adv = await self.adv_db.add_advertisement(**advertisement_fields)

            description = self.generate_advertisement_info_format(
                advertisement_id=new_adv.adv_id, **description_fields
            )

            media_group = [
                InputMediaPhoto(photo, caption=description if i == 0 else None)
                for i, photo in enumerate(advertisement_fields["photos"])
            ]
            await context.bot.send_media_group(
                chat_id=CHANELL_USERNAME,
                media=media_group,
            )
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="اطلاعات با موفقیت ثبت و در کانال قرار گرفت.",
                reply_to_message_id=update.effective_message.id,
                reply_markup=HOME_BOT_KEYBOARD,
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="دوباره تلاش کنید",
                reply_to_message_id=update.effective_message.id,
                reply_markup=HOME_BOT_KEYBOARD,
            )
        await query.edit_message_text(text=response)
        return ConversationHandler.END

    async def cancel_command_handler(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE) -> int:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="عملیات ثبت آگهی لغو شد",
            reply_to_message_id=update.effective_message.id,
            reply_markup=VEHICLE_KEYBOARD,
        )
        return ConversationHandler.END

    # step and filters
    def photo_step_handler(self):
        return MessageHandler(
            (~self.RETURN_FILTER) & (
                filters.PHOTO | filters.Regex(r"^تمام$") | filters.COMMAND),
            self.photo_message_handler)

    def brand_step_handler(self):
        return MessageHandler(
            filters.TEXT & ~filters.COMMAND & ~self.RETURN_FILTER,
            self.brand_message_handler)

    def model_step_handler(self):
        return MessageHandler(
            filters.TEXT & ~filters.COMMAND & ~self.RETURN_FILTER,
            self.model_message_handler)

    def color_step_handler(self):
        return MessageHandler(
            filters.TEXT & ~filters.COMMAND & ~self.RETURN_FILTER,
            self.color_message_handler)

    def function_step_handler(self):
        return MessageHandler(
            filters.TEXT & ~filters.COMMAND & ~self.RETURN_FILTER,
            self.function_message_handler)

    def insurance_step_handler(self):
        return MessageHandler(
            filters.TEXT & ~filters.COMMAND & ~self.RETURN_FILTER,
            self.insurance_message_handler)

    def exchange_step_handler(self):
        return CallbackQueryHandler(
            self.choice_exchange_message_handler
        )

    def cancel_step_handler(self):
        return MessageHandler(
            self.RETURN_FILTER, self.cancel_command_handler
        )

    def get_handlers(self):
        return [
            MessageHandler(
                filters.Regex(r"^ثبت تبلیغ جدید$"),
                self.start_init_vehicle_menue),
        ]
