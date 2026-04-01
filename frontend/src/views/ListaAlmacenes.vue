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
      almacenes: [],
      cargando: true
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
thead {
  background: #1B3A6B;
  color: white;
}
th, td {
  padding: 12px 16px;
  text-align: left;
  font-size: 14px;
}
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
</style>