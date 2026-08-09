import { useState } from "react";

const MAX_DIMENSION = 320; // matches the w-80 h-80 preview box below
const JPEG_QUALITY = 0.85;

async function resizeImage(file, maxDim = MAX_DIMENSION, quality = JPEG_QUALITY) {
    const bitmap = await createImageBitmap(file, { imageOrientation: "from-image" });
    const scale = Math.min(1, maxDim / Math.max(bitmap.width, bitmap.height));

    if (scale === 1) {
        bitmap.close();
        return file;
    }

    const canvas = document.createElement("canvas");
    canvas.width = Math.round(bitmap.width * scale);
    canvas.height = Math.round(bitmap.height * scale);
    canvas.getContext("2d").drawImage(bitmap, 0, 0, canvas.width, canvas.height);
    bitmap.close();

    const blob = await new Promise((resolve) => canvas.toBlob(resolve, "image/jpeg", quality));
    return new File([blob], file.name.replace(/\.\w+$/, "") + ".jpg", { type: "image/jpeg" });
}

export default function ImageUploader({title, setImg, preview}) {

    const handleFileChange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        setImg(await resizeImage(file));
    };

    return(
        <div className="flex flex-col items-center gap-y-4 w-80">
            <div className="w-80 h-80 flex items-center justify-center border-2 border-dashed border-gray-600 rounded-lg">
                 {preview ? (
                    <img
                      src={preview}
                      alt={`preview of the ${title}`}
                      className="object-cover rounded-lg"
                    />
                    ): (
                    <span className="text-gray-400">
                        {`select a picture for ${title}`}
                    </span>)
                 }
            </div>
            <input
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              className="border border-gray-800 file:input-bordered file:input-primary file:btn file:btn-sm
               text-white border border-gray-600 rounded-lg
               cursor-pointer"
            />
            <div>

                {preview ? (
                    <span className="text-blue-600 dark:text-sky-400 text-sm font-medium mb-2">
                        {title}
                    </span>
                    ):null
                }
            </div>

        </div>
    )
}