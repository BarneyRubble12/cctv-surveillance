from transformers import DetrImageProcessor, DetrForObjectDetection
import torch
from PIL import Image
import cv2
from utils.env_handler import EnvHandler
import requests

#Load environment configs
config = EnvHandler()

# Load the pre-trained processor and model
processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50", revision="no_timm")
model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50", revision="no_timm")

# Replace 'your_camera_rtsp_url' with the actual RTSP URL of your camera
camera_url = f'rtsp://{config.camera_id}:{config.camera_password}@{config.camera_ip}:{config.camera_port}/cam/realmonitor?channel=3&subtype=1'
cap = cv2.VideoCapture(camera_url)

while cap.isOpened():
    ret, frame = cap.read()

    if not ret:
        break

    # Convert the frame to PIL Image
    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    # Process the image with the DETR model
    inputs = processor(images=image, return_tensors="pt")
    outputs = model(**inputs)

    # Convert outputs to COCO API format
    target_sizes = torch.tensor([image.size[::-1]])
    results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.9)[0]

    # Draw bounding boxes on the frame
    for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
        box = [round(i, 2) for i in box.tolist()]
        label_str = model.config.id2label[label.item()]
        confidence_str = round(score.item(), 3)

        cv2.rectangle(frame, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 255, 0), 2)
        cv2.putText(frame, f"{label_str} {confidence_str}", (int(box[0]), int(box[1]) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Display the resulting frame
    cv2.imshow('Object Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close the window
cap.release()
cv2.destroyAllWindows()
