import { createApp } from 'vue' // Importing createApp from vue, though we don't use it here
import HighchartsVue from 'highcharts-vue'

export default {
  install(app) {
    app.use(HighchartsVue)
  },
}
