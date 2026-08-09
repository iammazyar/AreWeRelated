"""
Trains a logistic regression on the 6 similarity-score features extracted by
extract_features.py, evaluates it with family-grouped cross-validation, and
saves the final model for the backend to load.

Family-grouped, not row-grouped: a plain row-level train/test split would let
the same person (or even the same photo) appear in both train and test, since
each relationship contributes multiple image pairs. That leaks identity and
inflates test metrics. Instead we split whole families across folds, so every
image of every person in a family lands entirely on one side.
"""
import os

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import ConfusionMatrixDisplay, RocCurveDisplay, accuracy_score, roc_auc_score
from sklearn.model_selection import KFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

HERE = os.path.dirname(__file__)
DATA_DIR = os.path.join(HERE, "..", "data")
MODELS_DIR = os.path.join(HERE, "..", "models")
RESULTS_DIR = os.path.join(HERE, "..", "results")

# FEATURES = ["embedding", "jawline", "eyebrows", "eyes", "nose", "mouth"]
FEATURES = ["embedding"]
RANDOM_SEED = 42
N_FOLDS = 5

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)


def family_of(path):
    return path.split("/")[0]


def make_model():
    # StandardScaler matters here specifically because LogisticRegression's
    # default L2 penalty punishes coefficient magnitude uniformly — on
    # unstandardized features that unfairly favors low-variance features,
    # which would undermine using the coefficients to judge which regions
    # actually carry signal.
    return Pipeline([
        ("scaler", StandardScaler()),
        ("logreg", LogisticRegression(max_iter=1000)),
    ])


def main():
    df = pd.read_csv(os.path.join(DATA_DIR, "features.csv"))
    df["family1"] = df["p1"].apply(family_of)
    df["family2"] = df["p2"].apply(family_of)
    print(f"{len(df)} rows, {df['label'].mean():.1%} positive")

    families = np.array(sorted(set(df["family1"]) | set(df["family2"])))
    print(f"{len(families)} unique families")

    kfold = KFold(n_splits=N_FOLDS, shuffle=True, random_state=RANDOM_SEED)

    fold_metrics = []
    oof_true, oof_proba, oof_baseline = [], [], []

    for fold_i, (train_fam_idx, test_fam_idx) in enumerate(kfold.split(families)):
        test_families = set(families[test_fam_idx])
        train_families = set(families[train_fam_idx])

        is_train_row = df["family1"].isin(train_families) & df["family2"].isin(train_families)
        is_test_row = df["family1"].isin(test_families) & df["family2"].isin(test_families)
        # Rows straddling the boundary (only possible for cross-family negative
        # pairs) are dropped for this fold — they can't be assigned to either
        # side without leaking a family into the other.

        train_df, test_df = df[is_train_row], df[is_test_row]

        model = make_model()
        model.fit(train_df[FEATURES], train_df["label"])
        proba = model.predict_proba(test_df[FEATURES])[:, 1]
        pred = (proba >= 0.5).astype(int)

        acc = accuracy_score(test_df["label"], pred)
        auc = roc_auc_score(test_df["label"], proba)
        fold_metrics.append((acc, auc))
        print(f"  fold {fold_i}: {len(train_df)} train / {len(test_df)} test rows, "
              f"accuracy={acc:.3f}, AUC={auc:.3f}")

        oof_true.append(test_df["label"].values)
        oof_proba.append(proba)
        oof_baseline.append(test_df["embedding"].values)

    accs, aucs = zip(*fold_metrics)
    print(f"\n{N_FOLDS}-fold family-grouped CV:")
    print(f"  accuracy: {np.mean(accs):.3f} +/- {np.std(accs):.3f}")
    print(f"  ROC-AUC:  {np.mean(aucs):.3f} +/- {np.std(aucs):.3f}")

    y_true = np.concatenate(oof_true)
    y_proba = np.concatenate(oof_proba)
    baseline_proba = np.concatenate(oof_baseline)
    baseline_acc = accuracy_score(y_true, (baseline_proba >= 0.5).astype(int))
    baseline_auc = roc_auc_score(y_true, baseline_proba)
    print(f"\nBaseline (embedding only), same folds:")
    print(f"  accuracy: {baseline_acc:.3f}")
    print(f"  ROC-AUC:  {baseline_auc:.3f}")

    # --- final model for deployment: refit on all data ---
    final_model = make_model()
    final_model.fit(df[FEATURES], df["label"])
    coefs = final_model.named_steps["logreg"].coef_[0]
    print("\nLearned coefficients on standardized features (higher |coef| = more influence):")
    for name, coef in sorted(zip(FEATURES, coefs), key=lambda t: -abs(t[1])):
        print(f"  {name:10s} {coef:+.3f}")
    print(f"  {'intercept':10s} {final_model.named_steps['logreg'].intercept_[0]:+.3f}")

    # --- plots from the out-of-fold predictions (every row scored exactly once) ---
    fig, ax = plt.subplots(figsize=(6, 6))
    RocCurveDisplay.from_predictions(y_true, y_proba, ax=ax, name="logistic regression (6 features, CV)")
    RocCurveDisplay.from_predictions(y_true, baseline_proba, ax=ax, name="baseline (embedding only)")
    ax.plot([0, 1], [0, 1], linestyle="--", color="gray")
    ax.set_title(f"ROC — {N_FOLDS}-fold family-grouped CV (out-of-fold predictions)")
    fig.savefig(os.path.join(RESULTS_DIR, "roc_curve.png"), dpi=150, bbox_inches="tight")

    fig, ax = plt.subplots(figsize=(5, 5))
    ConfusionMatrixDisplay.from_predictions(
        y_true, (y_proba >= 0.5).astype(int), ax=ax, display_labels=["unrelated", "related"]
    )
    ax.set_title("Confusion matrix (out-of-fold, all folds combined)")
    fig.savefig(os.path.join(RESULTS_DIR, "confusion_matrix.png"), dpi=150, bbox_inches="tight")

    model_path = os.path.join(MODELS_DIR, "logreg.joblib")
    joblib.dump({"model": final_model, "features": FEATURES}, model_path)
    print(f"\nSaved final model (refit on all data) to {model_path}")
    print(f"Saved plots to {RESULTS_DIR}/")


if __name__ == "__main__":
    main()
