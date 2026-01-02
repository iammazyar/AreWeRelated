import { useState, useEffect } from "react";



export default function Header() {
    return (
        <div className="flex overflow-x-hidden absolute items-center justify-center w-full p-2 text-2xl
         text-center text-white bg-gray-900  border border-gray-800 rounded-b-lg shadow-sm"  >
            <span>
                Are We Lookalike?
            </span>
        </div>
    )
}