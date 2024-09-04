import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import HighchartsVuePlugin from '../plugins/highcharts-vue.js'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'

const app = createApp(App)

app.use(HighchartsVuePlugin)
app.use(router)
app.use(Antd)

app.mount('#app')
