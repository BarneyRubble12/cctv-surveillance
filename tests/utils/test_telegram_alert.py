import unittest
from unittest.mock import AsyncMock, patch
from src.utils.telegram_alert import TelegramAlert


class TestTelegramAlert(unittest.IsolatedAsyncioTestCase):

    async def test_send_alert(self):
        # Replace 'your_bot_token' and 'your_chat_id' with actual values
        bot_token = 'your_bot_token'
        chat_id = 'your_chat_id'
        alert_message = 'Test alert message'

        with patch('telegram_alert.Bot') as mock_bot:
            telegram_alert = TelegramAlert(bot_token=bot_token, chat_id=chat_id)

            # Mock the send_message method
            mock_send_message = AsyncMock()
            mock_bot.return_value.send_message = mock_send_message

            # Call the send_alert method
            await telegram_alert.send_alert(alert_message)

            # Assert that send_message was called with the expected arguments
            mock_send_message.assert_called_once_with(chat_id=chat_id, text=alert_message)


if __name__ == '__main__':
    unittest.main()
