<template>
  <div>
    <h1>Crear Producto</h1>

    <form @submit.prevent="crearProducto">
      <div class="fila2">
        <div class="grupo">
          <label>SKU</label>
          <input v-model="form.sku" type="text" placeholder="Ej: NK-001" />
        </div>
        <div class="grupo">
          <label>Nombre</label>
          <input v-model="form.nombre" type="text" placeholder="Ej: Nike Air Max" />
        </div>
      </div>

      <div class="fila3">
        <div class="grupo">
          <label>Categoría</label>
          <input v-model="form.categoria" type="text" placeholder="Ej: Calzado" />
        </div>
        <div class="grupo">
          <label>Marca</label>
          <input v-model="form.marca" type="text" placeholder="Ej: Nike" />
        </div>
        <div class="grupo">
          <label>Precio</label>
          <input v-model="form.precio" type="number" placeholder="Ej: 250000" />
        </div>
      </div>

      <div class="fila2">
        <div class="grupo">
          <label>Proveedor</label>
          <input v-model="form.proveedor" type="text" placeholder="Ej: Proveedor SA" />
        </div>
      </div>

      <div class="grupo">
        <label>Foto del producto</label>
        <input type="file" accept="image/*" @change="seleccionarFoto" />
        <img v-if="preview" :src="preview" style="width:120px; margin-top:8px; border-radius:6px;" />
      </div>

      <!-- Género -->
      <div class="grupo">
        <label>Género</label>
        <div class="genero-wrap">
          <div
            v-for="g in generos" :key="g.valor"
            class="genero-btn"
            :class="{ activo: form.genero === g.valor }"
            @click="form.genero = g.valor"
          >
            {{ g.label }}
          </div>
        </div>
      </div>

      <!-- Tallas -->
      <div class="seccion-tallas" v-if="form.genero">
        <p class="seccion-titulo">
          Tallas y unidades
          <span class="badge">{{ form.genero }}</span>
        </p>
        <table class="tabla-tallas">
          <thead>
            <tr>
              <th>Talla</th>
              <th>Unidades</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="talla in tallasActuales" :key="talla">
              <td class="talla-label">{{ talla }}</td>
              <td>
                <input
                  class="talla-input"
                  type="number"
                  min="0"
                  placeholder="0"
                  v-model.number="unidadesPorTalla[talla]"
                />
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <button type="submit" :disabled="cargando">
        {{ cargando ? 'Guardando...' : 'Guardar producto' }}
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

const TALLAS = {
  hombre: [6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10, 10.5, 11],
  mujer:  [5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5],
  nino:   [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]
}

export default {
  data() {
    return {
      form: {
        sku: '', nombre: '', categoria: '', marca: '',
        precio: 0, stock: 0, proveedor: '', foto_url: null,
        genero: ''
      },
      generos: [
        { valor: 'hombre', label: 'Hombre' },
        { valor: 'mujer',  label: 'Mujer'  },
        { valor: 'nino',   label: 'Niño'   }
      ],
      unidadesPorTalla: {},
      fotoArchivo: null,
      preview: null,
      mensaje: '',
      exito: false,
      cargando: false
    }
  },
  computed: {
    tallasActuales() {
      return TALLAS[this.form.genero] || []
    }
  },
  watch: {
    'form.genero'() {
      this.unidadesPorTalla = {}
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
        // Subir foto
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

        // Crear producto
        const res = await axios.post('https://kardex-app.onrender.com/productos', {
          sku: this.form.sku,
          nombre: this.form.nombre,
          categoria: this.form.categoria,
          marca: this.form.marca,
          precio: this.form.precio,
          stock: this.form.stock,
          proveedor: this.form.proveedor,
          foto_url: this.form.foto_url,
          genero: this.form.genero
        })

        const productoId = res.data.id

        // Guardar tallas
        const tallas = this.tallasActuales
          .filter(t => this.unidadesPorTalla[t] > 0)
          .map(t => ({
            producto_id: productoId,
            genero: this.form.genero,
            talla: String(t),
            unidades: this.unidadesPorTalla[t]
          }))

        if (tallas.length > 0) {
          await axios.post('https://kardex-app.onrender.com/producto-tallas', tallas)
        }

        this.mensaje = '¡Producto creado exitosamente!'
        this.exito = true
        this.form = { sku: '', nombre: '', categoria: '', marca: '', precio: 0, stock: 0, proveedor: '', foto_url: null, genero: '' }
        this.unidadesPorTalla = {}
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

<style scoped>
h1 { margin-bottom: 24px; color: #1B3A6B; }
form { max-width: 600px; }
.grupo { margin-bottom: 16px; }
label { font-size: 13px; color: #555; display: block; margin-bottom: 6px; }
input, select {
  display: block; width: 100%;
  padding: 8px 12px; font-size: 14px;
  border: 1px solid #ccc; border-radius: 6px;
}
.fila2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.fila3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }
.genero-wrap { display: flex; gap: 12px; }
.genero-btn {
  flex: 1; padding: 10px; text-align: center;
  border: 1px solid #ccc; border-radius: 6px;
  cursor: pointer; font-size: 14px; color: #555;
}
.genero-btn.activo {
  border: 2px solid #1B3A6B;
  background: #D6E4F7; color: #1B3A6B; font-weight: 500;
}
.seccion-tallas { margin-top: 24px; }
.seccion-titulo {
  font-size: 14px; font-weight: 500;
  color: #1B3A6B; margin-bottom: 12px;
  padding-bottom: 8px; border-bottom: 1px solid #eee;
}
.badge {
  display: inline-block; font-size: 11px;
  padding: 2px 8px; border-radius: 6px;
  background: #D6E4F7; color: #1B3A6B; margin-left: 8px;
}
.tabla-tallas { width: 100%; border-collapse: collapse; }
.tabla-tallas th {
  font-size: 12px; color: #888;
  padding: 6px 8px; text-align: left;
  border-bottom: 1px solid #eee;
}
.tabla-tallas td { padding: 6px 8px; border-bottom: 1px solid #eee; }
.talla-label { font-size: 14px; font-weight: 500; color: #333; }
.talla-input { width: 80px !important; }
button {
  margin-top: 24px; width: 100%; padding: 12px;
  background: #1B3A6B; color: white;
  border: none; border-radius: 6px;
  font-size: 15px; cursor: pointer;
}
button:disabled { background: #ccc; }
.exito { color: green; margin-top: 12px; }
.error { color: red; margin-top: 12px; }
</style>