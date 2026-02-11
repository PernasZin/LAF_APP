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
    
    // If on preview domain, use relative path (proxy handles routing)
    if (hostname.includes('preview.emergentagent.com')) {
      return '';
    }
    
    // If on localhost, need to use the full preview URL for API calls
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      const envBackendUrl = process.env.EXPO_PUBLIC_BACKEND_URL;
      if (envBackendUrl) {
        return envBackendUrl;
      }
    }
  }
  
  // First try app.json extra (works in Expo Go and production builds)
  const extraBackendUrl = Constants.expoConfig?.extra?.BACKEND_URL;
  if (extraBackendUrl) {
    console.log('📡 Using BACKEND_URL from app.json:', extraBackendUrl);
    return extraBackendUrl;
  }
  
  // Fallback to environment variable (works in development)
  const envBackendUrl = process.env.EXPO_PUBLIC_BACKEND_URL;
  if (envBackendUrl) {
    console.log('📡 Using BACKEND_URL from env:', envBackendUrl);
    return envBackendUrl;
  }
  
  // Default fallback
  console.log('📡 Using default BACKEND_URL');
  return 'https://macro-safety-caps.preview.emergentagent.com';
};

export const config = {
  BACKEND_URL: getBackendUrl(),
};

export default config;
