import { createRouter, createWebHistory} from 'vue-router'
import RecordPage from '@/views/RecordPage.vue'

const routes = [
  {
    path: '/',
    name: 'record',
    component: RecordPage,
  },
  // 必要に応じてページを追加
  // {
  //   path: '/about',
  //   name: 'About',
  //   component: () => import('@/views/AboutPage.vue') // 遅延読み込み
  // }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router