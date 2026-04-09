<template>
  <div>
    <h1>📋 Arqueo de Inventario</h1>

    <!-- Paso 1: Seleccionar almacén -->
    <div v-if="!almacenSeleccionado">
      <p class="subtitulo">Selecciona el almacén a arquear</p>
      <div class="almacenes-grid">
        <div
          v-for="a in almacenes" :key="a.id"
          class="almacen-card"
          @click="seleccionarAlmacen(a)"
        >
          <p class="alm-nombre">{{ a.nombre }}</p>
          <p class="alm-ciudad">{{ a.ciudad }}</p>
        </div>
      </div>
    </div>

    <!-- Paso 2: Arqueo -->
    <div v-else>

      <!-- Header -->
      <div class="arqueo-header">
        <span>🏪 {{ almacenSeleccionado.nombre }}</span>
        <button class="btn-cambiar" @click="resetear">Cambiar almacén</button>
      </div>

      <!-- Tipo y responsable -->
      <div class="config-wrap">
        <div class="campo">
          <label>Tipo de arqueo</label>
          <select v-model="tipoArqueo" @change="filtroMarca = ''">
            <option value="total">Total del almacén</option>
            <option value="por_marca">Por marca</option>
            <option value="por_producto">Por producto específico</option>
          </select>
        </div>
        <div class="campo" v-if="tipoArqueo === 'por_marca'">
          <label>Seleccionar marca</label>
          <select v-model="filtroMarca">
            <option value="">Todas las marcas</option>
            <option v-for="m in marcasDisponibles" :key="m" :value="m">{{ m }}</option>
          </select>
        </div>
        <div class="campo">
          <label>Responsable</label>
          <input v-model="responsable" type="text" placeholder="Nombre del responsable" />
        </div>
      </div>

      <!-- Buscador y QR -->
      <div class="buscador-wrap">
        <input
          v-model="busqueda"
          type="text"
          placeholder="🔍 Buscar producto por nombre o SKU..."
          class="buscador"
        />
        <button class="btn-qr" @click="activarQR">📷 Escanear QR</button>
      </div>

      <div v-if="escaneando">
        <div id="lector-qr-arqueo"></div>
        <button class="btn-cerrar-qr" @click="detenerQR">✕ Cerrar escáner</button>
      </div>

      <!-- Lista de productos -->
      <p v-if="cargandoProductos">Cargando productos...</p>
      <div v-else class="productos-arqueo">
        <div
          v-for="p in productosFiltrados" :key="p.sku"
          class="producto-row"
          @click="agregarProducto(p)"
        >
          <img v-if="p.foto_url" :src="p.foto_url" class="prod-foto" />
          <div class="prod-info">
            <p class="prod-nombre">{{ p.nombre }}</p>
            <p class="prod-sku">{{ p.sku }} · Marca: {{ p.marca }} · Stock sistema: {{ p.stockTotal }}</p>
          </div>
          <button class="btn-agregar">+ Contar</button>
        </div>
        <p v-if="productosFiltrados.length === 0" class="sin-datos">
          No hay productos para mostrar
        </p>
      </div>

      <!-- Tabla de conteo -->
      <div v-if="conteo.length > 0" class="conteo-wrap">
        <h2>📊 Conteo físico</h2>
        <table>
          <thead>
            <tr>
              <th>Producto</th>
              <th>Talla</th>
              <th>Género</th>
              <th>Sistema</th>
              <th>Físico</th>
              <th>Diferencia</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, i) in conteo" :key="i" :class="diferencia(item) !== 0 ? 'fila-diferencia' : ''">
              <td>{{ item.nombre }}</td>
              <td><span class="talla-badge">{{ item.talla }}</span></td>
              <td>{{ item.genero }}</td>
              <td>{{ item.stock_sistema }}</td>
              <td>
                <input
                  v-model.number="item.stock_fisico"
                  type="number"
                  min="0"
                  class="input-fisico"
                />
              </td>
              <td>
                <span :class="diferencia(item) < 0 ? 'dif-negativa' : diferencia(item) > 0 ? 'dif-positiva' : 'dif-cero'">
                  {{ diferencia(item) > 0 ? '+' : '' }}{{ diferencia(item) }}
                </span>
              </td>
              <td>
                <button class="btn-quitar" @click="conteo.splice(i, 1)">✕</button>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Resumen -->
        <div class="resumen">
          <div class="resumen-item">
            <span>Items contados</span>
            <strong>{{ conteo.length }}</strong>
          </div>
          <div class="resumen-item">
            <span>Con diferencias</span>
            <strong class="naranja">{{ conDiferencias }}</strong>
          </div>
          <div class="resumen-item">
            <span>Sin diferencias</span>
            <strong class="verde">{{ sinDiferencias }}</strong>
          </div>
        </div>

        <button
          class="btn-confirmar"
          @click="confirmarArqueo"
          :disabled="cargando"
        >
          {{ cargando ? 'Guardando...' : '✅ Confirmar arqueo y ajustar stock' }}
        </button>

        <p v-if="mensaje" :class="exito ? 'exito' : 'error'">{{ mensaje }}</p>
      </div>

    </div>

    <!-- Panel tallas -->
    <div class="overlay" v-if="panelTallasAbierto" @click.self="panelTallasAbierto = false"></div>
    <div class="panel" :class="{ abierto: panelTallasAbierto }">
      <div class="panel-header">
        <h2>Seleccionar talla — {{ productoActivo?.nombre }}</h2>
        <button class="cerrar" @click="panelTallasAbierto = false">✕</button>
      </div>
      <div class="panel-body">
        <p v-if="cargandoTallas">Cargando tallas...</p>
        <p v-else-if="tallasActivas.length === 0">Sin tallas en este almacén.</p>
        <div class="tallas-grid" v-else>
          <div
            v-for="t in tallasActivas" :key="t.id"
            class="talla-card"
            @click="agregarTallaAlConteo(t)"
          >
            <span class="talla-num">{{ t.talla }}</span>
            <span class="talla-gen">{{ t.genero }}</span>
            <span class="talla-stock">{{ t.unidades }} uds</span>
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
      almacenes: [],
      almacenSeleccionado: null,
      tipoArqueo: 'total',
      filtroMarca: '',
      responsable: '',
      busqueda: '',
      productos: [],
      cargandoProductos: false,
      conteo: [],
      cargando: false,
      mensaje: '',
      exito: false,
      escaneando: false,
      scannerInstancia: null,
      panelTallasAbierto: false,
      productoActivo: null,
      tallasActivas: [],
      cargandoTallas: false
    }
  },
  computed: {
    marcasDisponibles() {
      const marcas = this.productos
        .map(p => p.marca)
        .filter(m => m && m.trim() !== '')
      return [...new Set(marcas)].sort()
    },
    productosFiltrados() {
      const b = this.busqueda.toLowerCase()
      let lista = this.productos

      // Filtro por marca
      if (this.tipoArqueo === 'por_marca' && this.filtroMarca) {
        lista = lista.filter(p => p.marca === this.filtroMarca)
      }

      // Filtro por búsqueda
      if (b) {
        lista = lista.filter(p =>
          (p.nombre && p.nombre.toLowerCase().includes(b)) ||
          (p.sku && p.sku.toLowerCase().includes(b))
        )
      }

      // Consolidar por SKU
      const mapa = {}
      lista.forEach(p => {
        if (!mapa[p.sku]) mapa[p.sku] = { ...p, stockTotal: 0 }
        mapa[p.sku].stockTotal += p.stock
      })
      return Object.values(mapa)
    },
    conDiferencias() {
      return this.conteo.filter(i => this.diferencia(i) !== 0).length
    },
    sinDiferencias() {
      return this.conteo.filter(i => this.diferencia(i) === 0).length
    }
  },
  methods: {
    async seleccionarAlmacen(almacen) {
      this.almacenSeleccionado = almacen
      this.cargandoProductos = true
      try {
        const { data } = await axios.get(`${API}/almacenes/${almacen.id}/inventario`)
        this.productos = data
      } catch (error) {
        console.error('Error', error)
      }
      this.cargandoProductos = false
    },
    async agregarProducto(producto) {
      this.productoActivo = producto
      this.panelTallasAbierto = true
      this.cargandoTallas = true
      try {
        const { data } = await axios.get(
          `${API}/almacenes/${this.almacenSeleccionado.id}/productos/${producto.id}/tallas`
        )
        this.tallasActivas = data
      } catch (error) {
        console.error('Error', error)
      }
      this.cargandoTallas = false
    },
    agregarTallaAlConteo(talla) {
      const existe = this.conteo.find(
        i => i.producto_id === this.productoActivo.id && i.talla === talla.talla
      )
      if (existe) {
        this.panelTallasAbierto = false
        return
      }
      this.conteo.push({
        producto_id: this.productoActivo.id,
        nombre: this.productoActivo.nombre,
        talla: talla.talla,
        genero: talla.genero,
        stock_sistema: talla.unidades,
        stock_fisico: talla.unidades
      })
      this.panelTallasAbierto = false
    },
    diferencia(item) {
      return (item.stock_fisico || 0) - item.stock_sistema
    },
    activarQR() {
      this.escaneando = true
      this.$nextTick(() => {
        import('html5-qrcode').then(({ Html5Qrcode }) => {
          this.scannerInstancia = new Html5Qrcode('lector-qr-arqueo')
          this.scannerInstancia.start(
            { facingMode: 'environment' },
            { fps: 10, qrbox: { width: 250, height: 250 } },
            (texto) => {
              this.procesarQR(texto)
              this.detenerQR()
            },
            () => {}
          ).catch(() => {
            alert('No se pudo acceder a la cámara')
            this.escaneando = false
          })
        })
      })
    },
    detenerQR() {
      if (this.scannerInstancia) {
        this.scannerInstancia.stop().then(() => {
          this.scannerInstancia = null
          this.escaneando = false
        })
      }
    },
    async procesarQR(texto) {
      const partes = texto.split('|').map(p => p.trim())
      if (partes.length < 2) { alert('QR no reconocido'); return }
      const sku = partes[0]
      const producto = this.productosFiltrados.find(p => p.sku === sku)
      if (!producto) { alert(`Producto ${sku} no encontrado`); return }
      await this.agregarProducto(producto)
    },
    async confirmarArqueo() {
      if (this.conteo.length === 0) return
      this.cargando = true
      try {
        await axios.post(`${API}/arqueos`, {
          almacen_id: this.almacenSeleccionado.id,
          tipo: this.tipoArqueo,
          responsable: this.responsable,
          detalles: this.conteo.map(i => ({
            producto_id: i.producto_id,
            talla: i.talla,
            genero: i.genero,
            stock_sistema: i.stock_sistema,
            stock_fisico: i.stock_fisico || 0
          }))
        })
        this.mensaje = '¡Arqueo completado y stock ajustado exitosamente!'
        this.exito = true
        this.conteo = []
      } catch (error) {
        this.mensaje = error.response?.data?.detail || 'Error al guardar el arqueo'
        this.exito = false
      }
      this.cargando = false
    },
    resetear() {
      this.almacenSeleccionado = null
      this.productos = []
      this.conteo = []
      this.busqueda = ''
      this.filtroMarca = ''
      this.mensaje = ''
    }
  },
  async mounted() {
    try {
      const { data } = await axios.get(`${API}/almacenes`)
      this.almacenes = data.filter(a => a.estado === 'activo')
    } catch (error) {
      console.error('Error', error)
    }
  }
}
</script>

