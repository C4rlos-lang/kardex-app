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

          <!-- Matriz de reposición -->
          <p class="dash-subtitulo">🎯 Matriz de reposición</p>
          <div class="matriz-leyenda">
            <span class="ml urgente">🔴 Reponer urgente</span>
            <span class="ml vigilar">🟡 Vigilar</span>
            <span class="ml exceso">🔵 Exceso stock</span>
            <span class="ml revisar">⚪ Revisar</span>
          </div>

          <div v-if="dashboardData.inventario.matriz && dashboardData.inventario.matriz.length">
            <!-- Puntos visuales -->
            <div class="matriz-ejes">
              <span class="eje-y">↑ Ventas</span>
              <div class="matriz-grid">
                <div
                  v-for="p in dashboardData.inventario.matriz"
                  :key="p.sku"
                  class="matriz-punto"
                  :class="clasificarProducto(p)"
                  :title="`${p.nombre} | Stock: ${p.stock} | Ventas: ${p.ventas}`"
                >
                  <div class="punto-dot"></div>
                  <p class="punto-label">{{ p.nombre.length > 10 ? p.nombre.substring(0,10)+'...' : p.nombre }}</p>
                </div>
              </div>
              <span class="eje-x">Stock →</span>
            </div>

            <!-- Tabla detalle -->
            <div class="matriz-tabla">
              <table>
                <thead>
                  <tr>
                    <th>Producto</th>
                    <th>Stock</th>
                    <th>Ventas</th>
                    <th>Estado</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="p in dashboardData.inventario.matriz" :key="p.sku">
                    <td>{{ p.nombre }}</td>
                    <td>{{ p.stock }}</td>
                    <td>{{ p.ventas }}</td>
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
      filtroDias: 30,
      filtroSoloAyer: false,
      filtros: [
        { label: 'Hoy',     dias: 1,   soloAyer: false },
        { label: 'Ayer',    dias: 1,   soloAyer: true  },
        { label: '7 días',  dias: 7,   soloAyer: false },
        { label: '30 días', dias: 30,  soloAyer: false },
        { label: '6 meses', dias: 180, soloAyer: false },
        { label: '1 año',   dias: 365, soloAyer: false },
      ]
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
    }
  },
  methods: {
    clasificarProducto(p) {
      const matriz = this.dashboardData.inventario.matriz
      const maxV = Math.max(...matriz.map(x => x.ventas), 1)
      const maxS = Math.max(...matriz.map(x => x.stock), 1)
      const umbralV = maxV * 0.5
      const umbralS = maxS * 0.5
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
        revisar: '⚪ Revisar'
      }[c]
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
        const { data } = await axios.get(
          `${API}/almacenes/${this.almacenSeleccionado.id}/productos/${item.id}/tallas`
        )
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
        const { data } = await axios.get(
          `${API}/almacenes/${this.almacenSeleccionado.id}/productos/${item.id}/tallas`
        )
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
        const params = this.filtroSoloAyer
          ? `dias=1&solo_ayer=true`
          : `dias=${this.filtroDias}`
        const { data } = await axios.get(
          `${API}/dashboard/${this.almacenDashboard.id}?${params}`
        )
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
    alturaBarra(valor, max) {
      return Math.max((valor / max) * 100, 4)
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
table {
  width: 100%; border-collapse: collapse;
  background: white; border-radius: 8px;
  overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
thead { background: #1B3A6B; color: white; }
th, td { padding: 12px 16px; text-align: left; font-size: 14px; }
tbody tr:nth-child(even) { background: #F2F4F7; }
tbody tr:hover { background: #D6E4F7; }
.activo {
  background: #d4edda; color: #1E7E50;
  padding: 4px 10px; border-radius: 12px; font-size: 13px;
}
.inactivo {
  background: #f8d7da; color: #c0392b;
  padding: 4px 10px; border-radius: 12px; font-size: 13px;
}
.btn-ver {
  padding: 6px 12px; background: #2E5FA3;
  color: white; border: none;
  border-radius: 6px; cursor: pointer; font-size: 13px;
}
.btn-dashboard {
  padding: 6px 12px; background: #1B3A6B;
  color: white; border: none;
  border-radius: 6px; cursor: pointer; font-size: 13px;
}
.btn-dashboard:hover { background: #2E5FA3; }
.btn-etiqueta {
  padding: 5px 10px; background: #1E7E50;
  color: white; border: none;
  border-radius: 6px; cursor: pointer; font-size: 12px;
}
.btn-tallas {
  padding: 5px 10px; background: #8C9BAB;
  color: white; border: none;
  border-radius: 6px; cursor: pointer; font-size: 12px;
}
.overlay {
  position: fixed; top: 0; left: 0;
  width: 100%; height: 100%;
  background: rgba(0,0,0,0.3); z-index: 100;
}
.panel {
  position: fixed; top: 0; right: -700px;
  width: 700px; height: 100%;
  background: white;
  box-shadow: -4px 0 20px rgba(0,0,0,0.15);
  z-index: 101; transition: right 0.3s ease;
  display: flex; flex-direction: column;
}
.panel-wide { width: 850px; right: -850px; }
.panel.abierto { right: 0; }
.panel-header {
  display: flex; justify-content: space-between;
  align-items: center; padding: 20px 24px;
  background: #1B3A6B; color: white;
}
.panel-header h2 { margin: 0; font-size: 18px; color: white; }
.cerrar {
  background: none; border: none;
  color: white; font-size: 20px; cursor: pointer;
}
.panel-body { padding: 24px; overflow-y: auto; flex: 1; }
.tabla-scroll { overflow-x: auto; }
.tabla-inventario { margin-top: 0; min-width: 600px; }
.foto { width: 40px; height: 40px; object-fit: cover; border-radius: 4px; }
.talla-badge {
  background: #D6E4F7; color: #1B3A6B;
  padding: 2px 10px; border-radius: 20px;
  font-weight: 500; font-size: 14px;
}
.btn-imprimir {
  padding: 8px 16px; background: #1B3A6B;
  color: white; border: none;
  border-radius: 6px; cursor: pointer;
  font-size: 14px; margin-bottom: 16px;
}
.etiquetas-wrap { display: flex; flex-wrap: wrap; gap: 16px; }
.etiqueta {
  border: 1px solid #ccc; border-radius: 8px;
  padding: 12px; width: 150px; text-align: center;
  display: flex; flex-direction: column;
  align-items: center; gap: 6px;
}
.et-nombre { font-size: 12px; font-weight: 500; color: #333; }
.et-sku { font-size: 10px; color: #888; }
.et-talla {
  font-size: 18px; font-weight: 500;
  color: #185FA5; background: #E6F1FB;
  padding: 2px 12px; border-radius: 20px;
}
.qr-canvas { width: 80px !important; height: 80px !important; }
.et-codigo { font-size: 9px; color: #999; }
.filtros-wrap {
  display: flex; gap: 8px;
  margin-bottom: 20px; flex-wrap: wrap;
}
.filtro-btn {
  padding: 6px 14px; border: 1px solid #ccc;
  background: white; border-radius: 20px;
  cursor: pointer; font-size: 13px; color: #555;
}
.filtro-btn.activo {
  background: #1B3A6B; color: white; border-color: #1B3A6B;
}
.dash-seccion {
  margin-bottom: 24px; padding-bottom: 24px;
  border-bottom: 1px solid #eee;
}
.dash-titulo { font-size: 15px; font-weight: 600; color: #1B3A6B; margin-bottom: 12px; }
.dash-subtitulo { font-size: 13px; color: #555; margin: 16px 0 8px; font-weight: 500; }
.dash-cards { display: flex; flex-wrap: wrap; gap: 12px; }
.dash-card {
  background: #F2F4F7; border-radius: 8px;
  padding: 12px 16px; min-width: 120px; flex: 1;
}
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
.barras {
  display: flex; align-items: flex-end;
  gap: 8px; height: 160px;
  border-bottom: 2px solid #eee;
  padding-bottom: 4px; min-width: 300px;
}
.barra-wrap { display: flex; flex-direction: column; align-items: center; gap: 2px; flex: 1; min-width: 40px; }
.barra {
  width: 100%; background: #2E5FA3;
  border-radius: 4px 4px 0 0; min-height: 4px;
}
.barra-dia { background: #1E7E50; }
.barra-label { font-size: 10px; color: #888; }
.barra-valor-top { font-size: 9px; color: #555; text-align: center; font-weight: 500; }
.barra-porcentaje { font-size: 9px; color: #888; text-align: center; }
.sin-datos { font-size: 13px; color: #888; margin-top: 8px; }

/* Matriz de reposición */
.matriz-leyenda {
  display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px;
}
.ml {
  font-size: 11px; padding: 3px 10px;
  border-radius: 12px; font-weight: 500;
}
.ml.urgente { background: #fde8e8; color: #c0392b; }
.ml.vigilar { background: #fff3cd; color: #856404; }
.ml.exceso  { background: #D6E4F7; color: #1B3A6B; }
.ml.revisar { background: #F2F4F7; color: #555; }
.matriz-ejes { margin-bottom: 12px; }
.eje-y { font-size: 10px; color: #888; display: block; margin-bottom: 6px; }
.eje-x { font-size: 10px; color: #888; display: block; text-align: right; margin-top: 6px; }
.matriz-grid {
  display: flex; flex-wrap: wrap; gap: 10px;
  background: #F2F4F7; border-radius: 8px;
  padding: 12px; min-height: 80px;
}
.matriz-punto {
  display: flex; flex-direction: column;
  align-items: center; gap: 3px; cursor: default;
}
.punto-dot {
  width: 14px; height: 14px; border-radius: 50%;
}
.matriz-punto.urgente .punto-dot { background: #E24B4A; }
.matriz-punto.vigilar .punto-dot { background: #EF9F27; }
.matriz-punto.exceso  .punto-dot { background: #378ADD; }
.matriz-punto.revisar .punto-dot { background: #888; }
.punto-label { font-size: 9px; color: #555; text-align: center; max-width: 60px; }
.matriz-tabla { overflow-x: auto; margin-top: 12px; }
.badge-urgente { background: #fde8e8; color: #c0392b; padding: 2px 8px; border-radius: 10px; font-size: 11px; white-space: nowrap; }
.badge-vigilar { background: #fff3cd; color: #856404; padding: 2px 8px; border-radius: 10px; font-size: 11px; white-space: nowrap; }
.badge-exceso  { background: #D6E4F7; color: #1B3A6B; padding: 2px 8px; border-radius: 10px; font-size: 11px; white-space: nowrap; }
.badge-revisar { background: #F2F4F7; color: #555; padding: 2px 8px; border-radius: 10px; font-size: 11px; white-space: nowrap; }

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