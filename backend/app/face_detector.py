from insightface.app import FaceAnalysis

class FaceDetector:
    def __init__(self):
        self.model = FaceAnalysis(name="buffalo_l")
        self.model.prepare(ctx_id=-1)

    def detect_face(self, img):
        faces = self.model.get(img)
        if not faces:
            return None
        face = faces[0]
        return face
