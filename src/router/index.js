import { createRouter, createWebHistory } from 'vue-router'
import UserPage from '../components/UserPage.vue'
import HomePage from '../components/HomePage.vue'
import SignalBook from '../components/SignalBook.vue'
import Errors from '../components/Errors.vue'
import Keydblogs from '../components/Keydblogs.vue'
import DataVisualizer from '../components/DataVisualizer.vue'
import UserLagData from '../components/UserLagData.vue'
import ServerData from '../components/ServerData.vue'
import PositionMismatch from '../components/PositionMismatch.vue'
import AdminPanel from '../components/AdminPanel.vue'
import MarginUpdate from '../components/MarginUpdate.vue'
import MarginUpdateUser from '../components/MarginUpdateUser.vue'
import LivePositions from '../components/TradingMonitor.vue'
import MarginSettings from '../components/MarginSettings.vue'
import BrokerPositioMisMatch from '../components/BrokerPositioMisMatch.vue'
import OpenTrades from '../components/OpenTrades.vue'
import SlippageUserPage from '../components/SlippageUserPage.vue'
import UserStrategyVar from '../components/UserStrategyVar.vue'
import DailyLogsTable from '../components/DailyLogsTable.vue'
import ReadDailyLog from  '../components/ReadDailyLog.vue'
import NewDailyLog from '../components/NewDailyLog.vue'
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomePage,
    },
    {
      path: '/user/:username',
      name: 'userPage',
      component: UserPage,
    },
    {
      path: '/user/lag/:username',
      name: 'userLagData',
      component: UserLagData,
    },
    ,
    {
      path: '/signalBook',
      name: 'SignalBook',
      component: SignalBook,
    },
    {
      path: '/errors',
      name: 'ErrorPage',
      component: Errors,
    },
    {
      path: '/keydblogs',
      name: 'Keydblogs',
      component: Keydblogs,
    },
    {
      path: '/visualize',
      name: 'Visualize',
      component: DataVisualizer,
    },
    {
      path: '/serverData',
      name: 'ServerData',
      component: ServerData,
    },
    {
      path: '/posmismatch',
      name: 'PositionMismatch',
      component: PositionMismatch,
    },
    {
      path:'/brokerposmismatch',
      name:'BrokerPositioMisMatch',
      component:BrokerPositioMisMatch
    },
    {
      path: '/adminPanel',
      name: 'AdminPanel',
      component:AdminPanel,
    },
    {
      path: '/marginUpdate',
      name: 'MarginUpdate',
      component:MarginUpdate,
    },
    {
      path: '/marginUpdate/:username',
      name: 'MarginUpdateUser',
      component:MarginUpdateUser,
    },
    {
      path: '/livepositions',
      name: 'LivePositions',
      component:LivePositions,
    },
    {
      path: '/marginSettings',
      name: 'MarginSettings',
      component:MarginSettings,
    },
    {
      path: '/opentrades',
      name:'OpenTrades',
      component:OpenTrades
    },
    {
      path:'/slippageUserPage',
      name:'SlippageUserPage',
      component:SlippageUserPage
    },
    {
      path:'/userstrategyvar',
      name:'UserStrategyVar',
      component:UserStrategyVar
    },
    {
      path:'/dailylogs',
      name:'DailyLogsTable',
      component:DailyLogsTable
    },
    {
      path:'/readlog/:id',
      name:'ReadDailyLog',
      component:ReadDailyLog
    },
    {
      path:'/newlog',
      name:'NewDailyLog',
      component:NewDailyLog
    }
    // {
    //   path: '/about',
    //   name: 'about',
    //   // route level code-splitting
    //   // this generates a separate chunk (About.[hash].js) for this route
    //   // which is lazy-loaded when the route is visited.
    //   component: () => import('../views/AboutView.vue')
    // }
  ],
})

export default router
