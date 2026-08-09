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

const REGION_COLORS = {
    jawline: "#a855f7",
    eyebrows: "#f97316",
    eyes: "#38bdf8",
    nose: "#eab308",
    mouth: "#ec4899",
};

export default function DetectedFace({ title, imageSrc, bbox, age, gender, pose, landmarks }) {

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

            // Replicate `object-fit: cover; object-position: center`: the image is
            // scaled uniformly to cover the box, then the overflow is cropped evenly
            // from both sides on whichever axis overflows.
            const scale = Math.max(displayWidth / naturalWidth, displayHeight / naturalHeight);
            const offsetX = (displayWidth - naturalWidth * scale) / 2;
            const offsetY = (displayHeight - naturalHeight * scale) / 2;
            const toCanvas = ([x, y]) => [x * scale + offsetX, y * scale + offsetY];

            ctx.clearRect(0, 0, canvas.width, canvas.height);

            const [x1, y1, x2, y2] = bbox;
            ctx.strokeStyle = "#22c55e";
            ctx.lineWidth = 3;
            ctx.strokeRect(
                x1 * scale + offsetX,
                y1 * scale + offsetY,
                (x2 - x1) * scale,
                (y2 - y1) * scale
            );

            if (!landmarks) return;

            const drawPath = (points, closed) => {
                if (!points || points.length < 2) return;
                ctx.beginPath();
                points.forEach((p, i) => {
                    const [cx, cy] = toCanvas(p);
                    if (i === 0) ctx.moveTo(cx, cy);
                    else ctx.lineTo(cx, cy);
                });
                if (closed) ctx.closePath();
                ctx.stroke();
            };

            Object.entries(landmarks).forEach(([region, points]) => {
                ctx.strokeStyle = REGION_COLORS[region] ?? "#ffffff";
                ctx.lineWidth = 2;
                // eyebrows/eyes/mouth are arrays of separate arcs; jawline/nose are one
                const isMultiPath = Array.isArray(points[0][0]);
                const closed = region === "eyes" || region === "mouth";
                if (isMultiPath) points.forEach((sub) => drawPath(sub, closed));
                else drawPath(points, false);
            });
        };

        if (img.complete) {
            draw();
        } else {
            img.onload = draw;
        }
        window.addEventListener("resize", draw);
        return () => window.removeEventListener("resize", draw);
    }, [bbox, landmarks]);

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
