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
        <label>Marca</label>
        <input v-model="form.marca" type="text" placeholder="Ej: Nike" />
      </div>
      <div>
        <label>Precio</label>
        <input v-model="form.precio" type="number" placeholder="Ej: 25000" />
      </div>
      <div>
        <label>Stock</label>
        <input v-model="form.stock" type="number" placeholder="Ej: 100" />
      </div>
      <div>
        <label>Foto del producto</label>
        <input type="file" accept="image/*" @change="seleccionarFoto" />
        <img v-if="preview" :src="preview" style="width:100%; margin-top:8px; border-radius:4px;" />
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
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  'https://thcdadlejpdhaaekyost.supabase.co',
  'sb_publishable_d6fIfDVkO3SFZW4PBNr5Bw_6qgg9PKN'
)

export default {
  data() {
    return {
      form: {
        sku: '',
        nombre: '',
        categoria: '',
        proveedor: '',
        marca: '',
        precio: 0,
        stock: 0,
        foto_url: null
      },
      fotoArchivo: null,
      preview: null,
      mensaje: '',
      exito: false,
      cargando: false
    }
  },
  methods: {
    seleccionarFoto(event) {
      const archivo = event.target.files[0]
      if (archivo) {
        this.fotoArchivo = archivo
        this.preview = URL.createObjectURL(archivo)
      }
    },
    async crearProducto() {
      this.cargando = true
      try {
        // Subir foto a Supabase Storage
        if (this.fotoArchivo) {
          const nombre = `${Date.now()}_${this.fotoArchivo.name}`
          const { error } = await supabase.storage
            .from('fotos-productos')
            .upload(nombre, this.fotoArchivo)

          if (error) throw error

          const { data } = supabase.storage
            .from('fotos-productos')
            .getPublicUrl(nombre)

          this.form.foto_url = data.publicUrl
        }

        // Guardar producto en FastAPI
        await axios.post('https://kardex-app.onrender.com/productos', this.form)
        this.mensaje = '¡Producto creado exitosamente!'
        this.exito = true
        this.form = { sku: '', nombre: '', categoria: '', proveedor: '', marca: '', precio: 0, stock: 0, foto_url: null }
        this.preview = null
        this.fotoArchivo = null
      } catch (error) {
        this.mensaje = 'Error al crear el producto'
        this.exito = false
      }
      this.cargando = false
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
button:disabled {
  background: #ccc;
  cursor: not-allowed;
}
.exito { color: green; }
.error { color: red; }
</style>