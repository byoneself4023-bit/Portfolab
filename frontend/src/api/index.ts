import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://port-0-flask-mjfnx06q4cbf889f.sel3.cloudtype.app';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터 - 토큰 자동 추가
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 응답 인터셉터 - 401 에러 처리
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (data: { email: string; password: string; nickname: string }) =>
    api.post('/auth/register', data),
  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),
};

// Stock API
export const stockAPI = {
  getList: () => api.get('/stock/list'),
  search: (query: string) => api.get(`/stock/search?q=${query}`),
  getDetail: (symbol: string) => api.get(`/stock/${symbol}`),
};

// Portfolio API
export const portfolioAPI = {
  create: (data: { name: string; description?: string }) =>
    api.post('/portfolio', data),
  getList: () => api.get('/portfolio'),
  getDetail: (portfolioNo: number) => api.get(`/portfolio/${portfolioNo}`),
  delete: (portfolioNo: number) => api.delete(`/portfolio/${portfolioNo}`),
  // 종목 관련 추가
  getStocks: (portfolioNo: number) => api.get(`/portfolio/${portfolioNo}/stock`),
  addStock: (portfolioNo: number, data: { stock_no: number; quantity: number; avg_price: number }) =>
    api.post(`/portfolio/${portfolioNo}/stock`, data),
  updateStock: (portfolioNo: number, stockNo: number, data: { quantity: number; avg_price: number }) =>
    api.put(`/portfolio/${portfolioNo}/stock/${stockNo}`, data),
  removeStock: (portfolioNo: number, stockNo: number) =>
    api.delete(`/portfolio/${portfolioNo}/stock/${stockNo}`),
};

// Simulation API
export const simulationAPI = {
  preview: (portfolioNo: number, changes: any[]) =>
    api.post(`/simulation/${portfolioNo}/preview`, { changes }),
  
  // Markowitz 최적화
  optimize: (portfolioNo: number) =>
    api.get(`/simulation/${portfolioNo}/optimize`),
  
  // Monte Carlo 시뮬레이션
  monteCarlo: (portfolioNo: number, years: number = 10, simulations: number = 1000) =>
    api.get(`/simulation/${portfolioNo}/monte-carlo?years=${years}&simulations=${simulations}`),
};

// AI API
export const aiAPI = {
  analyze: (portfolioNo: number) => api.get(`/ai/analyze/${portfolioNo}`),
  rebalance: (portfolioNo: number, targetVolatility?: number) =>
    api.get(`/ai/rebalance/${portfolioNo}${targetVolatility ? `?target=${targetVolatility}` : ''}`),
  explainMetrics: (volatility: number, sharpeRatio: number) =>
    api.get(`/ai/explain?volatility=${volatility}&sharpe=${sharpeRatio}`),
};

export default api;