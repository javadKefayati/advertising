# test_vehicle.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update, Message, Chat, PhotoSize
from telegram.ext import CallbackContext
from vehicle_module import Vehicle
from constants import RETURN_MESSAGE_BUTTON
from enum import Enum

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def vehicle(mock_db):
    class ConcreteVehicle(Vehicle):
        FLOW_CONFIGS = {
            'sale': {
                'photo_message_handler': {
                    'NEXT_STATE_MESSAGE_FUNC': AsyncMock(),
                    'NEXT_STATE_RETURN_VALUE': 2
                },
                # Add other method configs as needed
            },
            'shop': {
                'photo_message_handler': {
                    'NEXT_STATE_MESSAGE_FUNC': AsyncMock(),
                    'NEXT_STATE_RETURN_VALUE': 2
                },
            }
        }
        adv_db = mock_db
    return ConcreteVehicle()

@pytest.fixture
def mock_update():
    update = AsyncMock(Update)
    message = AsyncMock(Message)
    chat = AsyncMock(Chat)
    chat.id = 123
    message.chat = chat
    message.text = "test"
    message.photo = [PhotoSize(file_id="photo1", width=100, height=100, file_unique_id="id1")]
    message.reply_to_message_id = None
    update.message = message
    update.effective_chat = chat
    update.effective_message = message
    update.effective_user.id = 123
    return update

@pytest.fixture
def mock_context():
    context = AsyncMock(CallbackContext)
    context.user_data = {}
    return context

@pytest.mark.asyncio
async def test_check_sale_or_shop(vehicle):
    assert vehicle.check_sale_or_shop("فروش ماشین") == "sale"
    assert vehicle.check_sale_or_shop("خرید ماشین") == "shop"
    assert vehicle.check_sale_or_shop("") == "shop"

@pytest.mark.asyncio
async def test_generate_advertisement_info_format(vehicle):
    result = vehicle.generate_advertisement_info_format(
        advertisement_type="sale",
        vehicle_type="Car",
        brand="پراید",
        model="۱۳۹۵",
        color="سفید"
    )
    assert "پراید" in result
    assert "۱۳۹۵" in result
    assert "سفید" in result

@pytest.mark.asyncio
async def test_photo_message_handler(vehicle, mock_update, mock_context):
    # Test with photo
    result = await vehicle.photo_message_handler(mock_update, mock_context)
    assert result == vehicle.Step.PHOTO.value
    assert "photos" in mock_context.user_data

    # Test with "تمام" command
    mock_update.message.text = "تمام"
    mock_update.message.photo = None
    result = await vehicle.photo_message_handler(mock_update, mock_context)
    assert result == 2  # NEXT_STATE_RETURN_VALUE from flow config

@pytest.mark.asyncio
async def test_brand_message_handler(vehicle, mock_update, mock_context):
    mock_context.user_data["advertisement_type"] = "sale"
    result = await vehicle.brand_message_handler(mock_update, mock_context)
    assert result == 2  # NEXT_STATE_RETURN_VALUE from flow config
    assert mock_context.user_data["brand"] == "test"

@pytest.mark.asyncio
async def test_more_detail_message_handler(vehicle, mock_update, mock_context):
    # Test with valid text
    mock_update.message.text = "توضیحات تست"
    result = await vehicle.more_detail_message_handler(mock_update, mock_context)
    assert mock_context.user_data["more_detail"] == "توضیحات تست"

    # Test with skip
    mock_update.message.text = SKIP_MESSAGE_BUTTON
    result = await vehicle.more_detail_message_handler(mock_update, mock_context)
    assert mock_context.user_data["more_detail"] == ""

@pytest.mark.asyncio
async def test_handle_approval_common(vehicle, mock_update, mock_context):
    mock_update.callback_query = AsyncMock()
    mock_update.callback_query.data = "✅ تأیید اطلاعات"
    mock_context.user_data["advertisement_type"] = "sale"
    
    with patch.object(vehicle.adv_db, 'add_advertisement', new_callable=AsyncMock) as mock_add:
        mock_add.return_value = MagicMock(adv_id=1)
        await vehicle.handle_approval_common(
            mock_update,
            mock_context,
            non_descriptive_fields={},
            description_fields={
                "advertisement_type": "sale",
                "vehicle_type": "Car",
                "brand": "Test"
            }
        )
        assert mock_add.called

@pytest.mark.asyncio
async def test_send_unregistered_user_message(vehicle, mock_update, mock_context):
    with patch.object(mock_context.bot, 'send_message') as mock_send:
        await vehicle.send_unregistered_user_message(mock_update, mock_context, "Test message")
        mock_send.assert_called_once()

def test_photo_state_handler(vehicle):
    handler = vehicle.photo_state_handler()
    assert handler.filters.name == "Regex('^تمام$') | (PHOTO & ~Regex('^بازگشت$')) | COMMAND"

def test_brand_state_handler(vehicle):
    handler = vehicle.brand_state_handler()
    assert handler.filters.name == "TEXT & ~COMMAND & ~Regex('^بازگشت$')"

@pytest.mark.asyncio
async def test_send_photo_pre_state_message(vehicle, mock_update, mock_context):
    with patch.object(mock_context.bot, 'send_message') as mock_send:
        await vehicle.send_photo_pre_state_message(mock_update, mock_context)
        mock_send.assert_called_once()

# Add similar tests for other pre-state message methods

@pytest.mark.asyncio
async def test_start_init_vehicle_menue(vehicle, mock_update, mock_context):
    # Test with unregistered user
    vehicle.adv_db.check_exist_user.return_value = False
    await vehicle.start_init_vehicle_menue(mock_update, mock_context)
    assert mock_context.bot.send_message.called

    # Test with registered user
    vehicle.adv_db.check_exist_user.return_value = True
    await vehicle.start_init_vehicle_menue(mock_update, mock_context)
    assert mock_update.message.reply_text.called

@pytest.mark.asyncio
async def test_vehicle_init_message_handler(vehicle, mock_update, mock_context):
    mock_update.message.text = "فروش ماشین"
    result = await vehicle.vehicle_init_message_handler(mock_update, mock_context)
    assert result == 2  # NEXT_STATE_RETURN_VALUE
    assert mock_context.user_data["advertisement_type"] == "sale"

def test_cleaning_user_data_cache(vehicle, mock_update, mock_context):
    mock_context.user_data["test"] = True
    vehicle.cleaning_user_data_cache(mock_update, mock_context)
    assert not mock_context.user_data

def test_generate_descript_fildes(vehicle, mock_update, mock_context):
    mock_context.user_data.update({
        "brand": "Test",
        "model": "2020",
        "advertisement_type": "sale"
    })
    result = vehicle.generate_descript_fildes(mock_update, mock_context)
    assert result == {
        "brand": "Test",
        "model": "2020",
        "advertisement_type": "sale",
        "vehicle_type": "ConcreteVehicle"
    }

@pytest.mark.asyncio
async def test_cancel_command_handler(vehicle, mock_update, mock_context):
    result = await vehicle.cancel_command_handler(mock_update, mock_context)
    assert result == ConversationHandler.END
