# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AreWeLookalike is a facial similarity comparison application that uses InsightFace for face detection and recognition. The project consists of:
- **Backend**: FastAPI server with InsightFace face analysis (Python)
- **Frontend**: React + Vite application with Tailwind CSS (JavaScript/JSX)

## Architecture

### Backend (Python/FastAPI)
- **Framework**: FastAPI with Uvicorn server
- **Face Recognition**: InsightFace `buffalo_l` model for face analysis
- **Model**: Loads on startup with CPU execution (`ctx_id=-1`)
- **Key Library**: `insightface.app.FaceAnalysis` for face detection and embedding extraction
- **Face Comparison**: Uses cosine similarity between face embeddings (default threshold: 0.65)
- **Location**: `backend/app/main.py`

### Frontend (React/Vite)
- **Framework**: React 19 with Vite build tool
- **Styling**: Tailwind CSS v4
- **API Communication**: Axios instance configured with base URL `http://localhost:3000` (see `frontend/src/api.js`)
- **Key Components**:
  - `Body.jsx`: Main component managing state for two image uploads, comparison results, and loading states
  - `imageUploader.jsx`: Reusable component for file upload with preview
  - Multi-step interface (`currentStep` state) for upload and results

### Face Analysis Algorithm (from Jupyter notebook)
The core facial comparison logic:
1. Load InsightFace `buffalo_l` model
2. Detect faces in uploaded images using `app.get(image)`
3. Extract 512-dimensional face embeddings
4. Calculate cosine similarity between embeddings
5. Compare against threshold (typically 0.65) to determine if same person

## Development Commands

### Frontend
```bash
cd frontend
npm install              # Install dependencies
npm run dev              # Start development server (Vite)
npm run build            # Build for production
npm run preview          # Preview production build
npm run lint             # Run ESLint
```

### Backend
```bash
cd backend
pip install -r requirements.txt    # Install dependencies
uvicorn app.main:app --reload      # Run FastAPI server with hot reload
```

Note: Backend expects the InsightFace model to be downloaded. First run will download the `buffalo_l` model to `~/.insightface/models/`.

## Important Notes

### API Configuration
- Frontend is configured to connect to `http://localhost:3000` but backend typically runs on `http://localhost:8000` (FastAPI default)
- **Check and update `frontend/src/api.js` baseURL** if backend port differs

### Face Analysis Behavior
- If no faces detected: raises "No faces detected" error
- If multiple faces detected: uses first detected face with warning
- Face embeddings are 512-dimensional vectors from the recognition model
- Similarity threshold of 0.65 is standard but can be adjusted based on use case

### Current Development Status
- Backend has InsightFace model initialization but no endpoints are visible in main.py (incomplete)
- Frontend has image upload UI but comparison logic is commented out in Body.jsx
- The Jupyter notebook `Untitled.ipynb` contains the working face comparison prototype
