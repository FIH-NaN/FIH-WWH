import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
});

// TODO: Add interceptors for auth tokens here

export default api;