import axios from 'axios';
import { toast } from '@/hooks/use-toast';
import { apiCache } from '@/utils/cache';

// Create axios instance with default config
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor with caching
api.interceptors.request.use(
  (config) => {
    // Add any auth tokens or custom headers here
    // const token = localStorage.getItem('auth_token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }

    // Check cache for GET requests
    if (config.method === 'get' && !config.params?.skipCache) {
      const cacheKey = apiCache.generateKey(config.url || '', config.params);
      const cachedData = apiCache.get(cacheKey);

      if (cachedData) {
        // Return cached response
        config.adapter = () => {
          return Promise.resolve({
            data: cachedData,
            status: 200,
            statusText: 'OK',
            headers: {},
            config,
          });
        };
      }
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor with caching
api.interceptors.response.use(
  (response) => {
    // Cache successful GET responses
    if (response.config.method === 'get' && response.status === 200) {
      const cacheKey = apiCache.generateKey(
        response.config.url || '',
        response.config.params
      );

      // Cache with different TTLs based on endpoint
      let ttl = 5 * 60 * 1000; // Default 5 minutes

      if (response.config.url?.includes('/statistics')) {
        ttl = 10 * 60 * 1000; // 10 minutes for statistics
      } else if (response.config.url?.includes('/articles/')) {
        ttl = 15 * 60 * 1000; // 15 minutes for article details
      } else if (response.config.url?.includes('/search')) {
        ttl = 3 * 60 * 1000; // 3 minutes for search results
      }

      apiCache.set(cacheKey, response.data, ttl);
    }

    return response;
  },
  (error) => {
    // Handle errors globally
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;

      switch (status) {
        case 400:
          toast({
            title: '请求参数错误',
            description: data.message || '请检查输入参数',
            variant: 'destructive',
          });
          break;
        case 401:
          toast({
            title: '未授权',
            description: '请重新登录',
            variant: 'destructive',
          });
          // Redirect to login if needed
          break;
        case 403:
          toast({
            title: '没有权限',
            description: '您没有权限访问此资源',
            variant: 'destructive',
          });
          break;
        case 404:
          toast({
            title: '资源不存在',
            description: '请求的资源未找到',
            variant: 'destructive',
          });
          break;
        case 500:
          toast({
            title: '服务器错误',
            description: '服务器内部错误，请稍后重试',
            variant: 'destructive',
          });
          break;
        case 503:
          toast({
            title: '服务不可用',
            description: '服务暂时不可用，请稍后重试',
            variant: 'destructive',
          });
          break;
        default:
          toast({
            title: '请求失败',
            description: data.message || '未知错误',
            variant: 'destructive',
          });
      }

      console.error('API Error:', status, data);
    } else if (error.request) {
      // Request made but no response
      toast({
        title: '网络错误',
        description: '网络连接失败，请检查网络',
        variant: 'destructive',
      });
      console.error('Network Error:', error.message);
    } else {
      // Error in request configuration
      toast({
        title: '请求配置错误',
        description: error.message,
        variant: 'destructive',
      });
      console.error('Request Error:', error.message);
    }

    return Promise.reject(error);
  }
);

// Export cache control functions
export const clearCache = () => apiCache.clear();
export const clearCacheByKey = (url: string, params?: any) => {
  const key = apiCache.generateKey(url, params);
  apiCache.delete(key);
};

export default api;
