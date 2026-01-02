import { useState } from "react";


export default function ImageUploader({title, setImg, preview}) {

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
              onChange={(e) => setImg(e.target.files[0])}
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