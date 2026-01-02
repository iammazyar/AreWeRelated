import math

from face_detector import FaceDetector
import numpy as np
from utils import to_base64


class Analyser:

    def __init__(self, detector: FaceDetector):

        self.detector = detector
        self.face1 = None
        self.face2 = None

    def compare(self, img1, img2):
        self.face1 = self.detector.detect_face(img1)
        self.face2 = self.detector.detect_face(img2)
        if self.face1 is None or self.face2 is None:
            return {"error": "Face not detected in one or both images"}
        e1, e2 = self.face1.embedding, self.face2.embedding
        similarity = float(np.dot(e1, e2) / (np.linalg.norm(e1) * np.linalg.norm(e2)))

        # x11, y11, x12, y12 = self.face1.bbox.astype(int)
        # x21, y21, x22, y22 = self.face2.bbox.astype(int)
        # crop1 = img1[y11:y12, x11:x12]
        # crop2 = img2[y21:y22, x21:x22]

        return {
            "similarity": math.floor(similarity*100)/100,
            "face1": {
                "bbox": self.face1.bbox.tolist(),
                # "crop": to_base64(crop1)
            },
            "face2": {
                "bbox": self.face2.bbox.tolist(),
                # "crop": to_base64(crop2)
            }
        }



