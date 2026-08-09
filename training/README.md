# Training

Trains a logistic regression that predicts whether two people are related,
using the same 6 similarity scores the backend already computes (embedding +
jawline/eyebrows/eyes/nose/mouth region similarity) as input features. This
replaces the hand-picked weighted-sum formula in `backend/app/analyser.py`
with weights learned from labeled data.

Dataset: [Recognizing Faces in the Wild](https://www.kaggle.com/competitions/recognizing-faces-in-the-wild)
(RFIW/FIW) on Kaggle — labeled kinship pairs (parent-child, siblings, etc.)
from real families.

## Setup

```bash
cd training
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## 1. Kaggle API token

1. Sign in at [kaggle.com](https://kaggle.com), go to Settings → API → "Generate New Token".
   This gives you a token string to copy (current Kaggle CLI versions use this instead
   of the older `kaggle.json` file).
2. Save it to `~/.kaggle/access_token` (never commit this file or paste the token anywhere):
   ```bash
   mkdir -p ~/.kaggle && chmod 700 ~/.kaggle
   echo -n "<paste your token here>" > ~/.kaggle/access_token
   chmod 600 ~/.kaggle/access_token
   ```
   (Alternative: `export KAGGLE_API_TOKEN=<token>` in your shell instead of a file.)
3. You also need to accept the competition rules on the
   [competition page](https://www.kaggle.com/competitions/recognizing-faces-in-the-wild/rules)
   (logged in, click "I Understand and Accept") — Kaggle blocks API downloads otherwise.

## 2. Download the dataset

```bash
scripts/download_data.sh
```

Extracts into `training/data/` (gitignored — not ours to redistribute).

## 3. Extract features

Runs every image through the backend's actual `FaceDetector`/`Analyser` (imported
directly, not reimplemented) to get the 6 similarity scores for each labeled pair,
plus generated negative (unrelated) pairs sampled from different families.

```bash
.venv/bin/python scripts/extract_features.py
```

Writes `data/features.csv`.

## 4. Train + evaluate

```bash
.venv/bin/python scripts/train_model.py
```

Trains a logistic regression on an 80/20 train/test split, prints AUC/accuracy/
coefficients, saves ROC curve + confusion matrix plots to `results/`, and saves
the trained model to `models/logreg.joblib`.

## 5. Use it in the backend

`backend/app/analyser.py` loads `training/models/logreg.joblib` at startup and
uses it in `compare()` in place of the hand-picked weighted sum.
