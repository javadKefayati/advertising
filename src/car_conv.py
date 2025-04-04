from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto
)
import os
from dotenv import load_dotenv
from vehicle import Vehicle
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    filters,
    MessageHandler,
    CallbackQueryHandler
)
from keyboards import (
    APPROVE_KEYBOARD
)

load_dotenv()  # take environment variables from .env.

CHANELL_ID = os.getenv("CHANELL_ID")


class Car(Vehicle):

    async def money_message_handler(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE):

        context.user_data["money"] = update.effective_message.text

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

        return self.Step.BODY.value

    async def body_message_handler(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE):
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
        return self.Step.CHASSIS.value

    async def chassis_message_handler(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE):
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
        return self.Step.TECHNICAL.value

    async def technical_message_handler(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        context.user_data["technical"] = query.data
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

        return self.Step.MOTOR.value

    async def motor_message_handler(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        context.user_data["motor"] = query.data

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
        return self.Step.GEARBOX.value

    async def gearbox_message_handler(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        context.user_data["gearbox"] = query.data
        await query.edit_message_text(text=f"{query.data}")

        vehicle_type = self.vehicle_type
        advertisement_type = context.user_data['advertisement_type']
        brand = context.user_data["brand"]
        model = context.user_data["model"]
        function = context.user_data["function"]
        insurance = context.user_data["insurance"]
        exchange = context.user_data["exchange"]
        money = context.user_data["money"]
        body = context.user_data['body']
        chassis = context.user_data['chassis']
        motor = context.user_data['motor']
        technical = context.user_data['technical']
        gearbox = context.user_data['gearbox']
        photos = context.user_data["photos"]

        description = self.generate_advertisement_info_format(
            vehicle_type=vehicle_type,
            advertisement_type=advertisement_type,
            brand=brand,
            model=model,
            function=function,
            insurance=insurance,
            exchange=exchange,
            money=money,
            body=body,
            chassis=chassis,
            motor=motor,
            technical=technical,
            gearbox=gearbox
        )

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
        return self.Step.APPROVE.value

    async def approve_handler(self, update, context):
        extra_fields = {
            "body": context.user_data['body'],
            "chassis": context.user_data['chassis'],
            "motor": context.user_data['motor'],
            "technical": context.user_data['technical'],
            "gearbox": context.user_data['gearbox'],
        }
        return await self.handle_approval_common(update, context, extra_fields)

    def get_handlers(self):
        return [
            ConversationHandler(
                entry_points=[
                    MessageHandler(
                        # Matches either phrase exactly
                        filters.Regex(r"^(🔵 خرید ماشین|🔴 فروش ماشین)$"),
                        self.vehicle_init_message_handler
                    )
                ],
                states={
                    self.Step.PHOTO.value: [
                        self.photo_step_handler()
                    ],
                    self.Step.BRAND.value: [
                        self.brand_step_handler()
                    ],
                    self.Step.MODEL.value: [
                        self.model_step_handler()
                    ],
                    self.Step.COLOR.value: [
                        self.color_step_handler()
                    ],
                    self.Step.FUNCTION.value: [
                        self.function_step_handler()
                    ],
                    self.Step.INSURANCE.value: [
                        self.insurance_step_handler()
                    ],
                    self.Step.EXCHANGE.value: [
                        self.exchange_step_handler()
                    ],
                    self.Step.MONEY.value: [
                        MessageHandler(
                            filters.TEXT & ~filters.COMMAND &
                            ~self.RETURN_FILTER,
                            self.money_message_handler
                        )
                    ],
                    self.Step.BODY.value: [
                        CallbackQueryHandler(
                            self.body_message_handler
                        )
                    ],
                    self.Step.CHASSIS.value: [
                        CallbackQueryHandler(
                            self.chassis_message_handler
                        )
                    ],
                    self.Step.TECHNICAL.value: [
                        CallbackQueryHandler(
                            self.technical_message_handler
                        )
                    ],
                    self.Step.MOTOR.value: [
                        CallbackQueryHandler(
                            self.motor_message_handler
                        )
                    ],
                    self.Step.GEARBOX.value: [
                        CallbackQueryHandler(
                            self.gearbox_message_handler
                        )
                    ],
                    self.Step.APPROVE.value: [
                        CallbackQueryHandler(
                            self.approve_handler
                        )
                    ]
                },
                fallbacks=[
                    self.cancel_step_handler()
                ],
                allow_reentry=True,
            )
        ]
