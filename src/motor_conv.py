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

    async def money_message_handler(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data["money"] = update.effective_message.text

        vehicle_type = self.vehicle_type
        advertisement_type = context.user_data['advertisement_type']
        brand = context.user_data["brand"]
        model = context.user_data["model"]
        function = context.user_data["function"]
        insurance = context.user_data["insurance"]
        exchange = context.user_data["exchange"]
        money = context.user_data["money"]
        photos = context.user_data["photos"]

        description = self.generate_advertisement_info_format(
            vehicle_type=vehicle_type,
            advertisement_type=advertisement_type,
            brand=brand,
            model=model,
            function=function,
            insurance=insurance,
            exchange=exchange,
            money=money
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

    async def approve_handler(self,
                              update: Update,
                              context: ContextTypes.DEFAULT_TYPE):
        return await self.handle_approval_common(update, context)

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
                        self.cancel_step_handler()
                    ],
                    allow_reentry=True,
                )
                ]
