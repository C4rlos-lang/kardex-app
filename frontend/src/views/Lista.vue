<template>
  <div>
    <h1>Bodega Principal</h1>

    <div class="buscador">
      <input 
        v-model="busqueda" 
        type="text" 
        placeholder="🔍 Buscar por nombre, SKU, marca o categoría..." 
      />
    </div>

    <p v-if="cargando">Cargando productos...</p>

    <table v-else>
      <thead>
        <tr>
          <th>Foto</th>
          <th>SKU</th>
          <th>Nombre</th>
          <th>Marca</th>
          <th>Categoría</th>
          <th>Proveedor</th>
          <th>Precio</th>
          <th>Stock</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="producto in productosPaginados" :key="producto.id">
          <td>
            <img v-if="producto.foto_url" :src="producto.foto_url" class="foto" />
            <span v-else>Sin foto</span>
          </td>
          <td>{{ producto.sku }}</td>
          <td>{{ producto.nombre }}</td>
          <td>{{ producto.marca }}</td>
          <td>{{ producto.categoria }}</td>
          <td>{{ producto.proveedor }}</td>
          <td>${{ producto.precio }}</td>
          <td>{{ producto.stock }}</td>
          <td>
            <div style="display:flex; gap:6px; flex-wrap:wrap;">
              <button class="btn-transferir-row" @click="abrirTransferencia(producto)">
                📦 Transferir
              </button>
              <button class="btn-tallas-row" @click="verTallasProducto(producto)">
                👁️ Tallas
              </button>
            </div>
          </td>
        </tr>
        <tr v-if="productosPaginados.length === 0">
          <td colspan="9" style="text-align:center; color:#888;">
            No se encontraron productos
          </td>
        </tr>
      </tbody>
    </table>

    <div class="paginacion" v-if="totalPaginas > 1">
      <button @click="paginaAnterior" :disabled="paginaActual === 1">← Anterior</button>
      <span v-for="pagina in totalPaginas" :key="pagina">
        <button @click="irAPagina(pagina)" :class="pagina === paginaActual ? 'activa' : ''">
          {{ pagina }}
        </button>
      </span>
      <button @click="paginaSiguiente" :disabled="paginaActual === totalPaginas">Siguiente →</button>
      <span class="info">
        Página {{ paginaActual }} de {{ totalPaginas }} 
        ({{ productosFiltrados.length }} productos)
      </span>
    </div>

    <!-- Overlay transferencia -->
    <div class="overlay" v-if="panelAbierto" @click.self="panelAbierto = false"></div>

    <!-- Panel transferencia -->
    <div class="panel" :class="{ abierto: panelAbierto }">
      <div class="panel-header">
        <h2>Nueva Transferencia</h2>
        <button class="cerrar" @click="panelAbierto = false">✕</button>
      </div>
      <div class="panel-body">
        <div class="campo">
          <label>Origen</label>
          <input type="text" value="Bodega Principal" disabled />
        </div>
        <div class="campo">
          <label>Destino (Almacén)</label>
          <select v-model="transferencia.almacen_id">
            <option value="">Selecciona un almacén...</option>
            <option v-for="a in almacenes" :key="a.id" :value="a.id">
              {{ a.nombre }} - {{ a.ciudad }}
            </option>
          </select>
        </div>
        <div class="campo">
          <label>Producto</label>
          <select v-model="transferencia.producto_id" @change="cargarTallasTransferencia">
            <option value="">Selecciona un producto...</option>
            <option v-for="p in productos" :key="p.id" :value="p.id">
              {{ p.nombre }} (Stock: {{ p.stock }})
            </option>
          </select>
        </div>
        <div class="campo" v-if="tallasTransferencia.length > 0">
          <label>Talla</label>
          <select v-model="transferencia.talla">
            <option value="">Selecciona una talla...</option>
            <option v-for="t in tallasTransferencia" :key="t.id" :value="t.talla">
              Talla {{ t.talla }} - {{ t.genero }} ({{ t.unidades }} uds)
            </option>
          </select>
        </div>
        <div class="campo" v-if="transferencia.talla">
          <label>Cantidad</label>
          <input 
            v-model="transferencia.cantidad" 
            type="number" 
            min="1" 
            placeholder="Ej: 5"
          />
        </div>
        <button class="btn-confirmar" @click="confirmarTransferencia" :disabled="cargandoTransferencia">
          {{ cargandoTransferencia ? 'Transfiriendo...' : '✅ Confirmar Transferencia' }}
        </button>
        <p v-if="mensajeTransferencia" :class="exitoTransferencia ? 'exito' : 'error'">
          {{ mensajeTransferencia }}
        </p>
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
        <p v-else-if="tallas.length === 0">Sin tallas registradas.</p>
        <div v-else>
          <button class="btn-imprimir" @click="imprimir">🖨️ Imprimir todas</button>
          <div class="etiquetas-wrap" id="etiquetas-print">
            <div class="etiqueta" v-for="(t, i) in tallas" :key="i">
              <p class="et-nombre">{{ productoEtiquetas?.nombre }}</p>
              <p class="et-sku">{{ productoEtiquetas?.sku }}</p>
              <span class="et-talla">{{ t.talla }}</span>
              <canvas :id="'qr-' + i" class="qr-canvas"></canvas>
              <p class="et-codigo">{{ productoEtiquetas?.sku }}-T{{ t.talla }}</p>
            </div>
          </div>
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
        <p v-if="cargandoTallasVista">Cargando...</p>
        <p v-else-if="tallasVista.length === 0">Sin tallas con stock disponible.</p>
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

  </div>
