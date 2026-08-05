import { useState, useEffect } from "react";
import ImageUploader from "./imageUploader";
import DetectedFace, { POSE_LABEL } from "./Results";
import { compareFaces } from "../api";

const SCORE_LABELS = {
    embedding: "Overall Identity",
    jawline:   "Jawline",
    eyebrows:  "Eyebrows",
    eyes:      "Eyes",
    nose:      "Nose",
    mouth:     "Mouth",
};

function SimilarityMessage({ score }) {
    if (score >= 0.8) return (
        <span className="text-sky-400 text-sm font-medium text-center">
            You look so much alike, I got confused that you might be the same person. Are you really?
        </span>
    );
    if (score >= 0.6) return (
        <span className="text-sky-400 text-sm font-medium text-center">
            You look so much alike that if you're actually two different people, you might have a serious talk with your father oorrrr your mom!!
        </span>
    );
    if (score >= 0.45) return (
        <span className="text-sky-400 text-sm font-medium text-center">
            You have a few similarities, but there's still a decent chance one of your parents was… not exactly a model citizen.
        </span>
    );
    return (
        <span className="text-sky-400 text-sm font-medium text-center">
            You have no similarities at all dudes, congratulations to your parents.
        </span>
    );
}

function ScoreBar({ label, value }) {
    const pct = Math.round(value * 100);
    return (
        <div className="flex items-center gap-x-3">
            <span className="text-gray-400 text-xs w-32 shrink-0">{label}</span>
            <div className="flex-1 bg-gray-700 rounded-full h-2">
                <div
                    className="bg-sky-500 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${pct}%` }}
                />
            </div>
            <span className="text-white text-xs w-8 text-right">{pct}%</span>
        </div>
    );
}

export default function Body() {
    const [img1, setImg1] = useState(null);
    const [img2, setImg2] = useState(null);
    const [preview1, setPreview1] = useState(null);
    const [preview2, setPreview2] = useState(null);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const [currentStep, setCurrentStep] = useState(1);

    useEffect(() => {
        if (!img1) { setPreview1(null); return; }
        const url = URL.createObjectURL(img1);
        setPreview1(url);
        return () => URL.revokeObjectURL(url);
    }, [img1]);

    useEffect(() => {
        if (!img2) { setPreview2(null); return; }
        const url = URL.createObjectURL(img2);
        setPreview2(url);
        return () => URL.revokeObjectURL(url);
    }, [img2]);

    useEffect(() => {
        setLoading(false);
    }, [currentStep]);

    const handleCompare = async () => {
        setError(null);
        setResult(null);
        setLoading(true);
        try {
            const res = await compareFaces(img1, img2);
            setResult(res);
            setCurrentStep(2);
        } catch (err) {
            setError(err.message);
            setLoading(false);
        }
    };

    const handleReset = () => {
        setImg1(null);
        setImg2(null);
        setResult(null);
        setError(null);
        setCurrentStep(1);
    };

    const samePose = result
        ? POSE_LABEL(result.face1.pose) === POSE_LABEL(result.face2.pose)
        : null;

    return (
        <div className="flex-1 flex items-center justify-center py-10">

            {/* Step 1 — Upload */}
            {currentStep === 1 && (
                <div className="flex flex-col items-center gap-y-8">
                    <div className="flex gap-24 justify-center">
                        <ImageUploader title="Person 1" setImg={setImg1} preview={preview1} />
                        <ImageUploader title="Person 2" setImg={setImg2} preview={preview2} />
                    </div>

                    {error && (
                        <span className="text-red-400 text-sm">{error}</span>
                    )}

                    <button
                        onClick={handleCompare}
                        disabled={!img1 || !img2 || loading}
                        className={`px-8 py-2 rounded-lg font-semibold text-white
                            ${loading || !img1 || !img2
                                ? "bg-gray-600 cursor-not-allowed"
                                : "bg-blue-600 hover:bg-blue-700"
                            }`}
                    >
                        {loading ? "Comparing..." : "Compare Faces"}
                    </button>
                </div>
            )}

            {/* Step 2 — Results */}
            {currentStep === 2 && result && result.scores && result.face1 && result.face2 && (
                <div className="flex flex-col items-center gap-y-8 w-full max-w-3xl px-4">

                    {/* Face cards */}
                    <div className="flex gap-16 justify-center flex-wrap">
                        <DetectedFace
                            title="Person 1"
                            imageSrc={preview1}
                            bbox={result.face1.bbox}
                            age={result.face1.age}
                            gender={result.face1.gender}
                            pose={result.face1.pose}
                        />
                        <DetectedFace
                            title="Person 2"
                            imageSrc={preview2}
                            bbox={result.face2.bbox}
                            age={result.face2.age}
                            gender={result.face2.gender}
                            pose={result.face2.pose}
                        />
                    </div>

                    {/* Same pose comparison */}
                    <span className="text-sm">
                        <span className="text-gray-400">Same pose: </span>
                        <span className={samePose ? "text-green-400 font-semibold" : "text-red-400 font-semibold"}>
                            {samePose ? "Yes" : "No"}
                        </span>
                    </span>

                    {/* Overall score */}
                    <div className="flex flex-col items-center gap-y-1">
                        <span className="text-white text-5xl font-bold">
                            {Math.round(result.similarity * 100)}%
                        </span>
                        <span className="text-gray-400 text-sm">similarity</span>
                    </div>

                    {/* Verdict message */}
                    <SimilarityMessage score={result.similarity} />

                    {/* Score breakdown */}
                    <div className="w-full max-w-md flex flex-col gap-y-3">
                        <span className="text-gray-400 text-xs uppercase tracking-widest mb-1">
                            Score Breakdown
                        </span>
                        {Object.entries(result.scores).map(([key, value]) => (
                            <ScoreBar
                                key={key}
                                label={SCORE_LABELS[key] ?? key}
                                value={value}
                            />
                        ))}
                    </div>

                    {/* Compare again */}
                    <button
                        onClick={handleReset}
                        className="px-6 py-2 rounded-lg font-semibold text-white bg-gray-700 hover:bg-gray-600"
                    >
                        Compare Again
                    </button>

                </div>
            )}
        </div>
    );
}
