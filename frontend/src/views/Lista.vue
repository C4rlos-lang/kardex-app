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

    <!-- Botón transferir -->
<button class="btn-transferir" @click="panelAbierto = true">
  📦 Transferir
</button>

<!-- Panel lateral derecho -->
<div class="overlay" v-if="panelAbierto" @click.self="panelAbierto = false"></div>
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
    <select v-model="transferencia.producto_id">
      <option value="">Selecciona un producto...</option>
      <option v-for="p in productos" :key="p.id" :value="p.id">
        {{ p.nombre }} (Stock: {{ p.stock }})
      </option>
    </select>
  </div>

  <div class="campo">
    <label>Cantidad</label>
    <input v-model="transferencia.cantidad" type="number" min="1" placeholder="Ej: 10" />
  </div>

  <button class="btn-confirmar" @click="confirmarTransferencia" :disabled="cargandoTransferencia">
    {{ cargandoTransferencia ? 'Transfiriendo...' : '✅ Confirmar Transferencia' }}
  </button>

  <p v-if="mensajeTransferencia" :class="exitoTransferencia ? 'exito' : 'error'">
    {{ mensajeTransferencia }}
  </p>
</div>

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
        </tr>
        <tr v-if="productosPaginados.length === 0">
          <td colspan="8" style="text-align:center; color:#888;">
            No se encontraron productos
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Paginación -->
    <div class="paginacion" v-if="totalPaginas > 1">
      <button @click="paginaAnterior" :disabled="paginaActual === 1">← Anterior</button>
      
      <span v-for="pagina in totalPaginas" :key="pagina">
        <button 
          @click="irAPagina(pagina)" 
          :class="pagina === paginaActual ? 'activa' : ''"
        >
          {{ pagina }}
        </button>
      </span>

      <button @click="paginaSiguiente" :disabled="paginaActual === totalPaginas">Siguiente →</button>
      
      <span class="info">
        Página {{ paginaActual }} de {{ totalPaginas }} 
        ({{ productosFiltrados.length }} productos)
      </span>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

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
      transferencia: {
        almacen_id: '',
        producto_id: '',
        cantidad: 0
      },
      mensajeTransferencia: '',
      exitoTransferencia: false,
      cargandoTransferencia: false
    }   // ← este cierra el return
  },
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
    busqueda() {
      this.paginaActual = 1
    }
  },
  methods: {
    irAPagina(pagina) {
      this.paginaActual = pagina
    },
    paginaAnterior() {
      if (this.paginaActual > 1) this.paginaActual--
    },
    paginaSiguiente() {
      if (this.paginaActual < this.totalPaginas) this.paginaActual++
    }
  },
  async mounted() {
    try {
      const { data } = await axios.get('https://kardex-app.onrender.com/productos')
      this.productos = data
    } catch (error) {
      console.error('Error cargando productos', error)
    }
    this.cargando = false
  }
}
</script>

<style scoped>
h1 { margin-bottom: 16px; color: #1B3A6B; }
.buscador { margin-bottom: 20px; }
.buscador input {
  width: 100%;
  max-width: 500px;
  padding: 10px 14px;
  font-size: 15px;
  border: 1px solid #ccc;
  border-radius: 8px;
}
.btn-transferir {
  margin-bottom: 16px;
  padding: 10px 20px;
  background: #2E5FA3;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 15px;
}
.overlay {
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
  background: rgba(0,0,0,0.3);
  z-index: 100;
}
.panel {
  position: fixed;
  top: 0; right: -450px;
  width: 450px;
  height: 100%;
  background: white;
  box-shadow: -4px 0 20px rgba(0,0,0,0.15);
  z-index: 101;
  transition: right 0.3s ease;
  display: flex;
  flex-direction: column;
}
.panel.abierto {
  right: 0;
}
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #eee;
  background: #1B3A6B;
  color: white;
}
.panel-header h2 {
  margin: 0;
  font-size: 18px;
}
.cerrar {
  background: none;
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
}
.panel-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}
table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
thead { background: #1B3A6B; color: white; }
th, td { padding: 12px 16px; text-align: left; font-size: 14px; }
tbody tr:nth-child(even) { background: #F2F4F7; }
tbody tr:hover { background: #D6E4F7; }
.foto {
  width: 50px;
  height: 50px;
  object-fit: cover;
  border-radius: 4px;
}
.paginacion {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 20px;
  flex-wrap: wrap;
}
.paginacion button {
  padding: 6px 12px;
  border: 1px solid #ccc;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}
.paginacion button:hover {
  background: #D6E4F7;
}
.paginacion button.activa {
  background: #1B3A6B;
  color: white;
  border-color: #1B3A6B;
}
.paginacion button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.info {
  margin-left: 10px;
  font-size: 13px;
  color: #888;
}
.campo {
  margin-bottom: 16px;
}
.campo label {
  display: block;
  font-size: 13px;
  color: #555;
  margin-bottom: 6px;
}
.campo input, .campo select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 14px;
}
.campo input:disabled {
  background: #f5f5f5;
  color: #888;
}
.btn-confirmar {
  width: 100%;
  padding: 12px;
  background: #1E7E50;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 15px;
  margin-top: 8px;
}
.btn-confirmar:disabled { background: #ccc; }
.exito { color: #1E7E50; margin-top: 12px; }
.error { color: red; margin-top: 12px; }
</style>