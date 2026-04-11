<template>
  <div>
    <h1>Lista de Almacenes</h1>

    <p v-if="cargando">Cargando almacenes...</p>

    <table v-else>
      <thead>
        <tr>
          <th>Nombre</th>
          <th>Dirección</th>
          <th>Ciudad</th>
          <th>Responsable</th>
          <th>Estado</th>
          <th>Acción</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="almacen in almacenes" :key="almacen.id">
          <td>{{ almacen.nombre }}</td>
          <td>{{ almacen.direccion }}</td>
          <td>{{ almacen.ciudad }}</td>
          <td>{{ almacen.responsable }}</td>
          <td>
            <span :class="almacen.estado === 'activo' ? 'activo' : 'inactivo'">
              {{ almacen.estado }}
            </span>
          </td>
          <td>
            <div style="display:flex; gap:6px; flex-wrap:wrap;">
              <button class="btn-ver" @click="verInventario(almacen)">👁️ Ver inventario</button>
              <button class="btn-dashboard" @click="verDashboard(almacen)">📊 Dashboard</button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Overlay inventario -->
    <div class="overlay" v-if="panelAbierto" @click.self="panelAbierto = false"></div>

    <!-- Panel inventario -->
    <div class="panel" :class="{ abierto: panelAbierto }">
      <div class="panel-header">
        <h2>📦 {{ almacenSeleccionado?.nombre }}</h2>
        <button class="cerrar" @click="panelAbierto = false">✕</button>
      </div>
      <div class="panel-body">
        <p v-if="cargandoInventario">Cargando inventario...</p>
        <p v-else-if="inventarioAgrupado.length === 0">Sin productos en este almacén.</p>
        <div v-else class="tabla-scroll">
          <table class="tabla-inventario">
            <thead>
              <tr>
                <th>Foto</th>
                <th>SKU</th>
                <th>Nombre</th>
                <th>Marca</th>
                <th>Precio</th>
                <th>Stock total</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in inventarioAgrupado" :key="item.id">
                <td>
                  <img v-if="item.foto_url" :src="item.foto_url" class="foto" />
                  <span v-else>Sin foto</span>
                </td>
                <td>{{ item.sku }}</td>
                <td>{{ item.nombre }}</td>
                <td>{{ item.marca }}</td>
                <td>${{ item.precio }}</td>
                <td>{{ item.stockTotal }}</td>
                <td>
                  <div style="display:flex; gap:6px; flex-wrap:wrap;">
                    <button class="btn-etiqueta" @click="verEtiquetas(item)">🏷️ Etiquetas</button>
                    <button class="btn-tallas" @click="verTallas(item)">👁️ Tallas</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Overlay tallas -->
    <div class="overlay" v-if="panelTallasAbierto" @click.self="panelTallasAbierto = false"></div>

    <!-- Panel tallas -->
    <div class="panel" :class="{ abierto: panelTallasAbierto }">
      <div class="panel-header">
        <h2>👁️ Tallas — {{ productoTallas?.nombre }}</h2>
        <button class="cerrar" @click="panelTallasAbierto = false">✕</button>
      </div>
      <div class="panel-body">
        <p v-if="cargandoTallas">Cargando...</p>
        <p v-else-if="tallasVista.length === 0">Sin tallas disponibles.</p>
        <table v-else>
          <thead>
            <tr>
              <th>Talla</th>
              <th>Género</th>
              <th>Unidades</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="t in tallasVista" :key="t.id">
              <td><span class="talla-badge">{{ t.talla }}</span></td>
              <td>{{ t.genero }}</td>
              <td>{{ t.unidades }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Overlay etiquetas -->
    <div class="overlay" v-if="panelEtiquetasAbierto" @click.self="panelEtiquetasAbierto = false"></div>

    <!-- Panel etiquetas -->
    <div class="panel" :class="{ abierto: panelEtiquetasAbierto }">
      <div class="panel-header">
        <h2>🏷️ Etiquetas — {{ productoEtiquetas?.nombre }}</h2>
        <button class="cerrar" @click="panelEtiquetasAbierto = false">✕</button>
      </div>
      <div class="panel-body">
        <p v-if="cargandoEtiquetas">Cargando etiquetas...</p>
        <p v-else-if="tallasEtiquetas.length === 0">Sin tallas registradas.</p>
        <div v-else>
          <button class="btn-imprimir" @click="imprimir">🖨️ Imprimir todas</button>
          <div class="etiquetas-wrap" id="etiquetas-print">
            <div class="etiqueta" v-for="(t, i) in tallasEtiquetas" :key="i">
              <p class="et-nombre">{{ productoEtiquetas?.nombre }}</p>
              <p class="et-sku">{{ productoEtiquetas?.sku }}</p>
              <span class="et-talla">{{ t.talla }}</span>
              <canvas :id="'qr-alm-' + i" class="qr-canvas"></canvas>
              <p class="et-codigo">{{ productoEtiquetas?.sku }}-T{{ t.talla }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Overlay dashboard -->
    <div class="overlay" v-if="panelDashboardAbierto" @click.self="panelDashboardAbierto = false"></div>

    <!-- Panel dashboard -->
    <div class="panel panel-wide" :class="{ abierto: panelDashboardAbierto }">
      <div class="panel-header">
        <h2>📊 Dashboard — {{ almacenDashboard?.nombre }}</h2>
        <button class="cerrar" @click="panelDashboardAbierto = false">✕</button>
      </div>
      <div class="panel-body" v-if="cargandoDashboard">
        <p>Cargando dashboard...</p>
      </div>
      <div class="panel-body" v-else-if="dashboardData">

        <!-- Filtros -->
        <div class="filtros-wrap">
          <button
            v-for="f in filtros" :key="f.label"
            class="filtro-btn"
            :class="{ activo: filtroDias === f.dias && filtroSoloAyer === f.soloAyer }"
            @click="filtroDias = f.dias; filtroSoloAyer = f.soloAyer; cargarDashboard()"
          >
            {{ f.label }}
          </button>
        </div>

        <!-- Financiero -->
        <div class="dash-seccion">
          <p class="dash-titulo">💰 Financiero</p>
          <div class="dash-cards">
            <div class="dash-card verde">
              <p class="dash-label">Ingresos del período</p>
              <p class="dash-valor">${{ formatNum(dashboardData.financiero.ventas_periodo) }}</p>
            </div>
            <div class="dash-card naranja-card">
              <p class="dash-label">Costo de ventas</p>
              <p class="dash-valor naranja">${{ formatNum(dashboardData.financiero.costo_ventas) }}</p>
            </div>
            <div class="dash-card azul-card">
              <p class="dash-label">Ganancia</p>
              <p class="dash-valor azul">${{ formatNum(dashboardData.financiero.ganancia) }}</p>
            </div>
            <div class="dash-card">
              <p class="dash-label">Margen</p>
              <p class="dash-valor">{{ dashboardData.financiero.margen }}%</p>
            </div>
            <div class="dash-card">
              <p class="dash-label">Total ventas</p>
              <p class="dash-valor">{{ dashboardData.financiero.total_ventas }}</p>
            </div>
            <div class="dash-card">
              <p class="dash-label">Ticket promedio</p>
              <p class="dash-valor">${{ formatNum(dashboardData.financiero.ticket_promedio) }}</p>
            </div>
            <div class="dash-card">
              <p class="dash-label">Método más usado</p>
              <p class="dash-valor">{{ dashboardData.financiero.metodo_top || 'Sin datos' }}</p>
            </div>
          </div>
        </div>

        <!-- Tendencias -->
        <div class="dash-seccion">
          <p class="dash-titulo">📈 Tendencias</p>
          <div class="dash-cards">
            <div class="dash-card">
              <p class="dash-label">Producto más vendido</p>
              <p class="dash-valor">{{ dashboardData.tendencias.producto_top || 'Sin datos' }}</p>
            </div>
            <div class="dash-card">
              <p class="dash-label">Talla top — Hombre</p>
              <p class="dash-valor">{{ dashboardData.tendencias.talla_top_hombre || 'Sin datos' }}</p>
            </div>
            <div class="dash-card">
              <p class="dash-label">Talla top — Mujer</p>
              <p class="dash-valor">{{ dashboardData.tendencias.talla_top_mujer || 'Sin datos' }}</p>
            </div>
          </div>
          <p class="dash-subtitulo">Ventas por mes</p>
          <div class="barras-container" v-if="dashboardData.tendencias.ventas_por_mes.length">
            <div class="barras">
              <div v-for="v in dashboardData.tendencias.ventas_por_mes" :key="v.mes" class="barra-wrap">
                <p class="barra-valor-top">${{ formatNum(v.total) }}</p>
                <p class="barra-porcentaje">{{ v.porcentaje }}%</p>
                <div class="barra" :style="{ height: alturaBarra(v.total, maxMes) + 'px' }"></div>
                <p class="barra-label">{{ nombreMes(v.mes) }}</p>
              </div>
            </div>
          </div>
          <p v-else class="sin-datos">Sin ventas en este período</p>
          <p class="dash-subtitulo">Ventas por día de la semana</p>
          <div class="barras-container" v-if="dashboardData.tendencias.ventas_por_dia.length">
            <div class="barras">
              <div v-for="v in dashboardData.tendencias.ventas_por_dia" :key="v.dia" class="barra-wrap">
                <p class="barra-valor-top">{{ v.total }}</p>
                <p class="barra-porcentaje">{{ v.porcentaje }}%</p>
                <div class="barra barra-dia" :style="{ height: alturaBarra(v.total, maxDia) + 'px' }"></div>
                <p class="barra-label">{{ nombreDia(v.dia) }}</p>
              </div>
            </div>
          </div>
          <p v-else class="sin-datos">Sin ventas en este período</p>
        </div>

        <!-- Inventario + Matriz -->
        <div class="dash-seccion">
          <p class="dash-titulo">📦 Inventario</p>
          <div class="dash-cards">
            <div class="dash-card">
              <p class="dash-label">Total productos</p>
              <p class="dash-valor">{{ dashboardData.inventario.total_productos }}</p>
            </div>
            <div class="dash-card alerta">
              <p class="dash-label">⚠️ Stock bajo</p>
              <p class="dash-valor naranja">{{ dashboardData.inventario.stock_bajo }}</p>
              <p class="dash-sub">menos de 5 unidades</p>
            </div>
            <div class="dash-card">
              <p class="dash-label">Costo del inventario</p>
              <p class="dash-valor">${{ formatNum(dashboardData.inventario.costo_inventario) }}</p>
            </div>
          </div>

          <!-- Matriz scatter resumida -->
          <p class="dash-subtitulo">🎯 Matriz de reposición — Top 5 críticos</p>
          <div class="matriz-leyenda">
            <span class="ml urgente">🔴 Reponer urgente</span>
            <span class="ml vigilar">🟡 Vigilar</span>
            <span class="ml exceso">🔵 Exceso stock</span>
            <span class="ml revisar">⚫ Revisar</span>
            <span class="ml baja">⚠️ Baja rotación</span>
          </div>

          <div v-if="dashboardData.inventario.matriz && dashboardData.inventario.matriz.length">
            <div class="matriz-tabla">
              <table>
                <thead>
                  <tr>
                    <th>Producto</th>
                    <th>Stock</th>
                    <th>Ventas 30d</th>
                    <th>DOH</th>
                    <th>Estado</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="p in top5Matriz" :key="p.sku"
                    :class="{ 'fila-baja-rotacion': p.baja_rotacion }"
                  >
                    <td>{{ p.nombre }}</td>
                    <td>{{ p.stock }}</td>
                    <td>{{ p.ventas_30 }}</td>
                    <td>
                      <span v-if="p.baja_rotacion" class="badge-baja-rotacion">⚠️ Baja rotación</span>
                      <span v-else-if="p.doh <= 7" class="badge-doh-critico">🔴 {{ p.doh }}d</span>
                      <span v-else-if="p.doh <= 15" class="badge-doh-alerta">🟡 {{ p.doh }}d</span>
                      <span v-else class="badge-doh-ok">🟢 {{ p.doh }}d</span>
                    </td>
                    <td>
                      <span :class="'badge-' + clasificarProducto(p)">
                        {{ etiquetaProducto(p) }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
              <button class="btn-ver-detalle" @click="panelMatrizAbierto = true">
                📋 Ver detalle completo ({{ dashboardData.inventario.matriz.length }} referencias)
              </button>
            </div>
          </div>
          <p v-else class="sin-datos">Sin datos suficientes para la matriz</p>
        </div>

        <!-- Clientes -->
        <div class="dash-seccion">
          <p class="dash-titulo">👥 Clientes</p>
          <div class="dash-cards">
            <div class="dash-card">
              <p class="dash-label">Total clientes</p>
              <p class="dash-valor">{{ dashboardData.clientes.total_clientes }}</p>
            </div>
            <div class="dash-card">
              <p class="dash-label">Nuevos este mes</p>
              <p class="dash-valor">{{ dashboardData.clientes.clientes_nuevos_mes }}</p>
            </div>
            <div class="dash-card">
              <p class="dash-label">Género más frecuente</p>
              <p class="dash-valor">{{ dashboardData.clientes.genero_top || 'Sin datos' }}</p>
            </div>
            <div class="dash-card">
              <p class="dash-label">Clientes recurrentes</p>
              <p class="dash-valor">{{ dashboardData.clientes.clientes_recurrentes }}</p>
            </div>
            <div class="dash-card">
              <p class="dash-label">Promedio de compras</p>
              <p class="dash-valor">{{ dashboardData.clientes.promedio_compras }}x</p>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- Overlay matriz detalle -->
    <div class="overlay" v-if="panelMatrizAbierto" @click.self="panelMatrizAbierto = false"></div>

    <!-- Panel matriz detalle completo -->
    <div class="panel panel-wide" :class="{ abierto: panelMatrizAbierto }">
      <div class="panel-header">
        <h2>🎯 Matriz de reposición — {{ almacenDashboard?.nombre }}</h2>
        <button class="cerrar" @click="panelMatrizAbierto = false">✕</button>
      </div>
      <div class="panel-body" v-if="dashboardData">

        <div class="matriz-leyenda">
          <span class="ml urgente">🔴 Reponer urgente</span>
          <span class="ml vigilar">🟡 Vigilar</span>
          <span class="ml exceso">🔵 Exceso stock</span>
          <span class="ml revisar">⚫ Revisar</span>
          <span class="ml baja">⚠️ Baja rotación</span>
        </div>

        <!-- Scatter completo -->
        <div class="scatter-wrap">
          <svg :width="scatterW" :height="scatterH" class="scatter-svg">
            <rect :x="pad" :y="pad" :width="(scatterW-pad*2)/2" :height="(scatterH-pad*2)/2" fill="rgba(55,138,221,0.08)"/>
            <rect :x="pad+(scatterW-pad*2)/2" :y="pad" :width="(scatterW-pad*2)/2" :height="(scatterH-pad*2)/2" fill="rgba(239,159,39,0.08)"/>
            <rect :x="pad" :y="pad+(scatterH-pad*2)/2" :width="(scatterW-pad*2)/2" :height="(scatterH-pad*2)/2" fill="rgba(136,135,128,0.08)"/>
            <rect :x="pad+(scatterW-pad*2)/2" :y="pad+(scatterH-pad*2)/2" :width="(scatterW-pad*2)/2" :height="(scatterH-pad*2)/2" fill="rgba(226,75,74,0.08)"/>
            <text :x="pad+8" :y="pad+16" class="q-label" fill="#185FA5">EXCESO DE STOCK</text>
            <text :x="pad+(scatterW-pad*2)/2+8" :y="pad+16" class="q-label" fill="#856404">VIGILAR</text>
            <text :x="pad+8" :y="pad+(scatterH-pad*2)/2+16" class="q-label" fill="#555">REVISAR / LIQUIDAR</text>
            <text :x="pad+(scatterW-pad*2)/2+8" :y="pad+(scatterH-pad*2)/2+16" class="q-label" fill="#c0392b">REPONER URGENTE</text>
            <line :x1="pad+(scatterW-pad*2)/2" :y1="pad" :x2="pad+(scatterW-pad*2)/2" :y2="scatterH-pad" stroke="#bbb" stroke-width="1" stroke-dasharray="5,4"/>
            <line :x1="pad" :y1="pad+(scatterH-pad*2)/2" :x2="scatterW-pad" :y2="pad+(scatterH-pad*2)/2" stroke="#bbb" stroke-width="1" stroke-dasharray="5,4"/>
            <line :x1="pad" :y1="pad" :x2="pad" :y2="scatterH-pad" stroke="#ccc" stroke-width="1"/>
            <line :x1="pad" :y1="scatterH-pad" :x2="scatterW-pad" :y2="scatterH-pad" stroke="#ccc" stroke-width="1"/>
            <g v-for="(t,i) in ventasTicks" :key="'x2'+i">
              <line :x1="pad + (t/maxVentas)*(scatterW-pad*2)" :y1="scatterH-pad" :x2="pad + (t/maxVentas)*(scatterW-pad*2)" :y2="scatterH-pad+4" stroke="#ccc" stroke-width="1"/>
              <text :x="pad + (t/maxVentas)*(scatterW-pad*2)" :y="scatterH-pad+14" text-anchor="middle" font-size="10" fill="#888">{{ t }}</text>
            </g>
            <g v-for="(t,i) in stockTicks" :key="'y2'+i">
              <line :x1="pad-4" :y1="scatterH-pad - (t/maxStock)*(scatterH-pad*2)" :x2="pad" :y2="scatterH-pad - (t/maxStock)*(scatterH-pad*2)" stroke="#ccc" stroke-width="1"/>
              <text :x="pad-6" :y="scatterH-pad - (t/maxStock)*(scatterH-pad*2) + 4" text-anchor="end" font-size="10" fill="#888">{{ t }}</text>
            </g>
            <text :x="scatterW/2" :y="scatterH-2" text-anchor="middle" font-size="11" fill="#888">Ventas mensuales (unidades)</text>
            <text :x="12" :y="scatterH/2" text-anchor="middle" font-size="11" fill="#888" :transform="`rotate(-90, 12, ${scatterH/2})`">Stock actual (unidades)</text>
            <g v-for="p in dashboardData.inventario.matriz" :key="'dot-'+p.sku">
              <circle
                :cx="pad + (p.ventas/maxVentas)*(scatterW-pad*2)"
                :cy="scatterH-pad - (p.stock/maxStock)*(scatterH-pad*2)"
                r="7" :fill="colorPunto(p)" fill-opacity="0.85"
                stroke="white" stroke-width="1.5" class="scatter-punto"
              >
                <title>{{ p.nombre }} | Stock: {{ p.stock }} | Ventas: {{ p.ventas }} | DOH: {{ p.doh ? p.doh + ' días' : 'Baja rotación' }}</title>
              </circle>
            </g>
          </svg>
        </div>

        <!-- Tabla completa ordenada -->
        <div class="matriz-tabla">
          <table>
            <thead>
              <tr>
                <th>Producto</th>
                <th>Stock</th>
                <th>Ventas 30d</th>
                <th>DOH</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="p in matrizOrdenada" :key="'det-'+p.sku"
                :class="{ 'fila-baja-rotacion': p.baja_rotacion }"
              >
                <td>{{ p.nombre }}</td>
                <td>{{ p.stock }}</td>
                <td>{{ p.ventas_30 }}</td>
                <td>
                  <span v-if="p.baja_rotacion" class="badge-baja-rotacion">⚠️ Baja rotación</span>
                  <span v-else-if="p.doh <= 7" class="badge-doh-critico">🔴 {{ p.doh }}d</span>
                  <span v-else-if="p.doh <= 15" class="badge-doh-alerta">🟡 {{ p.doh }}d</span>
                  <span v-else class="badge-doh-ok">🟢 {{ p.doh }}d</span>
                </td>
                <td>
                  <span :class="'badge-' + clasificarProducto(p)">
                    {{ etiquetaProducto(p) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import axios from 'axios'

const API = import.meta.env.VITE_API_URL

export default {
  data() {
    return {
      almacenes: [],
      cargando: true,
      panelAbierto: false,
      almacenSeleccionado: null,
      inventario: [],
      cargandoInventario: false,
      panelTallasAbierto: false,
      productoTallas: null,
      tallasVista: [],
      cargandoTallas: false,
      panelEtiquetasAbierto: false,
      productoEtiquetas: null,
      tallasEtiquetas: [],
      cargandoEtiquetas: false,
      panelDashboardAbierto: false,
      almacenDashboard: null,
      dashboardData: null,
      cargandoDashboard: false,
      panelMatrizAbierto: false,
      filtroDias: 30,
      filtroSoloAyer: false,
      filtros: [
        { label: 'Hoy',     dias: 1,   soloAyer: false },
        { label: 'Ayer',    dias: 1,   soloAyer: true  },
        { label: '7 días',  dias: 7,   soloAyer: false },
        { label: '30 días', dias: 30,  soloAyer: false },
        { label: '6 meses', dias: 180, soloAyer: false },
        { label: '1 año',   dias: 365, soloAyer: false },
      ],
      scatterW: 600,
      scatterH: 400,
      pad: 50,
    }
  },
  computed: {
    inventarioAgrupado() {
      const mapa = {}
      this.inventario.forEach(item => {
        if (!mapa[item.id]) mapa[item.id] = { ...item, stockTotal: 0 }
        mapa[item.id].stockTotal += item.stock
      })
      return Object.values(mapa)
    },
    maxMes() {
      if (!this.dashboardData || !this.dashboardData.tendencias.ventas_por_mes.length) return 1
      return Math.max(...this.dashboardData.tendencias.ventas_por_mes.map(v => v.total), 1)
    },
    maxDia() {
      if (!this.dashboardData || !this.dashboardData.tendencias.ventas_por_dia.length) return 1
      return Math.max(...this.dashboardData.tendencias.ventas_por_dia.map(v => v.total), 1)
    },
    maxVentas() {
      if (!this.dashboardData?.inventario?.matriz?.length) return 10
      return Math.max(...this.dashboardData.inventario.matriz.map(p => p.ventas), 1) * 1.2
    },
    maxStock() {
      if (!this.dashboardData?.inventario?.matriz?.length) return 10
      return Math.max(...this.dashboardData.inventario.matriz.map(p => p.stock), 1) * 1.2
    },
    ventasTicks() {
      const max = this.maxVentas
      const step = Math.max(Math.ceil(max / 5 / 5) * 5, 1)
      const ticks = []
      for (let i = 0; i <= max; i += step) ticks.push(Math.round(i))
      return ticks
    },
    stockTicks() {
      const max = this.maxStock
      const step = Math.max(Math.ceil(max / 5 / 5) * 5, 1)
      const ticks = []
      for (let i = 0; i <= max; i += step) ticks.push(Math.round(i))
      return ticks
    },
    top5Matriz() {
      if (!this.dashboardData?.inventario?.matriz?.length) return []
      const orden = { urgente: 0, baja: 1, vigilar: 2, exceso: 3, revisar: 4 }
      return [...this.dashboardData.inventario.matriz]
        .sort((a, b) => {
          const ca = a.baja_rotacion ? 'baja' : this.clasificarProducto(a)
          const cb = b.baja_rotacion ? 'baja' : this.clasificarProducto(b)
          return (orden[ca] ?? 5) - (orden[cb] ?? 5)
        })
        .slice(0, 5)
    },
    matrizOrdenada() {
      if (!this.dashboardData?.inventario?.matriz?.length) return []
      const orden = { urgente: 0, baja: 1, vigilar: 2, exceso: 3, revisar: 4 }
      return [...this.dashboardData.inventario.matriz].sort((a, b) => {
        const ca = a.baja_rotacion ? 'baja' : this.clasificarProducto(a)
        const cb = b.baja_rotacion ? 'baja' : this.clasificarProducto(b)
        return (orden[ca] ?? 5) - (orden[cb] ?? 5)
      })
    },
  },
  methods: {
    clasificarProducto(p) {
      const umbralV = (this.maxVentas / 1.2) * 0.5
      const umbralS = (this.maxStock / 1.2) * 0.5
      if (p.ventas >= umbralV && p.stock < umbralS) return 'urgente'
      if (p.ventas >= umbralV && p.stock >= umbralS) return 'vigilar'
      if (p.ventas < umbralV && p.stock >= umbralS) return 'exceso'
      return 'revisar'
    },
    etiquetaProducto(p) {
      const c = this.clasificarProducto(p)
      return {
        urgente: '🔴 Reponer urgente',
        vigilar: '🟡 Vigilar',
        exceso:  '🔵 Exceso stock',
        revisar: '⚫ Revisar'
      }[c]
    },
    colorPunto(p) {
      if (p.baja_rotacion) return '#F39C12'
      const c = this.clasificarProducto(p)
      return { urgente: '#E24B4A', vigilar: '#EF9F27', exceso: '#378ADD', revisar: '#888780' }[c]
    },
    async verInventario(almacen) {
      this.almacenSeleccionado = almacen
      this.panelAbierto = true
      this.cargandoInventario = true
      try {
        const { data } = await axios.get(`${API}/almacenes/${almacen.id}/inventario`)
        this.inventario = data
      } catch (error) {
        console.error('Error cargando inventario', error)
      }
      this.cargandoInventario = false
    },
    async verTallas(item) {
      this.productoTallas = item
      this.panelTallasAbierto = true
      this.cargandoTallas = true
      try {
        const { data } = await axios.get(`${API}/almacenes/${this.almacenSeleccionado.id}/productos/${item.id}/tallas`)
        this.tallasVista = data
      } catch (error) {
        console.error('Error', error)
      }
      this.cargandoTallas = false
    },
    async verEtiquetas(item) {
      this.productoEtiquetas = item
      this.panelEtiquetasAbierto = true
      this.cargandoEtiquetas = true
      try {
        const { data } = await axios.get(`${API}/almacenes/${this.almacenSeleccionado.id}/productos/${item.id}/tallas`)
        this.tallasEtiquetas = data
        this.$nextTick(() => { this.generarQRs() })
      } catch (error) {
        console.error('Error', error)
      }
      this.cargandoEtiquetas = false
    },
    async verDashboard(almacen) {
      this.almacenDashboard = almacen
      this.panelDashboardAbierto = true
      this.filtroDias = 30
      this.filtroSoloAyer = false
      await this.cargarDashboard()
    },
    async cargarDashboard() {
      this.cargandoDashboard = true
      try {
        const params = this.filtroSoloAyer ? `dias=1&solo_ayer=true` : `dias=${this.filtroDias}`
        const { data } = await axios.get(`${API}/dashboard/${this.almacenDashboard.id}?${params}`)
        this.dashboardData = data
      } catch (error) {
        console.error('Error cargando dashboard', error)
      }
      this.cargandoDashboard = false
    },
    generarQRs() {
      import('qrcode').then(QRCode => {
        this.tallasEtiquetas.forEach((t, i) => {
          const canvas = document.getElementById(`qr-alm-${i}`)
          if (canvas) {
            const texto = `${this.productoEtiquetas.sku} | ${this.productoEtiquetas.nombre} | Talla: ${t.talla}`
            QRCode.toCanvas(canvas, texto, { width: 80 })
          }
        })
      })
    },
    async imprimir() {
      const QRCode = await import('qrcode')
      const etiquetas = await Promise.all(this.tallasEtiquetas.map(async (t) => {
        const texto = `${this.productoEtiquetas.sku} | ${this.productoEtiquetas.nombre} | Talla: ${t.talla}`
        const qrBase64 = await QRCode.toDataURL(texto, { width: 100, margin: 1 })
        return `
          <div class="etiqueta">
            <p class="et-nombre">${this.productoEtiquetas.nombre}</p>
            <p class="et-sku">${this.productoEtiquetas.sku}</p>
            <span class="et-talla">${t.talla}</span>
            <img src="${qrBase64}" width="80" height="80" />
            <p class="et-codigo">${this.productoEtiquetas.sku}-T${t.talla}</p>
          </div>
        `
      }))
      const html = `
        <html><head><title>Etiquetas</title>
        <style>
          body { font-family: Arial; margin: 0; padding: 16px; }
          .etiquetas-wrap { display: flex; flex-wrap: wrap; gap: 16px; }
          .etiqueta { border: 1px solid #ccc; border-radius: 8px; padding: 12px; width: 150px; text-align: center; display: flex; flex-direction: column; align-items: center; gap: 6px; page-break-inside: avoid; }
          .et-nombre { font-size: 12px; font-weight: bold; margin: 0; }
          .et-sku { font-size: 10px; color: #666; margin: 0; }
          .et-talla { font-size: 18px; font-weight: bold; color: #185FA5; background: #E6F1FB; padding: 2px 12px; border-radius: 20px; display: inline-block; }
          .et-codigo { font-size: 9px; color: #999; margin: 0; }
          @media print { body { margin: 0; } }
        </style></head>
        <body onload="window.print()">
          <div class="etiquetas-wrap">${etiquetas.join('')}</div>
        </body></html>
      `
      const blob = new Blob([html], { type: 'text/html' })
      const url = URL.createObjectURL(blob)
      const ventana = window.open(url, '_blank')
      if (!ventana) alert('Por favor permite las ventanas emergentes para imprimir')
    },
    alturaBarra(valor, max) { return Math.max((valor / max) * 100, 4) },
    formatNum(n) { return Number(n).toLocaleString('es-CO') },
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
      const { data } = await axios.get(`${API}/almacenes`)
      this.almacenes = data
    } catch (error) {
      console.error('Error cargando almacenes', error)
    }
    this.cargando = false
  }
}
</script>

<style scoped>
h1 { margin-bottom: 24px; color: #1B3A6B; }
table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
thead { background: #1B3A6B; color: white; }
th, td { padding: 12px 16px; text-align: left; font-size: 14px; }
tbody tr:nth-child(even) { background: #F2F4F7; }
tbody tr:hover { background: #D6E4F7; }
.activo { background: #d4edda; color: #1E7E50; padding: 4px 10px; border-radius: 12px; font-size: 13px; }
.inactivo { background: #f8d7da; color: #c0392b; padding: 4px 10px; border-radius: 12px; font-size: 13px; }
.btn-ver { padding: 6px 12px; background: #2E5FA3; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; }
.btn-dashboard { padding: 6px 12px; background: #1B3A6B; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; }
.btn-dashboard:hover { background: #2E5FA3; }
.btn-etiqueta { padding: 5px 10px; background: #1E7E50; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 12px; }
.btn-tallas { padding: 5px 10px; background: #8C9BAB; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 12px; }
.overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.3); z-index: 100; }
.panel { position: fixed; top: 0; right: -700px; width: 700px; height: 100%; background: white; box-shadow: -4px 0 20px rgba(0,0,0,0.15); z-index: 101; transition: right 0.3s ease; display: flex; flex-direction: column; }
.panel-wide { width: 850px; right: -850px; }
.panel.abierto { right: 0; }
.panel-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; background: #1B3A6B; color: white; }
.panel-header h2 { margin: 0; font-size: 18px; color: white; }
.cerrar { background: none; border: none; color: white; font-size: 20px; cursor: pointer; }
.panel-body { padding: 24px; overflow-y: auto; flex: 1; }
.tabla-scroll { overflow-x: auto; }
.tabla-inventario { margin-top: 0; min-width: 600px; }
.foto { width: 40px; height: 40px; object-fit: cover; border-radius: 4px; }
.talla-badge { background: #D6E4F7; color: #1B3A6B; padding: 2px 10px; border-radius: 20px; font-weight: 500; font-size: 14px; }
.btn-imprimir { padding: 8px 16px; background: #1B3A6B; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; margin-bottom: 16px; }
.etiquetas-wrap { display: flex; flex-wrap: wrap; gap: 16px; }
.etiqueta { border: 1px solid #ccc; border-radius: 8px; padding: 12px; width: 150px; text-align: center; display: flex; flex-direction: column; align-items: center; gap: 6px; }
.et-nombre { font-size: 12px; font-weight: 500; color: #333; }
.et-sku { font-size: 10px; color: #888; }
.et-talla { font-size: 18px; font-weight: 500; color: #185FA5; background: #E6F1FB; padding: 2px 12px; border-radius: 20px; }
.qr-canvas { width: 80px !important; height: 80px !important; }
.et-codigo { font-size: 9px; color: #999; }
.filtros-wrap { display: flex; gap: 8px; margin-bottom: 20px; flex-wrap: wrap; }
.filtro-btn { padding: 6px 14px; border: 1px solid #ccc; background: white; border-radius: 20px; cursor: pointer; font-size: 13px; color: #555; }
.filtro-btn.activo { background: #1B3A6B; color: white; border-color: #1B3A6B; }
.dash-seccion { margin-bottom: 24px; padding-bottom: 24px; border-bottom: 1px solid #eee; }
.dash-titulo { font-size: 15px; font-weight: 600; color: #1B3A6B; margin-bottom: 12px; }
.dash-subtitulo { font-size: 13px; color: #555; margin: 16px 0 8px; font-weight: 500; }
.dash-cards { display: flex; flex-wrap: wrap; gap: 12px; }
.dash-card { background: #F2F4F7; border-radius: 8px; padding: 12px 16px; min-width: 120px; flex: 1; }
.dash-card.verde { background: #d4edda; }
.dash-card.alerta { background: #fff3cd; }
.dash-card.naranja-card { background: #fff3cd; }
.dash-card.azul-card { background: #D6E4F7; }
.dash-label { font-size: 11px; color: #888; margin-bottom: 6px; }
.dash-valor { font-size: 20px; font-weight: 600; color: #1B3A6B; }
.dash-valor.naranja { color: #D35400; }
.dash-valor.azul { color: #2E5FA3; }
.dash-sub { font-size: 10px; color: #888; margin-top: 4px; }
.barras-container { overflow-x: auto; }
.barras { display: flex; align-items: flex-end; gap: 8px; height: 160px; border-bottom: 2px solid #eee; padding-bottom: 4px; min-width: 300px; }
.barra-wrap { display: flex; flex-direction: column; align-items: center; gap: 2px; flex: 1; min-width: 40px; }
.barra { width: 100%; background: #2E5FA3; border-radius: 4px 4px 0 0; min-height: 4px; }
.barra-dia { background: #1E7E50; }
.barra-label { font-size: 10px; color: #888; }
.barra-valor-top { font-size: 9px; color: #555; text-align: center; font-weight: 500; }
.barra-porcentaje { font-size: 9px; color: #888; text-align: center; }
.sin-datos { font-size: 13px; color: #888; margin-top: 8px; }
.matriz-leyenda { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }
.ml { font-size: 11px; padding: 3px 10px; border-radius: 12px; font-weight: 500; }
.ml.urgente { background: #fde8e8; color: #c0392b; }
.ml.vigilar  { background: #fff3cd; color: #856404; }
.ml.exceso   { background: #D6E4F7; color: #1B3A6B; }
.ml.revisar  { background: #F2F4F7; color: #555; }
.ml.baja     { background: #fff3cd; color: #856404; }
.scatter-wrap { overflow-x: auto; margin-bottom: 16px; background: white; border-radius: 8px; padding: 8px; border: 1px solid #eee; }
.scatter-svg { display: block; min-width: 400px; }
.scatter-punto { cursor: pointer; }
.q-label { font-size: 10px; font-weight: 600; letter-spacing: 0.3px; }
.matriz-tabla { overflow-x: auto; margin-top: 12px; }
.fila-baja-rotacion { background: #fffbf0 !important; }
.btn-ver-detalle { width: 100%; margin-top: 12px; padding: 10px; background: #F2F4F7; color: #1B3A6B; border: 1px solid #D6E4F7; border-radius: 8px; cursor: pointer; font-size: 13px; font-weight: 500; }
.btn-ver-detalle:hover { background: #D6E4F7; }
.badge-urgente { background: #fde8e8; color: #c0392b; padding: 2px 8px; border-radius: 10px; font-size: 11px; white-space: nowrap; }
.badge-vigilar { background: #fff3cd; color: #856404; padding: 2px 8px; border-radius: 10px; font-size: 11px; white-space: nowrap; }
.badge-exceso  { background: #D6E4F7; color: #1B3A6B; padding: 2px 8px; border-radius: 10px; font-size: 11px; white-space: nowrap; }
.badge-revisar { background: #F2F4F7; color: #555; padding: 2px 8px; border-radius: 10px; font-size: 11px; white-space: nowrap; }
.badge-baja-rotacion { background: #fff3cd; color: #856404; padding: 2px 8px; border-radius: 10px; font-size: 11px; white-space: nowrap; }
.badge-doh-critico { background: #fde8e8; color: #c0392b; padding: 2px 8px; border-radius: 10px; font-size: 11px; white-space: nowrap; }
.badge-doh-alerta  { background: #fff3cd; color: #856404; padding: 2px 8px; border-radius: 10px; font-size: 11px; white-space: nowrap; }
.badge-doh-ok      { background: #d4edda; color: #1E7E50; padding: 2px 8px; border-radius: 10px; font-size: 11px; white-space: nowrap; }

@media (max-width: 900px) {
  .panel-wide { width: 100vw; right: -100vw; }
}
@media (max-width: 600px) {
  .panel { width: 100vw; right: -100vw; }
  .dash-cards { flex-direction: column; }
  .dash-card { min-width: 100%; }
  .barras { height: 100px; }
  .barra-valor-top { font-size: 7px; }
  .barra-porcentaje { font-size: 7px; }
  .filtros-wrap { gap: 4px; }
  .filtro-btn { padding: 5px 8px; font-size: 11px; }
  .dash-titulo { font-size: 14px; }
  .dash-valor { font-size: 16px; }
  th, td { padding: 8px 10px; font-size: 12px; }
}
</style>