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
          <th>Talla</th>
          <th>Género</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="almacen in almacenes" :key="almacen.id">
          <td>{{ almacen.nombre }}</td>
          <td>{{ almacen.direccion }}</td>
          <td>{{ almacen.ciudad }}</td>
          <td>{{ almacen.responsable }}</td>
          <td>{{ item.talla }}</td>
          <td>{{ item.genero }}</td>
          <td>
            <span :class="almacen.estado === 'activo' ? 'activo' : 'inactivo'">
              {{ almacen.estado }}
            </span>
          </td>
          <td>
            <button class="btn-ver" @click="verInventario(almacen)">
              👁️ Ver inventario
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Overlay -->
    <div class="overlay" v-if="panelAbierto" @click.self="panelAbierto = false"></div>

    <!-- Panel lateral derecho -->
    <div class="panel" :class="{ abierto: panelAbierto }">
      <div class="panel-header">
        <h2>📦 {{ almacenSeleccionado?.nombre }}</h2>
        <button class="cerrar" @click="panelAbierto = false">✕</button>
      </div>
      <div class="panel-body">
        <p v-if="cargandoInventario">Cargando inventario...</p>
        <p v-else-if="inventario.length === 0">Sin productos en este almacén.</p>
        <table v-else class="tabla-inventario">
          <thead>
            <tr>
              <th>Foto</th>
              <th>SKU</th>
              <th>Nombre</th>
              <th>Categoría</th>
              <th>Marca</th>
              <th>Proveedor</th>
              <th>Precio</th>
              <th>Stock</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in inventario" :key="item.id">
              <td>
                <img v-if="item.foto_url" :src="item.foto_url" class="foto" />
                <span v-else>Sin foto</span>
              </td>
              <td>{{ item.sku }}</td>
              <td>{{ item.nombre }}</td>
              <td>{{ item.categoria }}</td>
              <td>{{ item.marca }}</td>
              <td>{{ item.proveedor }}</td>
              <td>${{ item.precio }}</td>
              <td>{{ item.stock }}</td>
            </tr>
          </tbody>
        </table>
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
      cargandoInventario: false
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
.activo {
  background: #d4edda;
  color: #1E7E50;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 13px;
}
.inactivo {
  background: #f8d7da;
  color: #c0392b;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 13px;
}
.btn-ver {
  padding: 6px 12px;
  background: #2E5FA3;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
}
.btn-ver:hover { background: #1B3A6B; }
.overlay {
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
  background: rgba(0,0,0,0.3);
  z-index: 100;
}
.panel {
  position: fixed;
  top: 0; right: -700px;
  width: 700px;
  height: 100%;
  background: white;
  box-shadow: -4px 0 20px rgba(0,0,0,0.15);
  z-index: 101;
  transition: right 0.3s ease;
  display: flex;
  flex-direction: column;
}
.panel.abierto { right: 0; }
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: #1B3A6B;
  color: white;
}
.panel-header h2 { margin: 0; font-size: 18px; }
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
.tabla-inventario { margin-top: 0; }
.foto {
  width: 40px;
  height: 40px;
  object-fit: cover;
  border-radius: 4px;
}
</style>