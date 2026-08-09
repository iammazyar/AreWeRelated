from insightface.app import FaceAnalysis

class FaceDetector:
    def __init__(self, det_size=(640, 640)):
        self.model = FaceAnalysis(name="buffalo_l")
        self.model.prepare(ctx_id=-1, det_size=det_size)

    def detect_face(self, img):
        faces = self.model.get(img)
        if not faces:
            return None
        face = faces[0]
        return face
