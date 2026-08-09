import numpy as np

from face_detector import FaceDetector


class Analyser:

    def __init__(self, detector: FaceDetector, model=None):
        self.detector = detector
        self.model = model
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

    def region_similarity_euclidean(self, lm1, lm2, scale=3.0):
        """
        Mean per-point Euclidean distance after centering + unit-norm
        scaling (no rotation alignment, unlike Procrustes) — a plain
        geometric-distance baseline.
        """
        lm1 = lm1.copy()
        lm2 = lm2.copy()
        lm1[:, 2] *= 3.0
        lm2[:, 2] *= 3.0
        v1 = self.normalize_landmarks(lm1)
        v2 = self.normalize_landmarks(lm2)
        mean_dist = float(np.median(np.linalg.norm(v1 - v2, axis=1)))
        return float(np.exp(-mean_dist * scale))

    def _lm68(self, face):
        """Return the 68 3-D landmarks (from 1k3d68.onnx) as a float array, or None."""
        lm = getattr(face, "landmark_3d_68", None)
        return lm.astype(float) if lm is not None else None

    def region_points(self, face):
        """
        (x, y) pixel points per facial region, for drawing region outlines
        on the frontend. Same index ranges used by the *_similarity methods.
        """
        lm = self._lm68(face)
        if lm is None:
            return None
        pts = lm[:, :2]
        return {
            "jawline": pts[0:17].tolist(),
            "eyebrows": [pts[17:22].tolist(), pts[22:27].tolist()],
            "nose": pts[27:36].tolist(),
            "eyes": [pts[36:42].tolist(), pts[42:48].tolist()],
            "mouth": [pts[48:60].tolist(), pts[60:68].tolist()],
        }

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
        return self.region_similarity_euclidean(lm1[0:17], lm2[0:17])

    def eyebrow_similarity(self):
        lm1, lm2 = self._lm68(self.face1), self._lm68(self.face2)
        if lm1 is None or lm2 is None:
            return 1.0
        brow1 = np.vstack([lm1[17:22], lm1[22:27]])
        brow2 = np.vstack([lm2[17:22], lm2[22:27]])
        return self.region_similarity_euclidean(brow1, brow2)

    def nose_similarity(self):
        lm1, lm2 = self._lm68(self.face1), self._lm68(self.face2)
        if lm1 is None or lm2 is None:
            kps1 = self.normalize_landmarks(self.face1.kps)
            kps2 = self.normalize_landmarks(self.face2.kps)
            return float(np.exp(-np.linalg.norm(kps1[2] - kps2[2])))
        nose1 = lm1[27:36]  # bridge + base (9 points)
        nose2 = lm2[27:36]
        return self.region_similarity_euclidean(nose1, nose2)

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
        return self.region_similarity_euclidean(eyes1, eyes2)

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
        return self.region_similarity_euclidean(lips1, lips2)

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

        emb = self.embedding_similarity()

        if self.model is not None:
            # Trained on FIW kinship pairs (see training/README.md): a
            # calibrated logistic regression over the embedding similarity.
            # The 5 landmark region-similarity scores were also evaluated as
            # features there and dropped — 5-fold family-grouped CV showed
            # they added no measurable improvement over embedding alone
            # (AUC 0.799 vs 0.800), so the live endpoint no longer computes
            # them for the score (still used below for the drawn outlines).
            final_score = float(self.model["model"].predict_proba([[emb]])[0][1])
        else:
            final_score = emb

        return {

            "similarity": round(final_score, 2),

            "face1": {
                "bbox": self.face1.bbox.tolist(),
                "age": int(self.face1.age),
                "gender": int(self.face1.gender),
                "pose": self.face1.pose.tolist() if hasattr(self.face1, "pose") and self.face1.pose is not None else None,
                "landmarks": self.region_points(self.face1),
            },

            "face2": {
                "bbox": self.face2.bbox.tolist(),
                "age": int(self.face2.age),
                "gender": int(self.face2.gender),
                "pose": self.face2.pose.tolist() if hasattr(self.face2, "pose") and self.face2.pose is not None else None,
                "landmarks": self.region_points(self.face2),
            }
        }
