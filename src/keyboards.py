
from telegram import (
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup
)

from constants import (
    RETURN_MESSAGE_BUTTON,
    HELP_TEXT_BUTTON,
    MY_ADVERTISMENT_LIST_TEXT_BUTTON,
    SUBMIT_NEW_USER_BUTTON
)
# region common

BACK_KEYBOARD = ReplyKeyboardMarkup([[InlineKeyboardButton(
    text=RETURN_MESSAGE_BUTTON, callback_data='back_to_menu')]], resize_keyboard=True)
# endregion

# region user

USER_KEYBOARD = ReplyKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text="مشاهده اطلاعات پروفایل", callback_data='submit_motor'),
            InlineKeyboardButton(text=SUBMIT_NEW_USER_BUTTON, callback_data='submit_car')
        ],
        [
            InlineKeyboardButton(text="تغییر اطلاعات", callback_data='submit_motor')
        ],
        [
            InlineKeyboardButton(text=RETURN_MESSAGE_BUTTON, callback_data='back_to_menu')
        ]
    ]
)

CHANGE_USER_INFO_KEYBOARD = ReplyKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text="تغییر نام‌کاربری", callback_data='back_to_menu'),
            InlineKeyboardButton(text="تغییر نام و نام خانوادگی", callback_data='back_to_menu'),

        ],
        [
            InlineKeyboardButton(text="تغییر تلفن همراه", callback_data='back_to_menu'),
        ],
        [
            InlineKeyboardButton(text=RETURN_MESSAGE_BUTTON, callback_data='back_to_menu')
        ]
    ],
    resize_keyboard=True
)
# endregion

# region bot

HOME_BOT_KEYBOARD = ReplyKeyboardMarkup([
    [
        InlineKeyboardButton(text=MY_ADVERTISMENT_LIST_TEXT_BUTTON, callback_data='submit_car'),
        InlineKeyboardButton(text="ثبت تبلیغ جدید", callback_data='submit_motor')
    ],
    [InlineKeyboardButton(text="تنظیمات کاربری", callback_data='submit_motor')],
    [InlineKeyboardButton(text=HELP_TEXT_BUTTON, callback_data='help_command_handler')],
]
)
# endregion


# region vehicle

VEHICLE_KEYBOARD = ReplyKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text="🔴 فروش ماشین", callback_data='submit_car'),
            InlineKeyboardButton(text="🔵 خرید ماشین", callback_data='submit_motor')
        ],
        [
            InlineKeyboardButton(text="🔴 فروش موتور", callback_data='submit_bike'),
            InlineKeyboardButton(text="🔵 خرید موتور", callback_data='submit_bike_buy')
        ],
        [
            InlineKeyboardButton(text=RETURN_MESSAGE_BUTTON, callback_data='back_to_menu')
        ]
    ]
)
# endregion


APPROVE_KEYBOARD = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("✅ تأیید اطلاعات", callback_data="✅ تأیید اطلاعات")
        ],
        [
            InlineKeyboardButton("❌ اطلاعات نادرست است", callback_data="❌ اطلاعات نادرست است")
        ]

    ]
)
