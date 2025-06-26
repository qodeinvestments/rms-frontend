import { PublicClientApplication } from '@azure/msal-browser';

export const msalConfig = {
  auth: {
    clientId: '4c85eef0-b639-4bc1-9ca0-5e748cf8362c',
    authority: 'https://login.microsoftonline.com/34e64400-bcc0-4bd1-9a1a-d74ae51cf680',
    redirectUri: 'http://localhost:5175/',
  },
  cache: {
    cacheLocation: 'localStorage', // Configures cache location
    storeAuthStateInCookie: false, // Set to true for IE 11 or Edge
  }
};

// Login request configuration
export const loginRequest = {
  scopes: ["User.Read"],
  prompt: "select_account"
};

export const msalInstance = new PublicClientApplication(msalConfig); 
