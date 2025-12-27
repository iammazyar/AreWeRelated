import { useState } from "react";


export default function ImageUploader({title, setImg, preview}) {

    return(
        <>
            <div className="flex flex-col items-center gap-y-4 w-80">
                <div className="">
                     {preview ? (
                        <img
                          src={preview}
                          alt={`preview of the ${title}`}
                          className="w-full h-full object-cover rounded-lg"
                        />) : (
                        <span>
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
{/*                 {preview ? ( */}
{/*                     <label className="text-sm font-medium mb-2"> */}
{/*                         {title} */}
{/*                     </label> */}
{/*                     ) : null */}
{/*                 } */}
            </div>
        </>
    )
}