// Vercel Dashboard Configuration
// Configuration for QuantMuse Interactive Dashboard on Vercel

const config = {
  // API Configuration for Vercel deployment
  api: {
    // Base URL for API calls
    baseURL: process.env.NODE_ENV === 'production' 
      ? ''  // Empty for same-origin on Vercel
      : 'http://localhost:5000',  // Local development
    timeout: 10000,
    retries: 3
  },
  
  // WebSocket Configuration (disabled for Vercel)
  websocket: {
    enabled: false,  // WebSocket not supported on Vercel serverless
    fallbackPolling: true,
    pollInterval: 5000  // 5 seconds
  },
  
  // Dashboard Configuration
  dashboard: {
    title: 'QuantMuse Interactive Dashboard',
    version: '1.0.0',
    theme: 'light',
    autoRefresh: true,
    refreshInterval: 5000
  },
  
  // Mock Data Configuration
  mockData: {
    enabled: true,  // Enable mock data for Vercel deployment
    realTimeUpdates: true,
    priceVolatility: 0.001,
    updateFrequency: 2000
  },
  
  // Performance Configuration
  performance: {
    enableCaching: true,
    cacheTimeout: 30000,  // 30 seconds
    maxRetries: 3,
    retryDelay: 1000
  },
  
  // Error Handling
  errorHandling: {
    showNotifications: true,
    logErrors: true,
    fallbackToMock: true,
    retryFailedRequests: true
  }
};

// Export configuration for use in dashboard
if (typeof module !== 'undefined' && module.exports) {
  module.exports = config;
}

// Global configuration for browser
if (typeof window !== 'undefined') {
  window.QuantMuseConfig = config;
}
