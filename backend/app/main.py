from fastapi import FastAPI, UploadFile, File
import cv2
import numpy as np
import base64
from insightface.app import FaceAnalysis
from typing import List


app = FastAPI()
model = FaceAnalysis(name="buffalo_l")
model.prepare(ctx_id=-1)

