from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import Dict
from face_detector import FaceDetector
from analyser import Analyser
from utils import image_from_upload


app = FastAPI(title="AreWeLookalike API")

origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/compare", response_model=Dict)
async def compare_faces(img1: UploadFile = File(...), img2: UploadFile = File(...)):
    image1 = image_from_upload(img1)
    image2 = image_from_upload(img2)

    analyser = Analyser(FaceDetector())
    result = analyser.compare(image1, image2)
    print(result)

    if "error" in result:
        raise HTTPException(status_code=422, detail=result["error"])

    return result


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
