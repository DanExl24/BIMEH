import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.bimeh.app',
  appName: 'BIMEH',
  webDir: 'dist',
  server: {
    androidScheme: 'https'
  }
};

export default config;
