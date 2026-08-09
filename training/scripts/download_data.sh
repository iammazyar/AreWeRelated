#!/usr/bin/env bash
# Downloads the "Recognizing Faces in the Wild" (RFIW/FIW) kinship dataset from Kaggle.
# Requires a Kaggle API token at ~/.kaggle/kaggle.json (see README.md).
set -euo pipefail

cd "$(dirname "$0")/.."   # training/

DEST=data
mkdir -p "$DEST"

.venv/bin/kaggle competitions download -c recognizing-faces-in-the-wild -p "$DEST"
unzip -q -o "$DEST/recognizing-faces-in-the-wild.zip" -d "$DEST"

echo "Downloaded and extracted to $DEST/"
ls "$DEST"
