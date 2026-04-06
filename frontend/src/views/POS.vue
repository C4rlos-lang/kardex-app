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

      <!-- Header con almacén seleccionado -->
      <div class="pos-header">
        <span>🏪 {{ almacenSeleccionado.nombre }}</span>
        <button class="btn-cambiar" @click="almacenSeleccionado = null">Cambiar</button>
      </div>

      <div class="pos-grid">

        <!-- Panel izquierdo: buscar productos -->
        <div class="panel-productos">
          <h2>Productos</h2>
          <input
            v-model="busqueda"
            type="text"
            placeholder="🔍 Buscar por nombre o SKU..."
            class="buscador"
          />
          <p v-if="cargandoProductos">Cargando...</p>
          <div class="lista-productos">
            <div
              v-for="p in productosFiltrados" :key="p.id"
              class="producto-card"
              @click="seleccionarProducto(p)"
              :class="{ activo: productoActivo?.id === p.id }"
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
        <div class="panel-tallas" v-if="productoActivo">
          <h2>{{ productoActivo.nombre }}</h2>
          <p class="prod-precio">${{ productoActivo.precio?.toLocaleString() }}</p>
          <p v-if="cargandoTallas">Cargando tallas...</p>
          <div class="tallas-grid" v-else>
            <div
              v-for="t in tallas" :key="t.id"
              class="talla-card"
              @click="agregarAlCarrito(t)"
            >
              <span class="talla-num">{{ t.talla }}</span>
              <span class="talla-gen">{{ t.genero }}</span>
              <span class="talla-stock">{{ t.unidades }} uds</span>
            </div>
          </div>
        </div>

        <div class="panel-tallas vacio" v-else>
          <p>← Selecciona un producto</p>
        </div>

        <!-- Panel derecho: carrito -->
        <div class="panel-carrito">
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
              <p class="item-precio">${{ (item.precio * item.cantidad).toLocaleString() }}</p>
            </div>

            <div class="total-wrap">
              <span>Total</span>
              <span class="total">${{ totalCarrito.toLocaleString() }}</span>
            </div>

            <!-- Método de pago -->
            <div class="campo">
              <label>Método de pago</label>
              <div class="metodos-grid">
                <div
                  v-for="m in metodosPago" :key="m"
                  class="metodo-btn"
                  :class="{ activo: metodoPago === m }"
                  @click="metodoPago = m"
                >
                  {{ m }}
                </div>
              </div>
            </div>

            <button
              class="btn-venta"
              @click="confirmarVenta"
              :disabled="!metodoPago || cargandoVenta"
            >
              {{ cargandoVenta ? 'Procesando...' : '✅ Confirmar venta' }}
            </button>

            <p v-if="mensajeVenta" :class="exitoVenta ? 'exito' : 'error'">
              {{ mensajeVenta }}
            </p>
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
      exitoVenta: false
    }
  },
  computed: {
    productosFiltrados() {
      const b = this.busqueda.toLowerCase()
      if (!b) return this.productos
      return this.productos.filter(p =>
        (p.nombre && p.nombre.toLowerCase().includes(b)) ||
        (p.sku && p.sku.toLowerCase().includes(b))
      )
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
      if (existente) {
        existente.cantidad++
      } else {
        this.carrito.push({
          producto_id: this.productoActivo.id,
          nombre: this.productoActivo.nombre,
          talla: talla.talla,
          genero: talla.genero,
          precio: this.productoActivo.precio,
          cantidad: 1
        })
      }
    },
    incrementar(i) { this.carrito[i].cantidad++ },
    decrementar(i) {
      if (this.carrito[i].cantidad > 1) this.carrito[i].cantidad--
    },
    eliminarItem(i) { this.carrito.splice(i, 1) },
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
          }))
        })
        this.mensajeVenta = '¡Venta registrada exitosamente!'
        this.exitoVenta = true
        this.carrito = []
        this.metodoPago = ''
        this.productoActivo = null
        // Recargar inventario
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
.pos-grid {
  display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px;
}
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
.item-controls {
  display: flex; align-items: center; gap: 8px;
}
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
.exito { color: #1E7E50; margin-top: 12px; }
.error { color: red; margin-top: 12px; }
</style>