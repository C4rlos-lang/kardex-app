<template>
  <div>
    <h1>Crear Almacén</h1>

    <form @submit.prevent="crearAlmacen">
      <div>
        <label>Nombre del almacén</label>
        <input v-model="form.nombre" type="text" placeholder="Ej: Almacén Norte" />
      </div>
      <div>
        <label>Dirección</label>
        <input v-model="form.direccion" type="text" placeholder="Ej: Calle 123" />
      </div>
      <div>
        <label>Ciudad</label>
        <input v-model="form.ciudad" type="text" placeholder="Ej: Bogotá" />
      </div>
      <div>
        <label>Responsable</label>
        <input v-model="form.responsable" type="text" placeholder="Ej: Juan Pérez" />
      </div>
      <div>
        <label>Estado</label>
        <select v-model="form.estado">
          <option value="activo">Activo</option>
          <option value="inactivo">Inactivo</option>
        </select>
      </div>
      <button type="submit" :disabled="cargando">
        {{ cargando ? 'Guardando...' : 'Guardar' }}
      </button>
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
        nombre: '',
        direccion: '',
        ciudad: '',
        responsable: '',
        estado: 'activo'
      },
      mensaje: '',
      exito: false,
      cargando: false
    }
  },
  methods: {
    async crearAlmacen() {
      this.cargando = true
      try {
        await axios.post('https://kardex-app.onrender.com/almacenes', this.form)
        this.mensaje = '¡Almacén creado exitosamente!'
        this.exito = true
        this.form = { nombre: '', direccion: '', ciudad: '', responsable: '', estado: 'activo' }
      } catch (error) {
        this.mensaje = 'Error al crear el almacén'
        this.exito = false
      }
      this.cargando = false
    }
  }
}
</script>

<style scoped>
h1 { margin-bottom: 24px; color: #1B3A6B; }
form { max-width: 450px; }
label { font-size: 14px; color: #555; }
input, select {
  display: block;
  width: 100%;
  margin: 6px 0 16px;
  padding: 8px;
  font-size: 15px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
button {
  width: 100%;
  padding: 10px;
  background: #1B3A6B;
  color: white;
  border: none;
  cursor: pointer;
  font-size: 16px;
  border-radius: 4px;
}
button:disabled { background: #ccc; }
.exito { color: green; margin-top: 12px; }
.error { color: red; margin-top: 12px; }
</style>