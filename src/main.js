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
  msalInstance.handleRedirectPromise().then(async (response) => {
    if (response?.account) {
      try {
        const tokenResponse = await msalInstance.acquireTokenSilent({
          account: response.account,
          scopes: ["User.Read"],
        });
        
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
          localStorage.setItem('access_token', data.access_token);
          localStorage.setItem('user_info', JSON.stringify(data.user));
          window.location.reload();
        }
        
      } catch (error) {
        console.error('Microsoft login error:', error);
      }
    }
  }).catch(error => console.error('MSAL redirect error:', error));
}).catch(error => console.error('MSAL initialization error:', error));

app.mount("#app");

// Register Service Worker for Background Notifications
if ("serviceWorker" in navigator) {
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


