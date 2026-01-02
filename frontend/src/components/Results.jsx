import { useState, useRef, useEffect } from "react";


export default function DetectedFace({title, imageSrc, bbox, similarityScore}) {

    const imgRef = useRef(null);
    const canvasRef = useRef(null);


    useEffect(() => {
        const img = imgRef.current;
        const canvas = canvasRef.current;

        const ctx = canvas.getContext("2d");
        const draw = () => {
            const { naturalWidth, naturalHeight } = img;
            const displayWidth = img.clientWidth;
            const displayHeight = img.clientHeight;

            const imgRect = img.getBoundingClientRect();
            // Position canvas exactly on top of image
            canvas.style.position = "fixed";
            canvas.style.left = `${imgRect.left}px`;
            canvas.style.top = `${imgRect.top}px`;

            canvas.width = imgRect.width;
            canvas.height = imgRect.height;

            // Scale factors
            const scaleX = displayWidth / naturalWidth;
            const scaleY = displayHeight / naturalHeight;

            const [x1, y1, x2, y2] = bbox;
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.strokeStyle = "green";
            ctx.lineWidth = 4;

            ctx.strokeRect(
                x1 * scaleX,
                y1 * scaleY,
                (x2 - x1) * scaleX,
                (y2 - y1) * scaleY
            );
        }
        // Draw once image is loaded
        if (img.complete) {
            draw();
        } else {
            img.onload = draw;
        }
        // Redraw on resize (responsive layouts)
        window.addEventListener("resize", draw);
        return () => window.removeEventListener("resize", draw);
    },[bbox]);

    return(
        <div className="flex flex-col items-center gap-y-4 w-80">
            <div className="w-80 h-80 flex items-center justify-center border-2 border-dashed border-gray-600 rounded-lg">
                <img
                    ref={imgRef}
                    src={imageSrc}
                    alt={title}
                />
                <canvas
                    ref={canvasRef}
                    className="absolute top-0 left-0 pointer-events-none"
                />
            </div>
        </div>
    )

}