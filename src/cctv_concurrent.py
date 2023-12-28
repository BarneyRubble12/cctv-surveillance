# main_script.py

from transformers import DetrImageProcessor, DetrForObjectDetection
import torch
from PIL import Image
import cv2
from utils.env_handler import EnvHandler
import time
import imutils
from utils.telegram_alert import TelegramAlert
import asyncio
import os


class PersonDetectionAlert:

    def __init__(self):
        # Load environment configs
        self.config = EnvHandler()

        # Load the pre-trained processor and model
        self.processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50", revision="no_timm")
        self.model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50", revision="no_timm")

        # self.camera_url = f'rtsp://{self.config.camera_id}:{self.config.camera_password}@{self.config.camera_ip}:{self.config.camera_port}/cam/realmonitor?channel={self.config.camera_channel}&subtype=1'
        self.camera_url = f'rtsp://{self.config.camera_id}:{self.config.camera_password}@{self.config.camera_ip}:{self.config.camera_port}/cam/realmonitor?channel={self.config.camera_channel}&subtype=0&unicast=true&proto=Onvif'

        # Initialize Telegram alert system
        self.telegram_alert = TelegramAlert(
            bot_token=self.config.telegram_bot_token,
            chat_id=self.config.telegram_bot_channel_id)

    async def send_telegram_alert(self, message, frame):
        image_path = f'{self.config.telegram_message_photo_path}/detected_person.jpg'
        try:
            self.ensure_directory_exists(self.config.telegram_message_photo_path)
            cv2.imwrite(image_path, frame)
            await self.telegram_alert.send_alert(message, image_path)
        except Exception as e:
            print(f'Error sending Telegram alert: {e}')
        finally:
            # Clean up: Remove the saved image
            if os.path.exists(image_path):
                os.remove(image_path)

    async def process_frame(self, frame):
        # Resize the frame for better performance
        frame = imutils.resize(frame, width=800)

        # Convert the frame to PIL Image
        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # Process the image with the DETR model
        inputs = self.processor(images=image, return_tensors="pt")
        outputs = self.model(**inputs)

        # Convert outputs to COCO API format
        target_sizes = torch.tensor([image.size[::-1]])
        results = self.processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.9)[0]

        # Draw bounding boxes on the frame for detected persons
        for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
            box = [round(i, 2) for i in box.tolist()]

            # Check if the detected object is a person (label ID 1)
            if label.item() == 1:
                label_str = self.model.config.id2label[label.item()]
                confidence_str = round(score.item(), 3)

                # Get the current system time
                current_time = time.strftime("%Y-%m-%d %H:%M:%S")

                alert_message = f"¡¡¡Auauuuuuuuu!!! Intruso detectado a las {current_time}\nConfidence: {confidence_str}"

                # Print the system time when a person is detected
                print(alert_message)

                # Send a Telegram alert
                await self.send_telegram_alert(alert_message, frame)

                # Draw bounding box and label on the frame
                cv2.rectangle(frame, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 255, 0), 2)
                cv2.putText(frame, f"{label_str} {confidence_str}", (int(box[0]), int(box[1]) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Display the resulting frame
        cv2.imshow('Object Detection', frame)

    async def run_detection(self):
        cap = cv2.VideoCapture(self.camera_url)

        while True:
            ret, frame = cap.read()

            if not ret:
                print("Video stream ended.")
                break

            # Submit the frame processing task to the executor
            await self.process_frame(frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release the video capture object and close the window
        cap.release()
        cv2.destroyAllWindows()

    def ensure_directory_exists(self, directory_path):
        # Check if the directory exists
        if not os.path.exists(directory_path):
            # Create the directory if it doesn't exist
            os.makedirs(directory_path)


if __name__ == "__main__":
    alert_system = PersonDetectionAlert()

    # Ensure the event loop is created (if not using an existing one)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(alert_system.run_detection())
