import axios from "axios";

const apiUrl = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "");
const api = axios.create({
  baseURL: apiUrl,
  timeout: 30000
});

export async function compareFaces(img1, img2) {
  const formData = new FormData();
  formData.append("img1", img1);
  formData.append("img2", img2);

  try {
    const response = await api.post("/compare", formData, {
      headers: {
        "Content-Type": "multipart/form-data"
      }
    });

    return response.data;
  }
  catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || error.response.data.error || "Server error");
    } else if (error.request) {
      throw new Error(`Could not reach the backend at ${apiUrl}. Make sure the server is running.`);
    } else {
      throw new Error(error.message);
    }
  }
}
