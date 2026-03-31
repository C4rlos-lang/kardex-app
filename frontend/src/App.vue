<template>
  <div class="container">
    <h1>Crear Producto</h1>

    <form @submit.prevent="crearProducto">
      <div>
        <label>SKU</label>
        <input v-model="form.sku" type="text" placeholder="Ej: PROD-001" />
      </div>
      <div>
        <label>Nombre</label>
        <input v-model="form.nombre" type="text" placeholder="Ej: Camisa" />
      </div>
      <div>
        <label>Categoría</label>
        <input v-model="form.categoria" type="text" placeholder="Ej: Ropa" />
      </div>
      <div>
        <label>Proveedor</label>
        <input v-model="form.proveedor" type="text" placeholder="Ej: Proveedor SA" />
      </div>
      <div>
        <label>Precio</label>
        <input v-model="form.precio" type="number" placeholder="Ej: 25000" />
      </div>
      <div>
        <label>Stock</label>
        <input v-model="form.stock" type="number" placeholder="Ej: 100" />
      </div>
      <button type="submit">Guardar</button>
    </form>

    <p v-if="mensaje" :class="exito ? 'exito' : 'error'">{{ mensaje }}</p>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      form: {
        sku: '',
        nombre: '',
        categoria: '',
        proveedor: '',
        precio: 0,
        stock: 0,
        foto_url: null
      },
      mensaje: '',
      exito: false
    }
  },
  methods: {
    async crearProducto() {
      try {
        await axios.post('https://kardex-app.onrender.com/productos', this.form)
        this.mensaje = '¡Producto creado exitosamente!'
        this.exito = true
        this.form = { sku: '', nombre: '', categoria: '', proveedor: '', precio: 0, stock: 0, foto_url: null }
      } catch (error) {
        this.mensaje = 'Error al crear el producto'
        this.exito = false
      }
    }
  }
}
</script>

<style>
.container {
  max-width: 450px;
  margin: 50px auto;
  font-family: Arial;
}
input {
  display: block;
  width: 100%;
  margin: 8px 0 16px;
  padding: 8px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
button {
  width: 100%;
  padding: 10px;
  background: #42b883;
  color: white;
  border: none;
  cursor: pointer;
  font-size: 16px;
  border-radius: 4px;
}
.exito { color: green; }
.error { color: red; }
</style>