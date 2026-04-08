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
            <button class="btn-ver" @click="verInventario(almacen)">
              👁️ Ver inventario
            </button>
            <button class="btn-dashboard" @click="verDashboard(almacen)">
            📊 Dashboard
            </button>
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
        <table v-else class="tabla-inventario">
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
                <div style="display:flex; gap:6px;">
                  <button class="btn-etiqueta" @click="verEtiquetas(item)">🏷️ Etiquetas</button>
                  <button class="btn-tallas" @click="verTallas(item)">👁️ Tallas</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
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

  </div>
</template>

<script>
import axios from 'axios'

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
      cargandoEtiquetas: false
    }
  },
  computed: {
    inventarioAgrupado() {
      const mapa = {}
      this.inventario.forEach(item => {
        if (!mapa[item.id]) {
          mapa[item.id] = { ...item, stockTotal: 0 }
        }
        mapa[item.id].stockTotal += item.stock
      })
      return Object.values(mapa)
    }
  },
  methods: {
    async verInventario(almacen) {
      this.almacenSeleccionado = almacen
      this.panelAbierto = true
      this.cargandoInventario = true
      try {
        const { data } = await axios.get(`https://kardex-app.onrender.com/almacenes/${almacen.id}/inventario`)
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
          `https://kardex-app.onrender.com/almacenes/${this.almacenSeleccionado.id}/productos/${item.id}/tallas`
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
          `https://kardex-app.onrender.com/almacenes/${this.almacenSeleccionado.id}/productos/${item.id}/tallas`
        )
        this.tallasEtiquetas = data
        this.$nextTick(() => { this.generarQRs() })
      } catch (error) {
        console.error('Error', error)
      }
      this.cargandoEtiquetas = false
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
    }
  },
  async mounted() {
    try {
      const { data } = await axios.get('https://kardex-app.onrender.com/almacenes')
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
.tabla-inventario { margin-top: 0; }
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
</style>