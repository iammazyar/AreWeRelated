import { useState, useEffect } from "react";
import ImageUploader from "./imageUploader"
import DetectedFace from "./Results"
import { compareFaces } from "../api";

export default function Body() {
    const [img1, setImg1] = useState(null);
    const [img2, setImg2] = useState(null);
    const [preview1, setPreview1] = useState(null);
    const [preview2, setPreview2] = useState(null);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const [currentStep, setCurrentStep] = useState(1)



    useEffect(() => {
        if (!img1) {
          setPreview1(null);
          return;
        }
        const url = URL.createObjectURL(img1);
        setPreview1(url);
        return () => URL.revokeObjectURL(url);
    }, [img1]);

    useEffect(() => {
        if (!img2) {
          setPreview2(null);
          return;
        }
        const url = URL.createObjectURL(img2);
        setPreview2(url);
        return () => URL.revokeObjectURL(url);
    }, [img2]);

    useEffect(() => {
        setLoading(false)
    }, [currentStep]);

    const handleCompare = async () => {
        setError(null);
        setResult(null);
        setLoading(true);

        try {
          const res = await compareFaces(img1, img2);
          setResult(res);
          setCurrentStep(2)
          console.log(res)
        }
        catch (err) {
          setError(err.message);
        }
    };

  return (
    <div className="w-screen h-screen flex items-center justify-center bg-black ">

        {/* Upload section */}
        {currentStep === 1 &&(
            <div>
                <div className="flex gap-24 justify-center ms-32">
                    <ImageUploader title={"Person 1"} setImg={setImg1} preview={preview1}/>
                    <ImageUploader title={"Person 2"} setImg={setImg2} preview={preview2}/>
                </div>
                <div className="flex justify-center mb-6">
                    <button
                        onClick={handleCompare}
                        disabled={!img1 || !img2 || loading}
                        className={`px-8 py-2 rounded-lg font-semibold text-white
                          ${
                            loading || !img1 || !img2
                              ? "bg-gray-400 cursor-not-allowed"
                              : "bg-blue-600 hover:bg-blue-700"
                          }`}
                    >
                        {loading ? "Comparing..." : "Compare Faces"}
                    </button>
                </div>
            </div>
            )
        }
        {/* Results */}
        {currentStep === 2 && (
                <div>
                <div>
                    <div className="flex gap-24 justify-center ms-32">
                        <DetectedFace title={"Person 1"} imageSrc={preview1} bbox={result.face1.bbox} />
                        <DetectedFace title={"Person 2"} imageSrc={preview2} bbox={result.face2.bbox} />
                    </div>
                </div>
                <div className="flex justify-center mb-6">
                    {
                        result.similarity >= 0.8 ? (
                            <span className="text-blue-600 dark:text-sky-400 text-sm font-medium mb-2">
                                You look so much alike, I got confused that you might be the same person. Are you really ?
                            </span>
                        ) : result.similarity >= 0.6 ? (
                            <span className="text-blue-600 dark:text-sky-400 text-sm font-medium mb-2">
                                You look so much alike that if you’re actually two different people, you might have a serious talk with your father oorrrr your mom!!
                            </span>
                        ) : result.similarity >= 0.45 ? (
                            <span className="text-blue-600 dark:text-sky-400 text-sm font-medium mb-2">
                                You have a few similarities, but there’s still a decent chance one of your parents was… not exactly a model citizen.
                            </span>
                        ) : (
                            <span className="text-blue-600 dark:text-sky-400 text-sm font-medium mb-2">
                                You have no similarities at all dudes, congratulations to your parents.
                            </span>
                        )

                    }
                </div>
                </div>
                )
        }
    </div>
  );
}
