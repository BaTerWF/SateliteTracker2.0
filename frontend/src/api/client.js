import axios from 'axios';

const apiClient = axios.create({
  // Задаем базовый URL для всех запросов
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: срабатывает перед каждой отправкой запроса
apiClient.interceptors.request.use(
  (config) => {
    // Достаем ключ из переменных окружения Vite
    const apiKey = import.meta.env.VITE_API_KEY;
    
    // Если ключ есть, добавляем его в заголовки
    if (apiKey) {
      config.headers['X-API-Key'] = apiKey;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor: обрабатывает ответы сервера
apiClient.interceptors.response.use(
  (response) => {
    // Сразу возвращаем data, чтобы не писать res.data в компонентах
    return response.data;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export default apiClient;