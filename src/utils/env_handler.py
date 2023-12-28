
from dotenv import load_dotenv
import os

class EnvHandler:

    def __init__(self):
        load_dotenv()

        self.camera_ip = os.getenv('CAMERA_IP')
        self.camera_id = os.getenv('CAMERA_ID')
        self.camera_password = os.getenv('CAMERA_PASSWORD')
        self.camera_port = os.getenv('CAMERA_PORT')
        self.camera_channel = os.getenv('CAMERA_CHANNEL')

        self.telegram_bot_channel_id = os.getenv('TELEGRAM_BOT_CHANNEL_ID')
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_message_photo_path = os.getenv("TELEGRAM_MESSAGE_PHOTO_PATH")
