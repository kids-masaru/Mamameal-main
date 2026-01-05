// API configuration
// In production (Vercel), set NEXT_PUBLIC_API_URL environment variable
// to point to the Railway backend URL

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default API_URL;
