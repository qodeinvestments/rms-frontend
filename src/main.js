import "./assets/main.css";

import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import HighchartsVuePlugin from "../plugins/highcharts-vue.js";
import Antd from "ant-design-vue";
import "ant-design-vue/dist/reset.css";
import { msalInstance } from "./msal";
import { API_BASE_URL, WS_BASE_URL } from './config/url'

const app = createApp(App);

app.use(HighchartsVuePlugin);
app.use(router);
app.use(Antd);

// Initialize MSAL and handle redirects
msalInstance.initialize().then(() => {
  // Handle redirect promise for Microsoft login
  msalInstance.handleRedirectPromise().then(async (response) => {
    if (response && response.account) {
      // Microsoft login was successful
      console.log('Microsoft login successful:', response.account);
      
      try {
        // Get access token from Microsoft
        const tokenResponse = await msalInstance.acquireTokenSilent({
          account: response.account,
          scopes: ["User.Read"],
        });
        
        // Send Microsoft token to your backend
        const backendResponse = await fetch(`${API_BASE_URL}microsoft-login`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            microsoft_token: tokenResponse.accessToken
          }),
        });
        
        const data = await backendResponse.json();
        
        if (data.success) {
          // Store your backend JWT token (same as normal login)
          localStorage.setItem('access_token', data.access_token);
          localStorage.setItem('user_info', JSON.stringify(data.user));
          
          console.log('Backend authentication successful');
          alert('Microsoft login successful!');
          
          // Clear the URL fragment and navigate to home using Vue Router
          window.history.replaceState({}, document.title, window.location.pathname);
          
          // Emit a custom event to notify the app of successful authentication
          window.dispatchEvent(new CustomEvent('auth-success'));
          
          // Navigate to home page
          router.push('/');
        } else {
          console.error('Backend authentication failed:', data.detail);
          alert(`Login failed: ${data.detail}`);
        }
        
      } catch (error) {
        console.error('Error during Microsoft login process:', error);
        alert('Error completing Microsoft login. Please try again.');
      }
    } else if (window.location.hash.includes('code=')) {
      // If we have auth params but no response, clear the URL
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }).catch((error) => {
    console.error('MSAL redirect handling error:', error);
    // Clear URL if there's an error
    if (window.location.hash.includes('code=')) {
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  });
}).catch((error) => {
  console.error('MSAL initialization error:', error);
});

app.mount("#app");

// Register Service Worker for Background Notifications
if ("serviceWorker" in navigator) {  // No import required
    window.addEventListener("load", () => {
        navigator.serviceWorker
            .register("/service-worker.js")
            .then((registration) => {
                console.log("Service Worker registered with scope:", registration.scope);
            })
            .catch((error) => {
                console.error("Service Worker registration failed:", error);
            });
    });
}


