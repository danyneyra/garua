import axios from "axios";

export const apiURL = import.meta.env.VITE_API_URL || "http://127.0.0.1:4000/api";

console.log("API URL:", import.meta.env.VITE_API_URL);

export const api = axios.create({
  baseURL: `${apiURL}/api`,
  timeout: 10000,
});
