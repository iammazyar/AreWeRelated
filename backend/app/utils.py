import cv2
import base64
import numpy as np

def image_from_upload(upload):
    data = np.frombuffer(upload.file.read(), np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_COLOR)

def to_base64(img):
    _, buf = cv2.imencode(".jpg", img)
    return base64.b64encode(buf).decode()
    
