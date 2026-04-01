import { createRouter, createWebHashHistory } from 'vue-router'
import Productos from '../views/Productos.vue'
import Lista from '../views/Lista.vue'

const routes = [
  { path: '/', redirect: '/productos' },
  { path: '/productos', component: Productos },
  { path: '/lista', component: Lista },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router