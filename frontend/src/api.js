import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
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
      throw new Error("No response from server");
    } else {
      throw new Error(error.message);
    }
  }
}
