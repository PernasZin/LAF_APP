/**
 * App Configuration
 * =================
 * Centralized configuration for the app
 * Uses expo-constants to access app.json extra field
 */

import Constants from 'expo-constants';
import { Platform } from 'react-native';

// Get backend URL from app.json extra field (for production builds)
// or from environment variable (for development)
const getBackendUrl = (): string => {
  // For web running on localhost, use relative path (Kubernetes proxy handles routing)
  if (Platform.OS === 'web' && typeof window !== 'undefined') {
    const hostname = window.location?.hostname;
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return ''; // Use relative paths like /api/auth/login
    }
  }
  
  // First try app.json extra (works in production builds)
  const extraBackendUrl = Constants.expoConfig?.extra?.BACKEND_URL;
  if (extraBackendUrl) {
    return extraBackendUrl;
  }
  
  // Fallback to environment variable (works in development)
  const envBackendUrl = process.env.EXPO_PUBLIC_BACKEND_URL;
  if (envBackendUrl) {
    return envBackendUrl;
  }
  
  // Default fallback
  return 'https://nutriflow-38.preview.emergentagent.com';
};

export const config = {
  BACKEND_URL: getBackendUrl(),
};

export default config;
