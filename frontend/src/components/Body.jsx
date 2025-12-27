import { useState, useEffect } from "react";
import ImageUploader from "./imageUploader"
// import { compareFaces } from "./api";

export default function Body() {
    const [img1, setImg1] = useState(null);
    const [img2, setImg2] = useState(null);
    const [preview1, setPreview1] = useState(null);
    const [preview2, setPreview2] = useState(null);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const [currentStep, setCurrentStep] = useState(1)



//     useEffect(() => {
//         if (!img1) {
//           setPreview1(null);
//           return;
//         }
//         const url = URL.createObjectURL(img1);
//         setPreview1(url);
//         return () => URL.revokeObjectURL(url);
//     }, [img1]);

  return (
    <div className="w-screen h-screen flex items-center justify-center ">

        {/* Upload section */}
        {currentStep === 1 &&(
            <div className="flex flex-row gap-x-16 justify-center items-center">
                <ImageUploader title={"Person 1"} setImg={setImg1} preview={preview1}/>
                <ImageUploader title={"Person 2"} setImg={setImg2} preview={preview2}/>
            </div>)
        }
    </div>
  );
}
