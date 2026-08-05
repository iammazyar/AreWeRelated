import numpy as np

from .face_detector import FaceDetector


class Analyser:

    def __init__(self, detector: FaceDetector):
        self.detector = detector
        self.face1 = None
        self.face2 = None

    #######################################################
    # Helpers
    #######################################################

    def normalize_landmarks(self, kps):
        """Translate to centroid and scale to unit norm."""
        center = np.mean(kps, axis=0)
        kps = kps - center
        scale = np.linalg.norm(kps)
        return kps / scale

    def region_similarity(self, lm1, lm2):
        """
        Cosine similarity between two normalized landmark regions.
        Flatten to 1-D vectors so we compare the overall shape, not
        point-by-point positions.
        """
        v1 = self.normalize_landmarks(lm1).flatten()
        v2 = self.normalize_landmarks(lm2).flatten()
        return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))

    def _lm68(self, face):
        """Return the 68 3-D landmarks (from 1k3d68.onnx) as a float array, or None."""
        lm = getattr(face, "landmark_3d_68", None)
        return lm.astype(float) if lm is not None else None

    #######################################################
    # Similarity Metrics
    #######################################################

    def embedding_similarity(self):
        e1 = self.face1.embedding
        e2 = self.face2.embedding
        cosine = np.dot(e1, e2) / (np.linalg.norm(e1) * np.linalg.norm(e2))
        # map [-1, 1] -> [0, 1]
        return float((cosine + 1) / 2)

    # --- 68-point region similarities (1k3d68.onnx / iBUG 300-W layout) ---
    #   Jawline        0  - 16
    #   Right eyebrow 17  - 21
    #   Left eyebrow  22  - 26
    #   Nose bridge   27  - 30
    #   Nose base     31  - 35
    #   Right eye     36  - 41
    #   Left eye      42  - 47
    #   Outer lips    48  - 59
    #   Inner lips    60  - 67

    def jawline_similarity(self):
        lm1, lm2 = self._lm68(self.face1), self._lm68(self.face2)
        if lm1 is None or lm2 is None:
            return 1.0
        return self.region_similarity(lm1[0:17], lm2[0:17])

    def eyebrow_similarity(self):
        lm1, lm2 = self._lm68(self.face1), self._lm68(self.face2)
        if lm1 is None or lm2 is None:
            return 1.0
        brow1 = np.vstack([lm1[17:22], lm1[22:27]])
        brow2 = np.vstack([lm2[17:22], lm2[22:27]])
        return self.region_similarity(brow1, brow2)

    def nose_similarity(self):
        lm1, lm2 = self._lm68(self.face1), self._lm68(self.face2)
        if lm1 is None or lm2 is None:
            kps1 = self.normalize_landmarks(self.face1.kps)
            kps2 = self.normalize_landmarks(self.face2.kps)
            return float(np.exp(-np.linalg.norm(kps1[2] - kps2[2])))
        nose1 = lm1[27:36]  # bridge + base (9 points)
        nose2 = lm2[27:36]
        return self.region_similarity(nose1, nose2)

    def eye_similarity(self):
        lm1, lm2 = self._lm68(self.face1), self._lm68(self.face2)
        if lm1 is None or lm2 is None:
            kps1 = self.normalize_landmarks(self.face1.kps)
            kps2 = self.normalize_landmarks(self.face2.kps)
            eye1 = np.linalg.norm(kps1[0] - kps1[1])
            eye2 = np.linalg.norm(kps2[0] - kps2[1])
            return float(np.exp(-abs(eye1 - eye2)))
        eyes1 = np.vstack([lm1[36:42], lm1[42:48]])
        eyes2 = np.vstack([lm2[36:42], lm2[42:48]])
        return self.region_similarity(eyes1, eyes2)

    def mouth_similarity(self):
        lm1, lm2 = self._lm68(self.face1), self._lm68(self.face2)
        if lm1 is None or lm2 is None:
            kps1 = self.normalize_landmarks(self.face1.kps)
            kps2 = self.normalize_landmarks(self.face2.kps)
            mouth1 = (kps1[3] + kps1[4]) / 2
            mouth2 = (kps2[3] + kps2[4]) / 2
            return float(np.exp(-np.linalg.norm(mouth1 - mouth2)))
        lips1 = np.vstack([lm1[48:60], lm1[60:68]])  # outer + inner lips
        lips2 = np.vstack([lm2[48:60], lm2[60:68]])
        return self.region_similarity(lips1, lips2)

    def age_similarity(self):
        age1 = self.face1.age
        age2 = self.face2.age
        return float(np.exp(-abs(age1 - age2) / 20))

    def gender_similarity(self):
        return float(self.face1.gender == self.face2.gender)

    def pose_similarity(self):
        if not hasattr(self.face1, "pose"):
            return 1.0
        pose1 = np.array(self.face1.pose)
        pose2 = np.array(self.face2.pose)
        diff = np.linalg.norm(pose1 - pose2)
        return float(np.exp(-diff / 30))

    #######################################################
    # Final compare
    #######################################################

    def compare(self, img1, img2):

        self.face1 = self.detector.detect_face(img1)
        self.face2 = self.detector.detect_face(img2)

        if self.face1 is None or self.face2 is None:
            return {"error": "Face not detected"}

        emb    = self.embedding_similarity()
        jaw    = self.jawline_similarity()
        brow   = self.eyebrow_similarity()
        eye    = self.eye_similarity()
        nose   = self.nose_similarity()
        mouth  = self.mouth_similarity()

        final_score = (
            0.50 * emb +
            0.1 * jaw +
            0.1 * brow +
            0.1 * eye +
            0.1 * nose +
            0.1 * mouth
        )

        return {

            "similarity": round(final_score, 2),

            "scores": {
                "embedding": round(emb, 2),
                "jawline": round(jaw, 2),
                "eyebrows": round(brow, 2),
                "eyes": round(eye, 2),
                "nose": round(nose, 2),
                "mouth": round(mouth, 2),
            },

            "face1": {
                "bbox": self.face1.bbox.tolist(),
                "age": int(self.face1.age),
                "gender": int(self.face1.gender),
                "pose": self.face1.pose.tolist() if hasattr(self.face1, "pose") and self.face1.pose is not None else None,
            },

            "face2": {
                "bbox": self.face2.bbox.tolist(),
                "age": int(self.face2.age),
                "gender": int(self.face2.gender),
                "pose": self.face2.pose.tolist() if hasattr(self.face2, "pose") and self.face2.pose is not None else None,
            }
        }
