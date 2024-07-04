import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import VueApexCharts from 'vue3-apexcharts'
import HighchartsVuePlugin from '../plugins/highcharts-vue.js'

const app = createApp(App)

app.use(HighchartsVuePlugin)
app.use(VueApexCharts)
app.use(router)

app.mount('#app')
