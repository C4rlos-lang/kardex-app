<template>
  <div>
    <h1>📊 Dashboard</h1>
    <p v-if="cargando" class="cargando">Cargando indicadores...</p>

    <div v-else class="dashboard-grid">

      <!-- TENDENCIAS -->
      <div class="seccion">
        <h2>📈 Tendencias</h2>
        <div class="cards-row">
          <div class="card">
            <p class="card-label">Producto más vendido</p>
            <p class="card-valor">{{ data.tendencias.producto_top || 'Sin datos' }}</p>
          </div>
          <div class="card">
            <p class="card-label">Talla más vendida</p>
            <p class="card-valor">{{ data.tendencias.talla_top || 'Sin datos' }}</p>
          </div>
        </div>

        <div class="grafico-wrap">
          <p class="grafico-titulo">Ventas por mes</p>
          <div class="barras">
            <div
              v-for="v in data.tendencias.ventas_por_mes" :key="v.mes"
              class="barra-wrap"
            >
              <div
                class="barra"
                :style="{ height: alturaBarra(v.total, maxMes) + 'px' }"
              ></div>
              <p class="barra-label">{{ nombreMes(v.mes) }}</p>
              <p class="barra-valor">${{ formatNum(v.total) }}</p>
            </div>
          </div>
        </div>

        <div class="grafico-wrap">
          <p class="grafico-titulo">Ventas por día de la semana</p>
          <div class="barras">
            <div
              v-for="v in data.tendencias.ventas_por_dia" :key="v.dia"
              class="barra-wrap"
            >
              <div
                class="barra barra-dia"
                :style="{ height: alturaBarra(v.total, maxDia) + 'px' }"
              ></div>
              <p class="barra-label">{{ nombreDia(v.dia) }}</p>
              <p class="barra-valor">{{ v.total }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- INVENTARIO -->
      <div class="seccion">
        <h2>📦 Inventario</h2>
        <div class="cards-row">
          <div class="card">
            <p class="card-label">Total productos</p>
            <p class="card-valor">{{ data.inventario.total_productos }}</p>
          </div>
          <div class="card card-alerta">
            <p class="card-label">⚠️ Stock bajo</p>
            <p class="card-valor alerta">{{ data.inventario.stock_bajo }}</p>
            <p class="card-sub">productos con menos de 5 unidades</p>
          </div>
        </div>
      </div>

      <!-- CLIENTES -->
      <div class="seccion">
        <h2>👥 Clientes</h2>
        <div class="cards-row">
          <div class="card">
            <p class="card-label">Total clientes</p>
            <p class="card-valor">{{ data.clientes.total_clientes }}</p>
          </div>
          <div class="card">
            <p class="card-label">Nuevos este mes</p>
            <p class="card-valor">{{ data.clientes.clientes_nuevos_mes }}</p>
          </div>
          <div class="card">
            <p class="card-label">Género más frecuente</p>
            <p class="card-valor">{{ data.clientes.genero_top || 'Sin datos' }}</p>
          </div>
          <div class="card">
            <p class="card-label">Clientes recurrentes</p>
            <p class="card-valor">{{ data.clientes.clientes_recurrentes }}</p>
          </div>
          <div class="card">
            <p class="card-label">Promedio de compras</p>
            <p class="card-valor">{{ data.clientes.promedio_compras }}x</p>
          </div>
        </div>
      </div>

      <!-- FINANCIERO -->
      <div class="seccion">
        <h2>💰 Financiero</h2>
        <div class="cards-row">
          <div class="card card-verde">
            <p class="card-label">Ventas este mes</p>
            <p class="card-valor verde">${{ formatNum(data.financiero.ventas_mes) }}</p>
          </div>
          <div class="card">
            <p class="card-label">Total ventas</p>
            <p class="card-valor">{{ data.financiero.total_ventas }}</p>
          </div>
          <div class="card">
            <p class="card-label">Ticket promedio</p>
            <p class="card-valor">${{ formatNum(data.financiero.ticket_promedio) }}</p>
          </div>
          <div class="card">
            <p class="card-label">Método más usado</p>
            <p class="card-valor">{{ data.financiero.metodo_top || 'Sin datos' }}</p>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import axios from 'axios'

const API = 'https://kardex-app.onrender.com'

export default {
  data() {
    return {
      cargando: true,
      data: {
        tendencias: { producto_top: null, talla_top: null, ventas_por_mes: [], ventas_por_dia: [], ventas_por_semana: [] },
        inventario: { total_productos: 0, stock_bajo: 0 },
        clientes: { total_clientes: 0, genero_top: null, clientes_nuevos_mes: 0, clientes_recurrentes: 0, promedio_compras: 0 },
        financiero: { ventas_mes: 0, metodo_top: null, ticket_promedio: 0, total_ventas: 0 }
      }
    }
  },
  computed: {
    maxMes() {
      return Math.max(...this.data.tendencias.ventas_por_mes.map(v => v.total), 1)
    },
    maxDia() {
      return Math.max(...this.data.tendencias.ventas_por_dia.map(v => v.total), 1)
    }
  },
  methods: {
    alturaBarra(valor, max) {
      return Math.max((valor / max) * 120, 4)
    },
    formatNum(n) {
      return Number(n).toLocaleString('es-CO')
    },
    nombreMes(n) {
      const meses = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
      return meses[n - 1] || n
    },
    nombreDia(n) {
      const dias = ['Dom','Lun','Mar','Mié','Jue','Vie','Sáb']
      return dias[n] || n
    }
  },
  async mounted() {
    try {
      const { data } = await axios.get(`${API}/dashboard`)
      this.data = data
    } catch (error) {
      console.error('Error cargando dashboard', error)
    }
    this.cargando = false
  }
}
</script>

<style scoped>
h1 { margin-bottom: 24px; color: #1B3A6B; }
h2 { font-size: 16px; color: #1B3A6B; margin-bottom: 16px; }
.cargando { color: #888; }
.dashboard-grid { display: flex; flex-direction: column; gap: 32px; }
.seccion {
  background: white; border-radius: 12px;
  padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.cards-row { display: flex; flex-wrap: wrap; gap: 16px; margin-bottom: 24px; }
.card {
  background: #F2F4F7; border-radius: 10px;
  padding: 16px 20px; min-width: 160px; flex: 1;
}
.card-verde { background: #d4edda; }
.card-alerta { background: #fff3cd; }
.card-label { font-size: 12px; color: #888; margin-bottom: 8px; }
.card-valor { font-size: 24px; font-weight: 600; color: #1B3A6B; }
.card-valor.verde { color: #1E7E50; }
.card-valor.alerta { color: #D35400; }
.card-sub { font-size: 11px; color: #888; margin-top: 4px; }
.grafico-wrap { margin-top: 16px; }
.grafico-titulo { font-size: 13px; color: #555; margin-bottom: 12px; font-weight: 500; }
.barras {
  display: flex; align-items: flex-end;
  gap: 12px; height: 150px;
  border-bottom: 2px solid #eee;
  padding-bottom: 8px;
}
.barra-wrap { display: flex; flex-direction: column; align-items: center; gap: 4px; flex: 1; }
.barra {
  width: 100%; background: #2E5FA3;
  border-radius: 4px 4px 0 0;
  transition: height 0.3s ease;
  min-height: 4px;
}
.barra-dia { background: #1E7E50; }
.barra-label { font-size: 11px; color: #888; }
.barra-valor { font-size: 10px; color: #555; }
</style>