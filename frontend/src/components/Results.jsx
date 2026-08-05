import { useRef, useEffect } from "react";

const GENDER_LABEL = { 0: "Female", 1: "Male" };

export const POSE_LABEL = (pose) => {
    if (!Array.isArray(pose)) return "Unknown";
    const [pitch, yaw, roll] = pose;
    const yawAbs = Math.abs(yaw);
    if (yawAbs < 15) return "Frontal";
    if (yawAbs < 40) return yaw > 0 ? "Slight Right Turn" : "Slight Left Turn";
    return yaw > 0 ? "Right Profile" : "Left Profile";
};

export default function DetectedFace({ title, imageSrc, bbox, age, gender, pose }) {

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

            // Canvas is sized to match the rendered image and lives in the
            // same relative container, so it scrolls naturally with it.
            canvas.width = displayWidth;
            canvas.height = displayHeight;

            const scaleX = displayWidth / naturalWidth;
            const scaleY = displayHeight / naturalHeight;

            const [x1, y1, x2, y2] = bbox;
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.strokeStyle = "#22c55e";
            ctx.lineWidth = 3;
            ctx.strokeRect(
                x1 * scaleX,
                y1 * scaleY,
                (x2 - x1) * scaleX,
                (y2 - y1) * scaleY
            );
        };

        if (img.complete) {
            draw();
        } else {
            img.onload = draw;
        }
        window.addEventListener("resize", draw);
        return () => window.removeEventListener("resize", draw);
    }, [bbox]);

    return (
        <div className="flex flex-col items-center gap-y-3 w-80">

            {/* Title */}
            <span className="text-white font-semibold text-base">{title}</span>

            {/* Image + canvas stacked in the same relative container */}
            <div className="relative w-80 h-80 border-2 border-dashed border-gray-600 rounded-lg overflow-hidden">
                <img
                    ref={imgRef}
                    src={imageSrc}
                    alt={title}
                    className="w-full h-full object-cover rounded-lg"
                />
                <canvas
                    ref={canvasRef}
                    className="absolute inset-0 pointer-events-none"
                />
            </div>

            {/* Per-person info */}
            <div className="w-full flex flex-col gap-y-1 px-1">
                <InfoRow label="Age"    value={`~${age} years old`} />
                <InfoRow label="Gender" value={GENDER_LABEL[gender] ?? "Unknown"} />
                <InfoRow label="Pose"   value={POSE_LABEL(pose)} />
            </div>

        </div>
    );
}

function InfoRow({ label, value }) {
    return (
        <div className="flex justify-between text-sm">
            <span className="text-gray-400">{label}</span>
            <span className="text-white font-medium">{value}</span>
        </div>
    );
}
