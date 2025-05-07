import inspect
from telegram import (
    Update,
    InputMediaPhoto
)
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

from vehicle import Vehicle


class Motor(Vehicle):

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
                    "NEXT_STATE_MESSAGE_FUNC": self.send_more_detail_pre_state_message,
                    "NEXT_STATE_RETURN_VALUE": self.Step.MORE_DETAIL.value
                },
                "more_detail_message_handler":{
                    "NEXT_STATE_MESSAGE_FUNC": self.send_money_pre_state_message,
                    "NEXT_STATE_RETURN_VALUE": self.Step.MONEY.value
                },
                "money_message_handler":{
                    "NEXT_STATE_MESSAGE_FUNC": self.send_approve_pre_state_message,
                    "NEXT_STATE_RETURN_VALUE": self.Step.APPROVE.value,
                },
                # Approve is end of any converstion
                }

        }

    async def money_message_handler(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data["money"] = update.effective_message.text

        next_step = await self.run_pre_state_message_func_and_get_next_state(       methode_name=inspect.currentframe().f_code.co_name,
            update=update,
            context=context, advertisement_type=context.user_data["advertisement_type"]
        )
        return next_step

    async def approve_handler(self,
                              update: Update,
                              context: ContextTypes.DEFAULT_TYPE):

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
                "color": context.user_data["insurance"],
                "exchange": context.user_data["exchange"],
                "money": context.user_data["money"],
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
                "more_detail": context.user_data["more_detail"],
                }
        return await self.handle_approval_common(
            update=update,
            context=context,
            description_fields=description_fields,
            non_descriptive_fields=non_descriptive_fields)

   
    def get_handlers(self):
        return [ConversationHandler
                (
                    entry_points=[
                        MessageHandler(
                            filters.Regex(r"^(🔴 فروش موتور|🔵 خرید موتور)$"),
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
                        self.Step.MORE_DETAIL.value: [
                            self.more_detail_state_handler()
                        ],
                        self.Step.MONEY.value: [
                            MessageHandler(
                                filters.TEXT & ~filters.COMMAND & ~self.RETURN_FILTER, self.money_message_handler
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
