
from dotenv import load_dotenv
import os

class EnvHandler:

    def __init__(self):
        load_dotenv()
        self.camera_ip = os.getenv('CAMERA_IP')
        self.camera_id = os.getenv('CAMERA_ID')
        self.camera_password = os.getenv('CAMERA_PASSWORD')
        self.camera_port = os.getenv('CAMERA_PORT')
