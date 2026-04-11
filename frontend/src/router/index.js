import { createRouter, createWebHashHistory } from 'vue-router'
import Lista from '../views/Lista.vue'
import ListaAlmacenes from '../views/ListaAlmacenes.vue'
import POS from '../views/POS.vue'
import Arqueo from '../views/Arqueo.vue'
import Maestras from '../views/Maestras.vue'

const routes = [
  { path: '/', redirect: '/lista' },
  { path: '/lista', component: Lista },
  { path: '/lista-almacenes', component: ListaAlmacenes },
  { path: '/pos', component: POS },
  { path: '/arqueo', component: Arqueo },
  { path: '/maestras', component: Maestras },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router