<style scoped>
h1 { margin-bottom: 8px; color: #1B3A6B; }
h2 { font-size: 16px; color: #1B3A6B; margin-bottom: 12px; }
.subtitulo { color: #888; margin-bottom: 16px; font-size: 14px; }
.almacenes-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 16px; }
.almacen-card {
  background: white; border: 1px solid #ccc;
  border-radius: 8px; padding: 16px; cursor: pointer; text-align: center;
}
.almacen-card:hover { border-color: #1B3A6B; background: #D6E4F7; }
.alm-nombre { font-weight: 500; color: #1B3A6B; }
.alm-ciudad { font-size: 13px; color: #888; }
.arqueo-header {
  display: flex; justify-content: space-between; align-items: center;
  background: #1B3A6B; color: white;
  padding: 12px 16px; border-radius: 8px; margin-bottom: 16px;
}
.btn-cambiar {
  background: none; border: 1px solid white;
  color: white; padding: 4px 12px; border-radius: 4px; cursor: pointer;
}
.config-wrap { display: flex; gap: 16px; margin-bottom: 16px; flex-wrap: wrap; }
.campo { flex: 1; min-width: 160px; }
label { font-size: 13px; color: #555; display: block; margin-bottom: 4px; }
input, select {
  width: 100%; padding: 8px 12px;
  border: 1px solid #ccc; border-radius: 6px; font-size: 14px;
}
.buscador-wrap { display: flex; gap: 8px; margin-bottom: 16px; }
.buscador { flex: 1; padding: 8px 12px; border: 1px solid #ccc; border-radius: 6px; font-size: 14px; }
.btn-qr {
  padding: 8px 16px; background: #2E5FA3; color: white;
  border: none; border-radius: 6px; cursor: pointer; font-size: 14px;
}
.btn-cerrar-qr {
  width: 100%; padding: 6px; background: #c0392b; color: white;
  border: none; border-radius: 6px; cursor: pointer; font-size: 13px; margin-top: 8px;
}
#lector-qr-arqueo { width: 100%; border-radius: 8px; overflow: hidden; margin-bottom: 8px; }
.productos-arqueo { display: flex; flex-direction: column; gap: 8px; margin-bottom: 24px; }
.producto-row {
  display: flex; align-items: center; gap: 12px;
  background: white; border: 1px solid #eee;
  border-radius: 8px; padding: 10px 16px; cursor: pointer;
}
.producto-row:hover { border-color: #1B3A6B; background: #D6E4F7; }
.prod-foto { width: 40px; height: 40px; object-fit: cover; border-radius: 4px; }
.prod-info { flex: 1; }
.prod-nombre { font-size: 13px; font-weight: 500; color: #333; }
.prod-sku { font-size: 11px; color: #888; }
.btn-agregar {
  padding: 6px 12px; background: #1E7E50; color: white;
  border: none; border-radius: 6px; cursor: pointer; font-size: 13px;
}
.conteo-wrap { margin-top: 24px; }
table {
  width: 100%; border-collapse: collapse;
  background: white; border-radius: 8px;
  overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
thead { background: #1B3A6B; color: white; }
th, td { padding: 10px 14px; text-align: left; font-size: 13px; }
tbody tr:nth-child(even) { background: #F2F4F7; }
.fila-diferencia { background: #fff3cd !important; }
.talla-badge {
  background: #D6E4F7; color: #1B3A6B;
  padding: 2px 8px; border-radius: 12px; font-size: 13px;
}
.input-fisico {
  width: 70px; padding: 4px 8px;
  border: 1px solid #ccc; border-radius: 4px; font-size: 13px;
}
.dif-negativa { color: #c0392b; font-weight: 600; }
.dif-positiva { color: #1E7E50; font-weight: 600; }
.dif-cero { color: #888; }
.btn-quitar {
  background: none; border: none; color: #c0392b;
  cursor: pointer; font-size: 14px;
}
.resumen {
  display: flex; gap: 24px; padding: 16px;
  background: #F2F4F7; border-radius: 8px; margin: 16px 0;
}
.resumen-item { display: flex; flex-direction: column; gap: 4px; }
.resumen-item span { font-size: 12px; color: #888; }
.resumen-item strong { font-size: 20px; color: #1B3A6B; }
.resumen-item strong.naranja { color: #D35400; }
.resumen-item strong.verde { color: #1E7E50; }
.btn-confirmar {
  width: 100%; padding: 12px; background: #1B3A6B;
  color: white; border: none; border-radius: 8px;
  cursor: pointer; font-size: 15px;
}
.btn-confirmar:disabled { background: #ccc; }
.exito { color: #1E7E50; margin-top: 12px; }
.error { color: red; margin-top: 12px; }
.sin-datos { color: #888; font-size: 14px; text-align: center; padding: 24px; }
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
.panel-header h2 { margin: 0; font-size: 16px; color: white; }
.cerrar { background: none; border: none; color: white; font-size: 20px; cursor: pointer; }
.panel-body { padding: 24px; overflow-y: auto; flex: 1; }
.tallas-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
.talla-card {
  border: 1px solid #ccc; border-radius: 6px;
  padding: 10px; text-align: center; cursor: pointer;
  display: flex; flex-direction: column; gap: 2px;
}
.talla-card:hover { border-color: #1B3A6B; background: #D6E4F7; }
.talla-num { font-size: 18px; font-weight: 500; color: #1B3A6B; }
.talla-gen { font-size: 10px; color: #888; }
.talla-stock { font-size: 11px; color: #1E7E50; }
</style>