import { createRouter, createWebHistory } from 'vue-router'
import Productos from '../views/Productos.vue'
import Lista from '../views/Lista.vue'

const routes = [
  { path: '/', redirect: '/productos' },
  { path: '/productos', component: Productos },
  { path: '/lista', component: Lista },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router