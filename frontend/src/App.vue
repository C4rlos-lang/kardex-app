<template>
  <div class="container">
    <h1>Crear Producto</h1>

    <form @submit.prevent="crearProducto">
      <div>
        <label>Nombre</label>
        <input v-model="nombre" type="text" placeholder="Ej: Arroz" />
      </div>
      <div>
        <label>Stock</label>
        <input v-model="stock" type="number" placeholder="Ej: 100" />
      </div>
      <button type="submit">Guardar</button>
    </form>

    <p v-if="mensaje">{{ mensaje }}</p>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      nombre: '',
      stock: 0,
      mensaje: ''
    }
  },
  methods: {
    async crearProducto() {
      try {
        await axios.post('http://localhost:8000/productos', {
          nombre: this.nombre,
          stock: this.stock
        })
        this.mensaje = '¡Producto creado exitosamente!'
        this.nombre = ''
        this.stock = 0
      } catch (error) {
        this.mensaje = 'Error al crear el producto'
      }
    }
  }
}
</script>

<style>
.container {
  max-width: 400px;
  margin: 50px auto;
  font-family: Arial;
}
input {
  display: block;
  width: 100%;
  margin: 8px 0 16px;
  padding: 8px;
  font-size: 16px;
}
button {
  padding: 10px 20px;
  background: #42b883;
  color: white;
  border: none;
  cursor: pointer;
  font-size: 16px;
}
</style>