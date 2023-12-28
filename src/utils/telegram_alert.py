# telegram_alert.py

from telegram import Bot

class TelegramAlert:

    def __init__(self, bot_token, chat_id):
        self.telegram_bot = Bot(token=bot_token)
        self.chat_id = chat_id

    async def send_alert(self, message):
        try:
            await self.telegram_bot.send_message(chat_id=self.chat_id, text=message)
        except Exception as e:
            print(f"Error sending Telegram alert: {e}")
