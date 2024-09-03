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
