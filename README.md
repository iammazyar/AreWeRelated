# AreWeRelated

A face similarity application that estimates whether two people are likely to be related based on their facial features.

**Live demo:** [AreWeRelated](https://iammazyar.github.io/AreWeRelated)

## What It Does

Upload two photos, and **AreWeRelated** estimates the likelihood that the two people are related.
The model is trained on the **Recognizing Faces in the Wild (RFIW/FIW)** kinship dataset and uses facial embeddings extracted with **InsightFace**.

---

## How It Works

The application consists of three main steps:

### 1. Dataset

The model was trained using the [Recognizing Faces in the Wild (RFIW/FIW)](https://www.kaggle.com/competitions/recognizing-faces-in-the-wild) dataset.
The dataset contains labeled kinship pairs from hundreds of families, including relationships such as:

* Parent–child
* Siblings

The original dataset provides **related pairs**. To create the negative class, I wrote a script that generates **unrelated pairs by combining images from different families**.
This results in a binary classification problem:

* `1` → Related
* `0` → Unrelated

### 2. Feature Extraction

For each uploaded image, I use a pre-trained **InsightFace** model to extract:

* A **512-dimensional face embedding**
* **68 3D facial landmarks**

The face embedding captures high-level facial characteristics, while the landmarks describe the geometry of different facial regions.

I experimented with six similarity features:

1. Overall face embedding similarity
2. Jawline similarity
3. Eyebrow similarity
4. Eye similarity
5. Nose similarity
6. Mouth similarity

For each pair of images, the similarity between corresponding features is calculated using **cosine similarity**.

### 3. Model & Evaluation

I trained a **Logistic Regression** classifier using these similarity features.
To evaluate the model while preventing identity and family leakage, I used **5-fold family-grouped cross-validation**.
In each split, **all images belonging to a family remain entirely within either the training or validation set**. This prevents the model from seeing the same person's face, or another member of the same family, during training and evaluation.

---

## Feature Experiment

I initially expected the landmark-based facial region features to improve the prediction compared with using the face embedding alone.
However, the experiment showed otherwise:

| Features                            | Mean ROC-AUC |
| ----------------------------------- | -----------: |
| Embedding similarity only           |    **0.800** |
| Embedding + 5 landmark similarities |    **0.799** |

The five landmark-based features provided **no measurable improvement** over embedding similarity alone. The ROC curves were also almost completely overlapping.

![ROC curves](path/to/your/roc-curve-image.png)

### Final Model

Based on this experiment, the deployed model is:
**InsightFace → 512D face embeddings → Cosine Similarity → Logistic Regression**

The landmark-based similarity calculations remain in the codebase. They are still used for **visualizing facial regions on the uploaded images** and remain available for anyone who wants to continue experimenting with them, but they are **not used by the deployed classifier**.

---

## Running Locally

### Backend

```bash
cd backend

python3 -m venv .env
.env/bin/pip install -r requirements.txt

.env/bin/uvicorn app.main:app --reload --port 8000
```

### Frontend

In another terminal:

```bash
cd frontend

npm install
npm run dev
```

The frontend expects the API to be available at:

```text
http://localhost:8000
```

## License

MIT — see [LICENSE](LICENSE).
