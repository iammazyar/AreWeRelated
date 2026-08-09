"""
Builds a labeled feature table for kinship classification.

For every pair of face images (positive = related per train_relationships.csv,
negative = sampled from two different families), runs the *exact* backend
Analyser methods (imported directly, not reimplemented) to get the 6
similarity scores, and writes them + the label to data/features.csv.
"""
import csv
import os
import pickle
import random
import sys
import time

import cv2

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend", "app"))
from face_detector import FaceDetector
from analyser import Analyser

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
FACES_DIR = os.path.join(DATA_DIR, "train-faces")
RELATIONSHIPS_CSV = os.path.join(DATA_DIR, "train_relationships.csv")
CACHE_PATH = os.path.join(DATA_DIR, "face_cache.pkl")
OUTPUT_CSV = os.path.join(DATA_DIR, "features.csv")

# These 224x224 FIW crops fill nearly the whole frame, which the production
# det_size=640 fails to detect at all (0/15 in a spot check). 224 matches the
# actual crop size and detects reliably — see training/README.md.
DET_SIZE = (224, 224)

PAIRS_PER_RELATIONSHIP = 3
RANDOM_SEED = 42
CHECKPOINT_EVERY = 300


def list_person_images(person_dir):
    full = os.path.join(FACES_DIR, person_dir)
    if not os.path.isdir(full):
        return []
    return [os.path.join(person_dir, f) for f in os.listdir(full) if f.lower().endswith(".jpg")]


def load_relationships():
    rows = []
    with open(RELATIONSHIPS_CSV) as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append((row["p1"], row["p2"]))
    return rows


def build_pairs(relationships, families):
    rng = random.Random(RANDOM_SEED)
    pairs = []  # (img_a, img_b, label)

    for p1, p2 in relationships:
        imgs1, imgs2 = list_person_images(p1), list_person_images(p2)
        if not imgs1 or not imgs2:
            continue
        combos = [(a, b) for a in imgs1 for b in imgs2]
        rng.shuffle(combos)
        for a, b in combos[:PAIRS_PER_RELATIONSHIP]:
            pairs.append((a, b, 1))

    n_positive = len(pairs)
    attempts = 0
    while len(pairs) < 2 * n_positive and attempts < 20 * n_positive:
        attempts += 1
        fam_a, fam_b = rng.sample(families, 2)
        mids_a = [d for d in os.listdir(os.path.join(FACES_DIR, fam_a)) if d.startswith("MID")]
        mids_b = [d for d in os.listdir(os.path.join(FACES_DIR, fam_b)) if d.startswith("MID")]
        if not mids_a or not mids_b:
            continue
        imgs_a = list_person_images(os.path.join(fam_a, rng.choice(mids_a)))
        imgs_b = list_person_images(os.path.join(fam_b, rng.choice(mids_b)))
        if not imgs_a or not imgs_b:
            continue
        pairs.append((rng.choice(imgs_a), rng.choice(imgs_b), 0))

    rng.shuffle(pairs)
    return pairs


def load_cache():
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "rb") as f:
            return pickle.load(f)
    return {}


def save_cache(cache):
    tmp = CACHE_PATH + ".tmp"
    with open(tmp, "wb") as f:
        pickle.dump(cache, f)
    os.replace(tmp, CACHE_PATH)


def main():
    print("Loading relationships...")
    relationships = load_relationships()
    families = sorted(os.listdir(FACES_DIR))
    print(f"{len(relationships)} labeled relationships, {len(families)} families")

    pairs = build_pairs(relationships, families)
    n_pos = sum(1 for *_, y in pairs if y == 1)
    n_neg = len(pairs) - n_pos
    print(f"Built {len(pairs)} pairs ({n_pos} positive, {n_neg} negative)")

    unique_images = sorted({img for a, b, _ in pairs for img in (a, b)})
    print(f"{len(unique_images)} unique images to process")

    cache = load_cache()
    print(f"{len(cache)} images already cached from a previous run")

    print("Loading InsightFace model (det_size=224x224 for these tight crops)...")
    detector = FaceDetector(det_size=DET_SIZE)

    todo = [p for p in unique_images if p not in cache]
    t0 = time.time()
    for i, rel_path in enumerate(todo):
        full_path = os.path.join(FACES_DIR, rel_path)
        img = cv2.imread(full_path)
        face = detector.detect_face(img) if img is not None else None
        cache[rel_path] = face

        if (i + 1) % CHECKPOINT_EVERY == 0:
            save_cache(cache)
            elapsed = time.time() - t0
            rate = (i + 1) / elapsed
            remaining = (len(todo) - i - 1) / rate if rate > 0 else float("inf")
            print(f"  {i + 1}/{len(todo)} detected "
                  f"({rate:.2f} img/s, ~{remaining / 60:.1f} min left)")

    save_cache(cache)
    n_failed = sum(1 for f in cache.values() if f is None)
    print(f"Detection done. {n_failed}/{len(cache)} images had no detected face.")

    print("Computing similarity features for each pair...")
    analyser = Analyser(detector)
    rows = []
    for a, b, label in pairs:
        face_a, face_b = cache.get(a), cache.get(b)
        if face_a is None or face_b is None:
            continue
        analyser.face1, analyser.face2 = face_a, face_b
        rows.append({
            "p1": a,
            "p2": b,
            "embedding": analyser.embedding_similarity(),
            "jawline": analyser.jawline_similarity(),
            "eyebrows": analyser.eyebrow_similarity(),
            "eyes": analyser.eye_similarity(),
            "nose": analyser.nose_similarity(),
            "mouth": analyser.mouth_similarity(),
            "label": label,
        })

    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} feature rows to {OUTPUT_CSV} "
          f"(dropped {len(pairs) - len(rows)} pairs with a failed detection)")


if __name__ == "__main__":
    main()
