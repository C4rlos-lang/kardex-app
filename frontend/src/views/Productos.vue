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
          <select v-model="form.categoria">
            <option value="">Selecciona...</option>
            <option v-for="c in maestras.categoria" :key="c.id" :value="c.valor">
              {{ c.valor }}
            </option>
          </select>
        </div>
        <div class="grupo">
          <label>Marca</label>
          <select v-model="form.marca">
            <option value="">Selecciona...</option>
            <option v-for="m in maestras.marca" :key="m.id" :value="m.valor">
              {{ m.valor }}
            </option>
          </select>
        </div>
        <div class="grupo">
          <label>Precio</label>
          <input v-model="form.precio" type="number" placeholder="Ej: 250000" />
        </div>
      </div>

      <div class="fila2">
        <div class="grupo">
          <label>Proveedor</label>
          <select v-model="form.proveedor">
            <option value="">Selecciona...</option>
            <option v-for="p in maestras.proveedor" :key="p.id" :value="p.valor">
              {{ p.valor }}
            </option>
          </select>
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
            v-for="g in maestras.genero" :key="g.id"
            class="genero-btn"
            :class="{ activo: form.genero === g.valor }"
            @click="seleccionarGenero(g.valor)"
          >
            {{ g.valor }}
          </div>
        </div>
      </div>

      <!-- Tallas -->
      <div class="seccion-tallas" v-if="form.genero && tallasActuales.length">
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

      <div v-if="form.genero && tallasActuales.length === 0" class="aviso">
        ⚠️ No hay tallas configuradas para <strong>{{ form.genero }}</strong>. Ve a Maestras → Tallas para agregarlas.
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

const API = 'https://kardex-app.onrender.com'

export default {
  data() {
    return {
      form: {
        sku: '', nombre: '', categoria: '', marca: '',
        precio: 0, stock: 0, proveedor: '', foto_url: null,
        genero: ''
      },
      maestras: {
        categoria: [],
        marca: [],
        proveedor: [],
        genero: [],
        talla: []
      },
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
      if (!this.form.genero) return []
      return this.maestras.talla
        .filter(t => {
          if (!t.genero_relacionado) return true
          return t.genero_relacionado.toLowerCase() === this.form.genero.toLowerCase()
        })
        .map(t => t.valor)
        .sort((a, b) => parseFloat(a) - parseFloat(b))
    }
  },
  watch: {
    'form.genero'() {
      this.unidadesPorTalla = {}
    }
  },
  methods: {
    seleccionarGenero(valor) {
      this.form.genero = valor
    },
    seleccionarFoto(event) {
      const archivo = event.target.files[0]
      if (archivo) {
        this.fotoArchivo = archivo
        this.preview = URL.createObjectURL(archivo)
      }
    },
    async cargarMaestras() {
      try {
        const tipos = ['categoria', 'marca', 'proveedor', 'genero', 'talla']
        const resultados = await Promise.all(
          tipos.map(t => axios.get(`${API}/maestras/${t}`))
        )
        tipos.forEach((t, i) => {
          this.maestras[t] = resultados[i].data.filter(m => m.activo)
        })
      } catch (error) {
        console.error('Error cargando maestras', error)
      }
    },
    async crearProducto() {
      this.cargando = true
      try {
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

        const res = await axios.post(`${API}/productos`, {
          sku: this.form.sku,
          nombre: this.form.nombre,
          categoria: this.form.categoria,
          marca: this.form.marca,
          precio: this.form.precio,
          stock: Object.values(this.unidadesPorTalla).reduce((a, b) => a + (b || 0), 0),
          proveedor: this.form.proveedor,
          foto_url: this.form.foto_url,
          genero: this.form.genero
        })

        const productoId = res.data.id

        const tallas = this.tallasActuales
          .filter(t => this.unidadesPorTalla[t] > 0)
          .map(t => ({
            producto_id: productoId,
            genero: this.form.genero,
            talla: String(t),
            unidades: this.unidadesPorTalla[t]
          }))

        if (tallas.length > 0) {
          await axios.post(`${API}/producto-tallas`, tallas)
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
  },
  mounted() {
    this.cargarMaestras()
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
.genero-wrap { display: flex; gap: 12px; flex-wrap: wrap; }
.genero-btn {
  flex: 1; padding: 10px; text-align: center;
  border: 1px solid #ccc; border-radius: 6px;
  cursor: pointer; font-size: 14px; color: #555;
  min-width: 80px;
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
.aviso {
  margin-top: 16px; padding: 12px 16px;
  background: #fff3cd; border-radius: 8px;
  font-size: 13px; color: #856404;
  border-left: 4px solid #ffc107;
}
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