import { createRouter, createWebHashHistory } from 'vue-router'
import Productos from '../views/Productos.vue'
import Lista from '../views/Lista.vue'
import Almacenes from '../views/Almacenes.vue'

const routes = [
  { path: '/', redirect: '/productos' },
  { path: '/productos', component: Productos },
  { path: '/lista', component: Lista },
  { path: '/almacenes', component: Almacenes },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router