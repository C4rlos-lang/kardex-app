<template>
  <div>
    <h1>Punto de Venta</h1>

    <!-- Seleccionar almacén -->
    <div class="campo" v-if="!almacenSeleccionado">
      <label>Selecciona el almacén</label>
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

    <!-- POS principal -->
    <div v-else class="pos-wrap">

      <div class="pos-header">
        <span>🏪 {{ almacenSeleccionado.nombre }}</span>
        <button class="btn-cambiar" @click="almacenSeleccionado = null">Cambiar</button>
      </div>

      <!-- Tabs móvil -->
      <div class="tabs-movil">
        <button
          v-for="tab in tabs" :key="tab.key"
          class="tab-btn"
          :class="{ activo: tabActivo === tab.key }"
          @click="tabActivo = tab.key"
        >
          {{ tab.label }}
          <span v-if="tab.key === 'carrito' && carrito.length > 0" class="badge-carrito">
            {{ carrito.length }}
          </span>
        </button>
      </div>

      <div class="pos-grid">

        <!-- Panel izquierdo: buscar productos -->
        <div class="panel-productos" :class="{ 'tab-visible': tabActivo === 'productos' }">
          <h2>Productos</h2>
          <input
            v-model="busqueda"
            type="text"
            placeholder="🔍 Buscar por nombre o SKU..."
            class="buscador"
          />
          <button class="btn-qr" @click="activarQR">📷 Escanear QR</button>
          <div v-if="escaneando">
            <div id="lector-qr"></div>
            <button class="btn-cerrar-qr" @click="detenerQR">✕ Cerrar escáner</button>
          </div>
          <p v-if="cargandoProductos">Cargando...</p>
          <div class="lista-productos">
            <div
              v-for="p in productosFiltrados" :key="p.sku"
              class="producto-card"
              @click="seleccionarProducto(p); tabActivo = 'tallas'"
              :class="{ activo: productoActivo?.sku === p.sku }"
            >
              <img v-if="p.foto_url" :src="p.foto_url" class="prod-foto" />
              <div>
                <p class="prod-nombre">{{ p.nombre }}</p>
                <p class="prod-sku">{{ p.sku }}</p>
                <p class="prod-stock">Stock: {{ p.stock }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Panel centro: tallas -->
        <div class="panel-tallas" :class="{ 'tab-visible': tabActivo === 'tallas' }" v-if="productoActivo">
          <h2>{{ productoActivo.nombre }}</h2>
          <p class="prod-precio">${{ productoActivo.precio?.toLocaleString() }}</p>
          <p v-if="cargandoTallas">Cargando tallas...</p>
          <div class="tallas-grid" v-else>
            <div
              v-for="t in tallas" :key="t.id"
              class="talla-card"
              @click="agregarAlCarrito(t); tabActivo = 'carrito'"
            >
              <span class="talla-num">{{ t.talla }}</span>
              <span class="talla-gen">{{ t.genero }}</span>
              <span class="talla-stock">{{ t.unidades }} uds</span>
            </div>
          </div>
        </div>

        <div class="panel-tallas vacio" :class="{ 'tab-visible': tabActivo === 'tallas' }" v-else>
          <p>← Selecciona un producto</p>
        </div>

        <!-- Panel derecho: carrito -->
        <div class="panel-carrito" :class="{ 'tab-visible': tabActivo === 'carrito' }">
          <h2>Carrito</h2>
          <p v-if="carrito.length === 0" class="carrito-vacio">Sin productos</p>
          <div v-else>
            <div class="carrito-item" v-for="(item, i) in carrito" :key="i">
              <div class="item-info">
                <p class="item-nombre">{{ item.nombre }}</p>
                <p class="item-talla">Talla {{ item.talla }} · {{ item.genero }}</p>
              </div>
              <div class="item-controls">
                <button @click="decrementar(i)">−</button>
                <span>{{ item.cantidad }}</span>
                <button @click="incrementar(i)">+</button>
                <button class="btn-eliminar" @click="eliminarItem(i)">✕</button>
              </div>

              <!-- Precio de venta editable -->
              <div class="precio-venta-wrap">
                <label class="precio-label">Precio de venta</label>
                <input
                  v-model.number="item.precio"
                  type="number"
                  class="precio-input"
                  placeholder="Ingresa el precio"
                />
                <div class="precios-rapidos">
                  <button @click="item.precio = 100000">$100k</button>
                  <button @click="item.precio = 150000">$150k</button>
                  <button @click="item.precio = 200000">$200k</button>
                </div>
              </div>

              <p class="item-precio">
                Subtotal: ${{ (item.precio * item.cantidad).toLocaleString('es-CO') }}
              </p>
            </div>

            <div class="total-wrap">
              <span>Total</span>
              <span class="total">${{ totalCarrito.toLocaleString() }}</span>
            </div>

            <div class="campo">
              <label>Método de pago</label>
              <div class="metodos-grid">
                <div
                  v-for="m in metodosPago" :key="m"
                  class="metodo-btn"
                  :class="{ activo: metodoPago === m }"
                  @click="metodoPago = m"
                >{{ m }}</div>
              </div>
            </div>

            <button
              class="btn-venta"
              @click="mostrarModalVenta = true"
              :disabled="!metodoPago || carrito.length === 0"
            >
              ✅ Confirmar venta
            </button>
          </div>
        </div>

      </div>
    </div>

    <!-- Panel lateral confirmación venta -->
    <div class="overlay" v-if="mostrarModalVenta" @click.self="mostrarModalVenta = false"></div>
    <div class="panel-lateral" :class="{ abierto: mostrarModalVenta }">
      <div class="panel-header">
        <h2>✅ Confirmar Venta</h2>
        <button class="cerrar" @click="mostrarModalVenta = false">✕</button>
      </div>
      <div class="panel-body">
        <p class="modal-total">Total: <strong>${{ totalCarrito.toLocaleString() }}</strong></p>
        <p class="modal-metodo">Método: {{ metodoPago }}</p>

        <div class="modal-seccion">
          <p class="modal-label">Datos del cliente <span class="opcional">(opcional)</span></p>
          <div class="campo">
            <label>Nombre</label>
            <input v-model="cliente.nombre" type="text" placeholder="Nombre completo" />
          </div>
          <div class="campo">
            <label>Documento</label>
            <input v-model="cliente.documento" type="text" placeholder="Número de documento" />
          </div>
          <div class="campo">
            <label>Teléfono (máx. 10 dígitos)</label>
            <input
              v-model="cliente.telefono"
              type="tel"
              placeholder="Ej: 3001234567"
              maxlength="10"
              @input="cliente.telefono = cliente.telefono.replace(/\D/g, '').slice(0, 10)"
            />
          </div>
          <div class="campo">
            <label>Correo</label>
            <input v-model="cliente.correo" type="email" placeholder="correo@ejemplo.com" />
          </div>
          <div class="campo">
            <label>Género</label>
            <select v-model="cliente.genero">
              <option value="">Selecciona...</option>
              <option value="Masculino">Masculino</option>
              <option value="Femenino">Femenino</option>
              <option value="No binario">No binario</option>
              <option value="Prefiero no decir">Prefiero no decir</option>
            </select>
          </div>
        </div>

        <div class="modal-botones">
          <button class="btn-cancelar" @click="mostrarModalVenta = false">Cancelar</button>
          <button class="btn-confirmar-modal" @click="confirmarVenta" :disabled="cargandoVenta">
            {{ cargandoVenta ? 'Procesando...' : '✅ Confirmar' }}
          </button>
        </div>

        <p v-if="mensajeVenta" :class="exitoVenta ? 'exito' : 'error'">
          {{ mensajeVenta }}
        </p>
      </div>
    </div>

    <!-- Panel éxito -->
    <div class="overlay" v-if="ventaConfirmada" @click.self="ventaConfirmada = false"></div>
    <div class="panel-lateral" :class="{ abierto: ventaConfirmada }">
      <div class="panel-header">
        <h2>🎉 ¡Venta registrada!</h2>
        <button class="cerrar" @click="ventaConfirmada = false">✕</button>
      </div>
      <div class="panel-body exito-body">
        <div class="exito-icon">🎉</div>
        <p class="modal-total">Total cobrado: <strong>${{ ultimoTotal.toLocaleString() }}</strong></p>
        <p class="modal-metodo">Método: {{ ultimoMetodo }}</p>
        <button class="btn-confirmar-modal" @click="ventaConfirmada = false">Aceptar</button>
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
      almacenSeleccionado: null,
      busqueda: '',
      productos: [],
      cargandoProductos: false,
      productoActivo: null,
      tallas: [],
      cargandoTallas: false,
      carrito: [],
      metodoPago: '',
      metodosPago: ['Efectivo', 'Tarjeta', 'Nequi', 'Brew B', 'Daviplata'],
      cargandoVenta: false,
      mensajeVenta: '',
      exitoVenta: false,
      escaneando: false,
      scannerInstancia: null,
      cliente: { nombre: '', telefono: '', correo: '', genero: '', documento: '' },
      mostrarModalVenta: false,
      ventaConfirmada: false,
      ultimoTotal: 0,
      ultimoMetodo: '',
      tabActivo: 'productos',
      tabs: [
        { key: 'productos', label: '📦 Productos' },
        { key: 'tallas',    label: '👟 Tallas'    },
        { key: 'carrito',   label: '🛒 Carrito'   },
      ]
    }
  },
  computed: {
    productosFiltrados() {
      const b = this.busqueda.toLowerCase()
      let lista = this.productos
      if (b) {
        lista = lista.filter(p =>
          (p.nombre && p.nombre.toLowerCase().includes(b)) ||
          (p.sku && p.sku.toLowerCase().includes(b))
        )
      }
      const mapa = {}
      lista.forEach(p => {
        if (!mapa[p.sku]) mapa[p.sku] = { ...p, stock: 0 }
        mapa[p.sku].stock += p.stock
      })
      return Object.values(mapa)
    },
    totalCarrito() {
      return this.carrito.reduce((sum, item) => sum + item.precio * item.cantidad, 0)
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
        console.error('Error cargando productos', error)
      }
      this.cargandoProductos = false
    },
    async seleccionarProducto(producto) {
      this.productoActivo = producto
      this.cargandoTallas = true
      try {
        const { data } = await axios.get(
          `${API}/almacenes/${this.almacenSeleccionado.id}/productos/${producto.id}/tallas`
        )
        this.tallas = data
      } catch (error) {
        console.error('Error cargando tallas', error)
      }
      this.cargandoTallas = false
    },
    agregarAlCarrito(talla) {
      const existente = this.carrito.find(
        i => i.producto_id === this.productoActivo.id && i.talla === talla.talla
      )
      const cantidadEnCarrito = existente ? existente.cantidad : 0
      if (cantidadEnCarrito >= talla.unidades) {
        alert(`Solo hay ${talla.unidades} unidades disponibles de talla ${talla.talla}`)
        return
      }
      if (existente) {
        existente.cantidad++
      } else {
        this.carrito.push({
          producto_id: this.productoActivo.id,
          nombre: this.productoActivo.nombre,
          talla: talla.talla,
          genero: talla.genero,
          precio: this.productoActivo.precio,
          cantidad: 1,
          maxUnidades: talla.unidades
        })
      }
    },
    incrementar(i) {
      const item = this.carrito[i]
      if (item.cantidad >= item.maxUnidades) {
        alert(`Solo hay ${item.maxUnidades} unidades disponibles de talla ${item.talla}`)
        return
      }
      item.cantidad++
    },
    decrementar(i) {
      if (this.carrito[i].cantidad > 1) {
        this.carrito[i].cantidad--
      } else {
        this.eliminarItem(i)
      }
    },
    eliminarItem(i) { this.carrito.splice(i, 1) },
    activarQR() {
      this.escaneando = true
      this.$nextTick(() => {
        import('html5-qrcode').then(({ Html5Qrcode }) => {
          this.scannerInstancia = new Html5Qrcode('lector-qr')
          this.scannerInstancia.start(
            { facingMode: 'environment' },
            { fps: 10, qrbox: { width: 250, height: 250 } },
            (texto) => { this.procesarQR(texto); this.detenerQR() },
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
      const talla = partes[2] ? partes[2].replace('Talla:', '').trim() : null
      const producto = this.productos.find(p => p.sku === sku)
      if (!producto) { alert(`Producto ${sku} no encontrado`); return }
      await this.seleccionarProducto(producto)
      if (talla) {
        const tallaEncontrada = this.tallas.find(t => t.talla === talla)
        if (tallaEncontrada) this.agregarAlCarrito(tallaEncontrada)
      }
      this.tabActivo = 'carrito'
    },
    async confirmarVenta() {
      this.cargandoVenta = true
      try {
        await axios.post(`${API}/ventas`, {
          almacen_id: this.almacenSeleccionado.id,
          metodo_pago: this.metodoPago,
          total: this.totalCarrito,
          detalle: this.carrito.map(item => ({
            producto_id: item.producto_id,
            talla: item.talla,
            cantidad: item.cantidad,
            precio_unitario: item.precio
          })),
          cliente: this.cliente
        })
        this.ultimoTotal = this.totalCarrito
        this.ultimoMetodo = this.metodoPago
        this.mostrarModalVenta = false
        this.ventaConfirmada = true
        this.carrito = []
        this.metodoPago = ''
        this.productoActivo = null
        this.tallas = []
        this.cliente = { nombre: '', telefono: '', correo: '', genero: '', documento: '' }
        this.mensajeVenta = ''
        this.tabActivo = 'productos'
        const { data } = await axios.get(`${API}/almacenes/${this.almacenSeleccionado.id}/inventario`)
        this.productos = data
      } catch (error) {
        this.mensajeVenta = error.response?.data?.detail || 'Error al procesar la venta'
        this.exitoVenta = false
      }
      this.cargandoVenta = false
    }
  },
  async mounted() {
    try {
      const { data } = await axios.get(`${API}/almacenes`)
      this.almacenes = data.filter(a => a.estado === 'activo')
    } catch (error) {
      console.error('Error cargando almacenes', error)
    }
  }
}
</script>

<style scoped>
h1 { margin-bottom: 24px; color: #1B3A6B; }
h2 { font-size: 16px; color: #1B3A6B; margin-bottom: 12px; }
.campo { margin-bottom: 16px; }
label { font-size: 13px; color: #555; display: block; margin-bottom: 8px; }
.almacenes-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 16px; }
.almacen-card {
  background: white; border: 1px solid #ccc;
  border-radius: 8px; padding: 16px; cursor: pointer; text-align: center;
}
.almacen-card:hover { border-color: #1B3A6B; background: #D6E4F7; }
.alm-nombre { font-weight: 500; color: #1B3A6B; }
.alm-ciudad { font-size: 13px; color: #888; }
.pos-header {
  display: flex; justify-content: space-between; align-items: center;
  background: #1B3A6B; color: white;
  padding: 12px 16px; border-radius: 8px; margin-bottom: 16px;
}
.btn-cambiar {
  background: none; border: 1px solid white;
  color: white; padding: 4px 12px; border-radius: 4px; cursor: pointer;
}

/* Tabs móvil — ocultos en desktop */
.tabs-movil { display: none; }

.pos-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }
.panel-productos, .panel-tallas, .panel-carrito {
  background: white; border-radius: 8px;
  padding: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  max-height: 80vh; overflow-y: auto;
}
.buscador {
  width: 100%; padding: 8px 12px;
  border: 1px solid #ccc; border-radius: 6px;
  font-size: 14px; margin-bottom: 12px;
}
.btn-qr {
  width: 100%; padding: 8px;
  background: #2E5FA3; color: white;
  border: none; border-radius: 6px;
  cursor: pointer; font-size: 14px; margin-bottom: 12px;
}
.btn-cerrar-qr {
  width: 100%; padding: 6px;
  background: #c0392b; color: white;
  border: none; border-radius: 6px;
  cursor: pointer; font-size: 13px; margin-top: 8px;
}
#lector-qr { width: 100%; border-radius: 8px; overflow: hidden; }
.lista-productos { display: flex; flex-direction: column; gap: 8px; }
.producto-card {
  display: flex; gap: 10px; align-items: center;
  padding: 8px; border: 1px solid #eee;
  border-radius: 6px; cursor: pointer;
}
.producto-card:hover, .producto-card.activo { border-color: #1B3A6B; background: #D6E4F7; }
.prod-foto { width: 40px; height: 40px; object-fit: cover; border-radius: 4px; }
.prod-nombre { font-size: 13px; font-weight: 500; color: #333; }
.prod-sku { font-size: 11px; color: #888; }
.prod-stock { font-size: 11px; color: #1E7E50; }
.prod-precio { font-size: 18px; font-weight: 500; color: #1B3A6B; margin-bottom: 16px; }
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
.panel-tallas.vacio { display: flex; align-items: center; justify-content: center; color: #888; }
.carrito-vacio { color: #888; text-align: center; margin-top: 24px; }
.carrito-item {
  border-bottom: 1px solid #eee; padding: 8px 0;
  display: flex; flex-direction: column; gap: 4px;
}
.item-nombre { font-size: 13px; font-weight: 500; }
.item-talla { font-size: 11px; color: #888; }
.item-controls { display: flex; align-items: center; gap: 8px; }
.item-controls button {
  width: 24px; height: 24px; border: 1px solid #ccc;
  background: white; border-radius: 4px; cursor: pointer;
}
.btn-eliminar { color: red !important; }
.item-precio { font-size: 13px; font-weight: 500; color: #1B3A6B; }
.total-wrap {
  display: flex; justify-content: space-between;
  padding: 12px 0; margin-top: 8px;
  border-top: 2px solid #1B3A6B;
}
.total { font-size: 20px; font-weight: 500; color: #1B3A6B; }
.metodos-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-top: 8px; }
.metodo-btn {
  padding: 8px; border: 1px solid #ccc;
  border-radius: 6px; text-align: center;
  cursor: pointer; font-size: 12px;
}
.metodo-btn.activo { border-color: #1B3A6B; background: #D6E4F7; color: #1B3A6B; font-weight: 500; }
.btn-venta {
  width: 100%; padding: 12px; margin-top: 12px;
  background: #1E7E50; color: white;
  border: none; border-radius: 8px;
  cursor: pointer; font-size: 15px;
}
.btn-venta:disabled { background: #ccc; }
.overlay {
  position: fixed; top: 0; left: 0;
  width: 100%; height: 100%;
  background: rgba(0,0,0,0.3); z-index: 100;
}
.panel-lateral {
  position: fixed; top: 0; right: -480px;
  width: 480px; height: 100%;
  background: white;
  box-shadow: -4px 0 20px rgba(0,0,0,0.15);
  z-index: 101; transition: right 0.3s ease;
  display: flex; flex-direction: column;
}
.panel-lateral.abierto { right: 0; }
.panel-header {
  display: flex; justify-content: space-between;
  align-items: center; padding: 20px 24px;
  background: #1B3A6B; color: white;
}
.panel-header h2 { margin: 0; font-size: 18px; color: white; }
.cerrar { background: none; border: none; color: white; font-size: 20px; cursor: pointer; }
.panel-body { padding: 24px; overflow-y: auto; flex: 1; }
.modal-total { font-size: 18px; margin-bottom: 8px; color: #333; }
.modal-metodo { font-size: 14px; color: #888; margin-bottom: 16px; }
.modal-seccion { border-top: 1px solid #eee; padding-top: 16px; margin-bottom: 16px; }
.modal-label { font-size: 14px; font-weight: 500; color: #1B3A6B; margin-bottom: 12px; }
.opcional { font-size: 12px; color: #888; font-weight: 400; }
.panel-body input, .panel-body select {
  width: 100%; padding: 8px 12px;
  border: 1px solid #ccc; border-radius: 6px;
  font-size: 14px; margin-top: 4px;
}
.modal-botones { display: flex; gap: 12px; margin-top: 16px; }
.btn-cancelar {
  flex: 1; padding: 10px; background: white; color: #888;
  border: 1px solid #ccc; border-radius: 8px; cursor: pointer; font-size: 14px;
}
.btn-confirmar-modal {
  flex: 1; padding: 10px; background: #1E7E50; color: white;
  border: none; border-radius: 8px; cursor: pointer; font-size: 14px;
}
.btn-confirmar-modal:disabled { background: #ccc; }
.exito-body { text-align: center; padding-top: 48px; }
.exito-icon { font-size: 64px; margin-bottom: 24px; }
.exito { color: #1E7E50; margin-top: 12px; }
.error { color: red; margin-top: 12px; }
.precio-venta-wrap {
  margin-top: 8px; padding: 8px;
  background: #F2F4F7; border-radius: 6px;
}
.precio-label { font-size: 11px; color: #888; display: block; margin-bottom: 4px; }
.precio-input {
  width: 100%; padding: 6px 10px;
  border: 1px solid #ccc; border-radius: 6px;
  font-size: 14px; margin-bottom: 6px;
}
.precios-rapidos { display: flex; gap: 6px; }
.precios-rapidos button {
  flex: 1; padding: 4px 6px; background: white;
  border: 1px solid #2E5FA3; color: #2E5FA3;
  border-radius: 4px; cursor: pointer; font-size: 11px; font-weight: 500;
}
.precios-rapidos button:hover { background: #D6E4F7; }

/* ── Responsive ────────────────────────────────────────────────── */
@media (max-width: 768px) {
  .tabs-movil {
    display: flex; gap: 8px;
    margin-bottom: 16px;
  }
  .tab-btn {
    flex: 1; padding: 10px 8px;
    border: 1px solid #ccc; background: white;
    border-radius: 8px; cursor: pointer;
    font-size: 13px; color: #555;
    position: relative;
  }
  .tab-btn.activo {
    background: #1B3A6B; color: white; border-color: #1B3A6B;
  }
  .badge-carrito {
    position: absolute; top: -6px; right: -6px;
    background: #c0392b; color: white;
    border-radius: 50%; width: 18px; height: 18px;
    font-size: 11px; display: flex;
    align-items: center; justify-content: center;
  }
  .pos-grid {
    grid-template-columns: 1fr;
  }
  .panel-productos,
  .panel-tallas,
  .panel-carrito {
    display: none;
    max-height: none;
  }
  .panel-productos.tab-visible,
  .panel-tallas.tab-visible,
  .panel-carrito.tab-visible {
    display: block;
  }
  .panel-lateral {
    width: 100vw;
    right: -100vw;
  }
  .tallas-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
</style>