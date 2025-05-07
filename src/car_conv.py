from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto
)
import os
from dotenv import load_dotenv
from vehicle import Vehicle
import inspect
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
    def __init__(self):
        super().__init__()
        self.FLOW_CONFIGS = {
            "sale":{
                "vehicle_init_message_handler":{
                    "NEXT_STATE_MESSAGE_FUNC": self.send_photo_pre_state_message,
                    "NEXT_STATE_RETURN_VALUE": self.Step.PHOTO.value
                },
                "photo_message_handler":{
                    "NEXT_STATE_MESSAGE_FUNC": self.send_brand_pre_state_message,
                    "NEXT_STATE_RETURN_VALUE": self.Step.BRAND.value
                },
                "brand_message_handler":{
                    "NEXT_STATE_MESSAGE_FUNC": self.send_model_pre_state_message,
                    "NEXT_STATE_RETURN_VALUE": self.Step.MODEL.value
                },
                "model_message_handler":{
                    "NEXT_STATE_MESSAGE_FUNC": self.send_color_pre_state_message,
                    "NEXT_STATE_RETURN_VALUE": self.Step.COLOR.value
                },
                "color_message_handler":{
                    "NEXT_STATE_MESSAGE_FUNC": self.send_function_pre_state_message,
                    "NEXT_STATE_RETURN_VALUE": self.Step.FUNCTION.value
                },
                "function_message_handler":{
                    "NEXT_STATE_MESSAGE_FUNC": self.send_insurance_pre_state_message,
                    "NEXT_STATE_RETURN_VALUE": self.Step.INSURANCE.value
                },
                "insurance_message_handler":{
                    "NEXT_STATE_MESSAGE_FUNC": self.send_exchange_pre_state_message,
                    "NEXT_STATE_RETURN_VALUE": self.Step.EXCHANGE.value
                },
                "exchange_message_handler":{
                    "NEXT_STATE_MESSAGE_FUNC": self.send_money_pre_state_message,
                    "NEXT_STATE_RETURN_VALUE": self.Step.MONEY.value,
                },
                "money_message_handler":{
                    "NEXT_STATE_MESSAGE_FUNC": self.send_body_pre_state_message,
                    "NEXT_STATE_RETURN_VALUE": self.Step.BODY.value,
                },
                "body_message_handler":{
                    "NEXT_STATE_MESSAGE_FUNC": self.send_chassis_pre_state_message,
                    "NEXT_STATE_RETURN_VALUE": self.Step.CHASSIS.value,
                },
                "chassis_message_handler":{
                    "NEXT_STATE_MESSAGE_FUNC": self.send_technical_pre_state_message,
                    "NEXT_STATE_RETURN_VALUE": self.Step.TECHNICAL.value,
                },
                "technical_message_handler":{
                    "NEXT_STATE_MESSAGE_FUNC": self.send_motor_pre_state_message,
                    "NEXT_STATE_RETURN_VALUE": self.Step.MOTOR.value,
                },
                "motor_message_handler":{
                    "NEXT_STATE_MESSAGE_FUNC": self.send_gearbox_pre_state_message,
                    "NEXT_STATE_RETURN_VALUE": self.Step.GEARBOX.value,
                },
                "gearbox_message_handler":{
                    "NEXT_STATE_MESSAGE_FUNC": self.send_approve_pre_state_message,
                    "NEXT_STATE_RETURN_VALUE": self.Step.APPROVE.value,
                },
                # Approve is end of any converstion
                },
            "shop":{                
                "vehicle_init_message_handler":{
                    "NEXT_STATE_MESSAGE_FUNC": self.send_brand_pre_state_message,
                    "NEXT_STATE_RETURN_VALUE": self.Step.BRAND.value
                },
                "brand_message_handler":{
                    "NEXT_STATE_MESSAGE_FUNC": self.send_color_pre_state_message,
                    "NEXT_STATE_RETURN_VALUE": self.Step.COLOR.value
                },
                "color_message_handler":{
                    "NEXT_STATE_MESSAGE_FUNC": self.send_money_pre_state_message,
                    "NEXT_STATE_RETURN_VALUE": self.Step.MONEY.value
                },
                "money_message_handler":{
                    "NEXT_STATE_MESSAGE_FUNC": self.send_more_detail_pre_state_message,
                    "NEXT_STATE_RETURN_VALUE": self.Step.MORE_DETAIL.value
                },
                "more_detail_message_handler":{
                    "NEXT_STATE_MESSAGE_FUNC": self.send_gearbox_pre_state_message,
                    "NEXT_STATE_RETURN_VALUE": self.Step.GEARBOX.value,
                },
                "gearbox_message_handler":{
                    "NEXT_STATE_MESSAGE_FUNC": self.send_approve_pre_state_message,
                    "NEXT_STATE_RETURN_VALUE": self.Step.APPROVE.value,
                },
                # Approve is end of any converstion
                }

        }
    async def money_message_handler(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE):

        context.user_data["money"] = update.effective_message.text

        next_step = await self.run_pre_state_message_func_and_get_next_state(       methode_name=inspect.currentframe().f_code.co_name,
            update=update,
            context=context,
            advertisement_type=context.user_data["advertisement_type"]
        )
        return next_step


    async def body_message_handler(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        context.user_data["body"] = query.data
        await query.edit_message_text(text=f"{query.data}")

        next_step = await self.run_pre_state_message_func_and_get_next_state(
            methode_name=inspect.currentframe().f_code.co_name,
            update=update,
            context=context,
            advertisement_type=context.user_data["advertisement_type"]
        )
        return next_step

    async def chassis_message_handler(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        context.user_data["chassis"] = query.data
        await query.edit_message_text(text=f"{query.data}")

        next_step = await self.run_pre_state_message_func_and_get_next_state(
            methode_name=inspect.currentframe().f_code.co_name,
            update=update,
            context=context,
            advertisement_type=context.user_data["advertisement_type"]
        )
        return next_step

    async def technical_message_handler(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        context.user_data["technical"] = query.data
        await query.edit_message_text(text=f"{query.data}")

        next_step = await self.run_pre_state_message_func_and_get_next_state(
            methode_name=inspect.currentframe().f_code.co_name,
            update=update,
            context=context,
            advertisement_type=context.user_data["advertisement_type"]
        )
        return next_step

    async def motor_message_handler(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        context.user_data["motor"] = query.data

        await query.edit_message_text(text=f"{query.data}")

        next_step = await self.run_pre_state_message_func_and_get_next_state(
            methode_name=inspect.currentframe().f_code.co_name,
            update=update,
            context=context,
            advertisement_type=context.user_data["advertisement_type"]
        )
        return next_step

    async def gearbox_message_handler(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        context.user_data["gearbox"] = query.data
        await query.edit_message_text(text=f"{query.data}")

        next_step = await self.run_pre_state_message_func_and_get_next_state(
            methode_name=inspect.currentframe().f_code.co_name,
            update=update,
            context=context,
            advertisement_type=context.user_data["advertisement_type"]
        )
        return next_step


    async def approve_handler(self, update, context):
        user_id = update.effective_user.id
        vehicle_type = self.vehicle_type
        advertisement_type = context.user_data['advertisement_type']

        if context.user_data['advertisement_type'] == 'sale':
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
                "body": context.user_data['body'],
                "chassis": context.user_data['chassis'],
                "motor": context.user_data['motor'],
                "technical": context.user_data['technical'],
                "gearbox": context.user_data['gearbox'],
                "color": context.user_data["color"]
            }
        if context.user_data['advertisement_type'] == 'shop':
            non_descriptive_fields = {
                "user_id": user_id
            }
            description_fields = {
                "vehicle_type": vehicle_type,
                "advertisement_type": advertisement_type,
                "brand": context.user_data["brand"],
                "color": context.user_data["color"],
                "money": context.user_data["money"],
                "gearbox": context.user_data['gearbox'],
                "more_detail": context.user_data["more_detail"],

                }
        return await self.handle_approval_common(
            update=update,
            context=context,
            description_fields=description_fields,
            non_descriptive_fields=non_descriptive_fields)


    # region pre states message
    async def send_gearbox_pre_state_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ):
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

    async def send_body_pre_state_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ):
        keyboard = [
            [InlineKeyboardButton("سالم و بی‌خط و خش", callback_data="سالم و بی‌خط و خش")],
            [InlineKeyboardButton("خط و خش جزیی", callback_data="خط و خش جزیی")],
            [InlineKeyboardButton("صافکاری بی‌رنگ", callback_data="صافکاری بی‌رنگ")],
            [InlineKeyboardButton("رنگ شدگی", callback_data="رنگ شدگی")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="وضعیت بدنه ؟",
            reply_markup=reply_markup
        )


    async def send_chassis_pre_state_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ):
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

    async def send_technical_pre_state_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ):
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

    async def send_motor_pre_state_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ):
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

    # endregion

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
                        self.photo_state_handler()
                    ],
                    self.Step.BRAND.value: [
                        self.brand_state_handler()
                    ],
                    self.Step.MODEL.value: [
                        self.model_state_handler()
                    ],
                    self.Step.COLOR.value: [
                        self.color_state_handler()
                    ],
                    self.Step.FUNCTION.value: [
                        self.function_state_handler()
                    ],
                    self.Step.INSURANCE.value: [
                        self.insurance_state_handler()
                    ],
                    self.Step.EXCHANGE.value: [
                        self.exchange_state_handler()
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
                    self.Step.MORE_DETAIL.value: [
                            self.more_detail_state_handler()
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
                    self.cancel_state_handler()
                ],
                allow_reentry=True
                )
        ]
