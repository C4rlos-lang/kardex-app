import { createRouter, createWebHistory } from 'vue-router'
import Productos from '../views/Productos.vue'

const routes = [
  { path: '/', redirect: '/productos' },
  { path: '/productos', component: Productos },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router