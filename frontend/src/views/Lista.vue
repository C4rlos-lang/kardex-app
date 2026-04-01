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
        </tr>
      </thead>
      <tbody>
        <tr v-for="producto in productosFiltrados" :key="producto.id">
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
        <tr v-if="productosFiltrados.length === 0">
          <td colspan="8" style="text-align:center; color:#888;">
            No se encontraron productos
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      productos: [],
      busqueda: '',
      cargando: true
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
.buscador {
  margin-bottom: 20px;
}
.buscador input {
  width: 100%;
  max-width: 500px;
  padding: 10px 14px;
  font-size: 15px;
  border: 1px solid #ccc;
  border-radius: 8px;
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
</style>