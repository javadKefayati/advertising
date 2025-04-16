from abc import ABC
from typing import Optional, List, Tuple
from enum import Enum, auto
import os
import inspect

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
    UNREGISTERED_USER_TEXT,
    SUPPORT_USERNAMES,
    DEFAULT_PICT_PATH
)
from keyboards import (
    VEHICLE_KEYBOARD,
    BACK_KEYBOARD,
    HOME_BOT_KEYBOARD,
    USER_KEYBOARD,
    APPROVE_KEYBOARD
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
    FLOW_CONFIGS = {}
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
        bot_username: str,
        advertisement_id: Optional[int] = None,
        advertisement_type: Optional[str] = None,
        vehicle_type: Optional[str] = None,
        **kwargs
    ) -> str:
        # Static mappings
        type_labels = {
            'shop': '🔵 آگهی خرید\n',
            'sale': '🔴 آگهی فروش\n'
        }

        vehicle_labels = {
            'Car': '🚗 نوع: ماشین',
            'Motor': '🛵 نوع: موتور'
        }

        field_templates: List[Tuple[str, str]] = [
            ('brand', '🏷  برند:  {}'),
            ('model', '📅  مدل:  {}'),
            ('function', '🔄  کارکرد:  {} هزار کیلومتر'),
            ('insurance', '🛡  بیمه:  {} ماه'),
            ('exchange', '🔄  معاوضه:  {}'),
            ('money', '💰  قیمت:  {}'),
            ('body', '🚗  وضعیت بدنه:  {}'),
            ('chassis', '🛠  وضعیت شاسی:  {}'),
            ('motor', '⚙  وضعیت موتور:  {}'),
            ('technical', '✅  معاینه فنی:  {}'),
            ('gearbox', '⚡  نوع گیربکس:  {}'),
            ('color', '🎨  رنگ:  {}'),
        ]

        description_parts = []

        # Add advertisement type
        if advertisement_type and advertisement_type in type_labels:
            description_parts.append(type_labels[advertisement_type])

        # Add vehicle type
        if vehicle_type and vehicle_type in vehicle_labels:
            description_parts.append(vehicle_labels[vehicle_type])

        # Override templates for 'color' and 'money' if advertisement_type is 'shop'
        updated_templates = []
        for key, template in field_templates:
            if key == 'color' and 'color' in kwargs:
                if advertisement_type == 'shop':
                    template = "🎨  رنگ ترجیحی: {}"
            elif key == 'money' and 'money' in kwargs:
                if advertisement_type == 'shop':
                    template = "💰  حداکثر قیمت:  {}"
            updated_templates.append((key, template))

        # Generate final lines
        for key, template in updated_templates:
            value = kwargs.get(key)
            if value:
                description_parts.append(template.format(value))

        # Final composition
        description = '\n'.join(description_parts)

        if advertisement_id:
            description = f"🔹 آگهی شماره: {advertisement_id}\n\n" + description
        else:
            description = "\n\n" + description

        if SUPPORT_USERNAMES:
            description += "\n\n👤 برای خرید یا فروش به آی‌دی‌های زیر پیام بدهید:"
            description += '\n' + '\n'.join(f"@{username}" for username in SUPPORT_USERNAMES)

        description += f"\n\n\n📌 آدرس کانال: {CHANELL_USERNAME}"
        
        bot_username_text = f"@{bot_username}"

        description += f"\n🤖 ثبت آگهی جدید: {bot_username_text}"
        return description


    def check_sale_or_shop(self, text):
        if text and "فروش" in text:
            vehicle_type = "sale"
        else:
            vehicle_type = "shop"

        return vehicle_type
    
    async def run_pre_state_message_func_and_get_next_state(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        methode_name:str,
        advertisement_type:str
        ):
        NEXT_STATE_MESSAGE_FUNC = self.FLOW_CONFIGS[advertisement_type][methode_name]["NEXT_STATE_MESSAGE_FUNC"]
        await NEXT_STATE_MESSAGE_FUNC(
            update=update,
            context=context
        )
        return self.FLOW_CONFIGS[advertisement_type][methode_name]["NEXT_STATE_RETURN_VALUE"]


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
        next_step = await self.run_pre_state_message_func_and_get_next_state(        methode_name=inspect.currentframe().f_code.co_name,
            update=update,
            context=context,
            advertisement_type=context.user_data["advertisement_type"]
        )
        return next_step

    async def photo_message_handler(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE) -> int:
        if update.message.text == 'تمام':
            if not context.user_data.get("photos", False):
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="شما هیچ تصویری بارگذاری نکرده‌اید. لطفا حداقل یک تصویر بارگذاری کنید.",
                    reply_to_message_id=update.effective_message.id,
                )
                return self.Step.PHOTO.value

            next_step = await self.run_pre_state_message_func_and_get_next_state(                methode_name=inspect.currentframe().f_code.co_name,
                update=update,
                context=context,
                advertisement_type=context.user_data["advertisement_type"]

            )
            return next_step

        if update.message.photo:
            context.user_data.setdefault("photos", [])
            photo_file_id = update.message.photo[-1]
            context.user_data["photos"].append(photo_file_id)

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

        next_step = await self.run_pre_state_message_func_and_get_next_state(       methode_name=inspect.currentframe().f_code.co_name,
            update=update,
            context=context, advertisement_type=context.user_data["advertisement_type"]
        )
        return next_step


    async def model_message_handler(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data["model"] = update.effective_message.text

        next_step = await self.run_pre_state_message_func_and_get_next_state(       methode_name=inspect.currentframe().f_code.co_name,
            update=update,
            context=context,
            advertisement_type=context.user_data["advertisement_type"]
        )
        return next_step


    async def color_message_handler(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data["color"] = update.effective_message.text

        next_step = await self.run_pre_state_message_func_and_get_next_state(
            methode_name=inspect.currentframe().f_code.co_name,
            update=update,
            context=context,
            advertisement_type=context.user_data["advertisement_type"]
        )
        return next_step

    async def function_message_handler(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data["function"] = update.effective_message.text
        next_step = await self.run_pre_state_message_func_and_get_next_state(       methode_name=inspect.currentframe().f_code.co_name,
            update=update,
            context=context,
            advertisement_type=context.user_data["advertisement_type"]
        )
        return next_step

    async def insurance_message_handler(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data["insurance"] = update.effective_message.text
        next_step = await self.run_pre_state_message_func_and_get_next_state(       methode_name=inspect.currentframe().f_code.co_name,
            update=update,
            context=context,
            advertisement_type=context.user_data["advertisement_type"]
        )
        return next_step

    async def exchange_message_handler(
            self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()

        # write your code here
        context.user_data["exchange"] = query.data
        await query.edit_message_text(text=f"{query.data}")
        next_step = await self.run_pre_state_message_func_and_get_next_state(       methode_name=inspect.currentframe().f_code.co_name,
            update=update,
            context=context,
            advertisement_type=context.user_data["advertisement_type"]
        )
        return next_step

    # endregion

    async def send_advertisement_info_to_user(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE,
            user_id,
            adv_obj):
        description = self.generate_advertisement_info_format(
            bot_username=context.bot.username,
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


    def cleaning_user_data_cache(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        context.user_data.clear()


    async def handle_approval_common(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        non_descriptive_fields: dict,
        description_fields: dict
    ):

        query = update.callback_query
        await query.answer()
        response = query.data
        user_id = update.effective_user.id
        vehicle_type = self.vehicle_type
        advertisement_type = context.user_data['advertisement_type']

        advertisement_fields = {**description_fields, **non_descriptive_fields}

        
        if response == "✅ تأیید اطلاعات":
            new_adv = await self.adv_db.add_advertisement(
                default_photo=context.user_data.get('default_photo',''),
                **advertisement_fields)

            description = self.generate_advertisement_info_format(
                bot_username=context.bot.username,
                advertisement_id=new_adv.adv_id, **description_fields
            )
            default_photo = context.user_data.get('default_photo','')
            media_group = []
            if default_photo:
                with open(default_photo, 'rb') as first_photo:
                    media_group.append(
                        InputMediaPhoto(
                            media=first_photo,
                            caption=description,
                            parse_mode='HTML'
                        )
                    )
            else:
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
        self.cleaning_user_data_cache(
            update=update,
            context=context
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
    def photo_state_handler(self):
        return MessageHandler(
            (~self.RETURN_FILTER) & (
                filters.PHOTO | filters.Regex(r"^تمام$") | filters.COMMAND),
            self.photo_message_handler)

    def brand_state_handler(self):
        return MessageHandler(
            filters.TEXT & ~filters.COMMAND & ~self.RETURN_FILTER,
            self.brand_message_handler)

    def model_state_handler(self):
        return MessageHandler(
            filters.TEXT & ~filters.COMMAND & ~self.RETURN_FILTER,
            self.model_message_handler)

    def color_state_handler(self):
        return MessageHandler(
            filters.TEXT & ~filters.COMMAND & ~self.RETURN_FILTER,
            self.color_message_handler)

    def function_state_handler(self):
        return MessageHandler(
            filters.TEXT & ~filters.COMMAND & ~self.RETURN_FILTER,
            self.function_message_handler)

    def insurance_state_handler(self):
        return MessageHandler(
            filters.TEXT & ~filters.COMMAND & ~self.RETURN_FILTER,
            self.insurance_message_handler)

    def exchange_state_handler(self):
        return CallbackQueryHandler(
            self.exchange_message_handler
        )

    def cancel_state_handler(self):
        return MessageHandler(
            self.RETURN_FILTER, self.cancel_command_handler
        )
    
    async def send_photo_pre_state_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ):
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

    async def send_brand_pre_state_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ):
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

    async def send_model_pre_state_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="لطفا سال ساخت را تایپ کنید(به عدد وارد کنید)",
            reply_to_message_id=update.effective_message.id,
        )


    async def send_color_pre_state_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ):
        advertisement_type = context.user_data.get("advertisement_type")
        if advertisement_type == 'sale':
            color_text = 'رنگ'
        if advertisement_type == 'shop':
            color_text = 'رنگ ترجیحی'

        if self.vehicle_type == 'Car':
            text = f"لطفا {color_text} ماشین را تایپ کنید"
        if self.vehicle_type == 'Motor':
            text = f"لطفا {color_text} موتور را تایپ کنید"

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_to_message_id=update.effective_message.id,
        )


    async def send_function_pre_state_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🔹 لطفاً میزان کارکرد را به هزار کیلومتر وارد کنید.\n✔ فقط عدد بنویسید.\n(مثال: ۲۰ یعنی ۲۰,۰۰۰ کیلومتر)\n\n📌 نمونه درست: ۲۰ \n🚫 نمونه نادرست: ۲۰ هزار یا بیست هزار کیلومتر\n\n✅ نیازی به نوشتن 'هزار' یا 'کیلومتر' نیست، فقط عدد را وارد کنید.",
            reply_to_message_id=update.effective_message.id,
        )


    async def send_insurance_pre_state_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🔹 لطفاً تعداد ماه‌های بیمه را وارد کنید.\n✔ فقط عدد بنویسید.\n(مثال: ۲ یعنی ۲ ماه بیمه)\n\n📌 نمونه درست: ۲ \n🚫 نمونه نادرست: ۲ ماه یا دو ماه\n\n✅ نیازی به نوشتن 'ماه' نیست، فقط عدد را وارد کنید.",
            reply_to_message_id=update.effective_message.id,
        )


    async def send_exchange_pre_state_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ):
        keyboard = [
            [
                InlineKeyboardButton("دارد", callback_data="دارد"),
                InlineKeyboardButton("ندارد", callback_data="ندارد"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("معاوضه ؟", reply_markup=reply_markup)


    async def send_money_pre_state_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ):
        if context.user_data.get('advertisement_type','') == 'sale':
            text=(
                "🔹 لطفاً قیمت را به تومان وارد کنید.\n"
                "✔ عدد را **همراه با واحد** بنویسید.\n\n"
                "مثلاً اگر قیمت ۲۰۰ میلیون تومان است، بنویسید:\n"
                "📌 ۲۰۰ میلیون تومان\n\n"
                "🚫 ننویسید فقط «۲۰۰» یا «۲۰۰۰۰۰۰۰۰» یا «دویست»\n\n"
                "✅ حتماً واحدی مثل «میلیون تومان» یا «تومان» را در عدد وارد کنید."
            )
        if context.user_data.get('advertisement_type','') == 'shop':
            text=(
                "🔹 لطفاً حداکثر قیمت پیشنهادی را به تومان وارد کنید.\n"
                "✔ عدد را **همراه با واحد** بنویسید.\n\n"
                "مثلاً اگر حداکثر قیمت پیشنهادی ۲۰۰ میلیون تومان است، بنویسید:\n"
                "📌 ۲۰۰ میلیون تومان\n\n"
                "🚫 ننویسید فقط «۲۰۰» یا «۲۰۰۰۰۰۰۰۰» یا «دویست»\n\n"
                "✅ حتماً واحدی مثل «میلیون تومان» یا «تومان» را در عدد وارد کنید."
            )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_to_message_id=update.effective_message.id
        )


    def generate_descript_fildes(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        keys = ["brand", "model","function",
                "insurance","exchange","money",
                "body","chassis","motor",
                "technical", "gearbox",
                "color"
        ]

        infos = {
            key: context.user_data[key]
            for key in keys
            if key in context.user_data and context.user_data[key]
        }
        infos["vehicle_type"] = self.vehicle_type
        infos["advertisement_type"] = context.user_data['advertisement_type']
        return infos


    async def send_approve_pre_state_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ):
        infos = self.generate_descript_fildes(
            update=update,
            context=context
        )
        photos = context.user_data.get("photos")
        if not photos:
            default_photo_path = os.path.join(BASE_PATH, DEFAULT_PICT_PATH)
            if os.path.exists(default_photo_path):
                context.user_data['default_photo'] = default_photo_path

        description = self.generate_advertisement_info_format(
            bot_username=context.bot.username,
            **infos
        )
        media_group = []
        default_photo = context.user_data.get('default_photo','')
        if default_photo:
            with open(default_photo, 'rb') as first_photo:
                media_group.append(
                    InputMediaPhoto(
                        media=first_photo,
                        caption=description,
                        parse_mode='HTML'  # Allows bold/formatting
                    )
                )
        else:
            media_group = [
                InputMediaPhoto(photo, caption=description if i == 0 else None)
                for i, photo in enumerate(photos)
            ]

        await context.bot.send_media_group(
            chat_id=update.effective_chat.id,
            media=media_group
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="آیا اطلاعات بالا صحیح است؟",
            reply_markup=APPROVE_KEYBOARD
        )


    def get_handlers(self):
        return [
            MessageHandler(
                filters.Regex(r"^ثبت تبلیغ جدید$"),
                self.start_init_vehicle_menue),
        ]
