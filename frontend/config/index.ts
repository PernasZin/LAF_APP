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
  // For web, we need to determine if we're on the preview domain or localhost
  if (Platform.OS === 'web' && typeof window !== 'undefined') {
    const hostname = window.location?.hostname;
    
    // If on localhost, need to use the full preview URL for API calls
    // because there's no local proxy configured
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      // Use environment variable or default to preview domain
      const envBackendUrl = process.env.EXPO_PUBLIC_BACKEND_URL;
      if (envBackendUrl) {
        return envBackendUrl;
      }
      return 'https://nutriflow-38.preview.emergentagent.com';
    }
    
    // If on preview domain, use relative path (proxy handles routing)
    if (hostname.includes('preview.emergentagent.com')) {
      return '';
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
