import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import HighchartsVuePlugin from '../plugins/highcharts-vue.js'

const app = createApp(App)

app.use(HighchartsVuePlugin)
app.use(router)

app.mount('#app')