</template>

<script>
import axios from 'axios'

const API = import.meta.env.VITE_API_URL

export default {
  data() {
    return {
      productos: [],
      busqueda: '',
      cargando: true,
      paginaActual: 1,
      porPagina: 10,
      panelAbierto: false,
      almacenes: [],
      transferencia: { almacen_id: '', producto_id: '', cantidad: 0, talla: '', genero: '' },
      mensajeTransferencia: '',
      exitoTransferencia: false,
      cargandoTransferencia: false,
      tallasTransferencia: [],
      panelEtiquetasAbierto: false,
      productoEtiquetas: null,
      tallas: [],
      cargandoEtiquetas: false,
      panelTallasAbierto: false,
      productoTallas: null,
      tallasVista: [],
      cargandoTallasVista: false
    }
  },
  computed: {
    productosFiltrados() {
      const b = this.busqueda.toLowerCase()
      if (!b) return this.productos
      return this.productos.filter(p =>
        (p.nombre && p.nombre.toLowerCase().includes(b)) ||
        (p.sku && p.sku.toLowerCase().includes(b)) ||
        (p.marca && p.marca.toLowerCase().includes(b)) ||
        (p.categoria && p.categoria.toLowerCase().includes(b))
      )
    },
    totalPaginas() {
      return Math.ceil(this.productosFiltrados.length / this.porPagina)
    },
    productosPaginados() {
      const inicio = (this.paginaActual - 1) * this.porPagina
      const fin = inicio + this.porPagina
      return this.productosFiltrados.slice(inicio, fin)
    }
  },
  watch: {
    busqueda() { this.paginaActual = 1 }
  },
  methods: {
    irAPagina(pagina) { this.paginaActual = pagina },
    paginaAnterior() { if (this.paginaActual > 1) this.paginaActual-- },
    paginaSiguiente() { if (this.paginaActual < this.totalPaginas) this.paginaActual++ },
    abrirTransferencia(producto) {
      this.transferencia.producto_id = producto.id
      this.panelAbierto = true
      this.cargarTallasTransferencia()
    },
    async verTallasProducto(producto) {
      this.productoTallas = producto
      this.panelTallasAbierto = true
      this.cargandoTallasVista = true
      try {
        const { data } = await axios.get(`${API}/productos/${producto.id}/tallas`)
        this.tallasVista = data.filter(t => t.unidades > 0)
      } catch (error) {
        console.error('Error', error)
      }
      this.cargandoTallasVista = false
    },
    async cargarTallasTransferencia() {
      if (!this.transferencia.producto_id) return
      try {
        const { data } = await axios.get(`${API}/productos/${this.transferencia.producto_id}/tallas`)
        this.tallasTransferencia = data.filter(t => t.unidades > 0)
      } catch (error) {
        console.error('Error cargando tallas', error)
      }
    },
    async confirmarTransferencia() {
      if (!this.transferencia.almacen_id || !this.transferencia.producto_id || !this.transferencia.cantidad || !this.transferencia.talla) {
        this.mensajeTransferencia = 'Por favor llena todos los campos incluyendo la talla'
        this.exitoTransferencia = false
        return
      }
      this.cargandoTransferencia = true
      try {
        await axios.post(`${API}/transferencias`, {
          almacen_id: this.transferencia.almacen_id,
          producto_id: this.transferencia.producto_id,
          cantidad: parseFloat(this.transferencia.cantidad),
          talla: this.transferencia.talla,
          genero: this.tallasTransferencia.find(t => t.talla === this.transferencia.talla)?.genero || ''
        })
        this.mensajeTransferencia = '¡Transferencia realizada exitosamente!'
        this.exitoTransferencia = true
        this.transferencia = { almacen_id: '', producto_id: '', cantidad: 0, talla: '', genero: '' }
        this.tallasTransferencia = []
        const { data } = await axios.get(`${API}/productos`)
        this.productos = data.sort((a, b) =>
          new Date(b.fecha_registro) - new Date(a.fecha_registro)
        )
      } catch (error) {
        this.mensajeTransferencia = error.response?.data?.detail || 'Error al transferir'
        this.exitoTransferencia = false
      }
      this.cargandoTransferencia = false
    },
    async verEtiquetas(producto) {
      this.productoEtiquetas = producto
      this.panelEtiquetasAbierto = true
      this.cargandoEtiquetas = true
      try {
        const { data } = await axios.get(`${API}/productos/${producto.id}/tallas`)
        this.tallas = data
        this.$nextTick(() => { this.generarQRs() })
      } catch (error) {
        console.error('Error cargando tallas', error)
      }
      this.cargandoEtiquetas = false
    },
    generarQRs() {
      import('qrcode').then(QRCode => {
        this.tallas.forEach((t, i) => {
          const canvas = document.getElementById(`qr-${i}`)
          if (canvas) {
            const texto = `${this.productoEtiquetas.sku} | ${this.productoEtiquetas.nombre} | Talla: ${t.talla}`
            QRCode.toCanvas(canvas, texto, { width: 80 })
          }
        })
      })
    },
    async imprimir() {
      const QRCode = await import('qrcode')
      const etiquetas = await Promise.all(this.tallas.map(async (t) => {
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
      const [productosRes, almacenesRes] = await Promise.all([
        axios.get(`${API}/productos`),
        axios.get(`${API}/almacenes`)
      ])
      this.productos = productosRes.data.sort((a, b) =>
        new Date(b.fecha_registro) - new Date(a.fecha_registro)
      )
      this.almacenes = almacenesRes.data
    } catch (error) {
      console.error('Error cargando datos', error)
    }
    this.cargando = false
  }
}
</script>

<style scoped>
h1 { margin-bottom: 16px; color: #1B3A6B; }
.buscador { margin-bottom: 16px; }
.buscador input {
  width: 100%; max-width: 500px;
  padding: 10px 14px; font-size: 15px;
  border: 1px solid #ccc; border-radius: 8px;
}
.btn-transferir-row {
  padding: 5px 10px; background: #2E5FA3;
  color: white; border: none;
  border-radius: 6px; cursor: pointer; font-size: 12px;
}
.btn-tallas-row {
  padding: 5px 10px; background: #8C9BAB;
  color: white; border: none;
  border-radius: 6px; cursor: pointer; font-size: 12px;
}
table {
  width: 100%; border-collapse: collapse;
  background: white; border-radius: 8px;
  overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
thead { background: #1B3A6B; color: white; }
th, td { padding: 12px 16px; text-align: left; font-size: 14px; }
tbody tr:nth-child(even) { background: #F2F4F7; }
tbody tr:hover { background: #D6E4F7; }
.foto { width: 50px; height: 50px; object-fit: cover; border-radius: 4px; }
.paginacion {
  display: flex; align-items: center;
  gap: 6px; margin-top: 20px; flex-wrap: wrap;
}
.paginacion button {
  padding: 6px 12px; border: 1px solid #ccc;
  background: white; border-radius: 4px;
  cursor: pointer; font-size: 14px;
}
.paginacion button:hover { background: #D6E4F7; }
.paginacion button.activa { background: #1B3A6B; color: white; border-color: #1B3A6B; }
.paginacion button:disabled { opacity: 0.4; cursor: not-allowed; }
.info { margin-left: 10px; font-size: 13px; color: #888; }
.overlay {
  position: fixed; top: 0; left: 0;
  width: 100%; height: 100%;
  background: rgba(0,0,0,0.3); z-index: 100;
}
.panel {
  position: fixed; top: 0; right: -450px;
  width: 450px; height: 100%;
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
.panel-header h2 { margin: 0; font-size: 18px; }
.cerrar {
  background: none; border: none;
  color: white; font-size: 20px; cursor: pointer;
}
.panel-body { padding: 24px; overflow-y: auto; flex: 1; }
.campo { margin-bottom: 16px; }
.campo label { display: block; font-size: 13px; color: #555; margin-bottom: 6px; }
.campo input, .campo select {
  width: 100%; padding: 8px 12px;
  border: 1px solid #ccc; border-radius: 6px; font-size: 14px;
}
.campo input:disabled { background: #f5f5f5; color: #888; }
.btn-confirmar {
  width: 100%; padding: 12px;
  background: #1E7E50; color: white;
  border: none; border-radius: 8px;
  cursor: pointer; font-size: 15px; margin-top: 8px;
}
.btn-confirmar:disabled { background: #ccc; }
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
.talla-badge {
  background: #D6E4F7; color: #1B3A6B;
  padding: 2px 10px; border-radius: 20px;
  font-weight: 500; font-size: 14px;
}
.exito { color: #1E7E50; margin-top: 12px; }
.error { color: red; margin-top: 12px; }
</style>