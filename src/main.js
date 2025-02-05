import "./assets/main.css";

import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import HighchartsVuePlugin from "../plugins/highcharts-vue.js";
import Antd from "ant-design-vue";
import "ant-design-vue/dist/reset.css";

const app = createApp(App);

app.use(HighchartsVuePlugin);
app.use(router);
app.use(Antd);

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


