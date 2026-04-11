<template>
  <div>
    <h1>⚙️ Maestras</h1>

    <!-- Pestañas -->
    <div class="tabs">
      <button
        v-for="t in tipos" :key="t.key"
        class="tab"
        :class="{ activo: tipoActivo === t.key }"
        @click="cambiarTipo(t.key)"
      >
        {{ t.label }}
      </button>
    </div>

    <!-- ── SECCIÓN MAESTRAS SIMPLES ─────────────────────────────── -->
    <div v-if="esMaestraSimple">

      <div class="form-wrap">
        <input
          v-model="nuevoValor"
          type="text"
          :placeholder="`Agregar ${tipoLabel}...`"
          @keyup.enter="agregar"
        />
        <button class="btn-agregar" @click="agregar" :disabled="!nuevoValor.trim()">
          + Agregar
        </button>
      </div>

      <p v-if="mensaje" :class="exito ? 'exito' : 'error'">{{ mensaje }}</p>

      <p v-if="cargando">Cargando...</p>
      <div v-else class="lista">
        <div v-if="items.length === 0" class="vacio">
          No hay {{ tipoLabel }} registradas. Agrega la primera arriba.
        </div>
        <div v-for="item in items" :key="item.id" class="item-row">
          <div class="item-info">
            <span v-if="!item.editando" class="item-valor">{{ item.valor }}</span>
            <input
              v-else v-model="item.valorTemp" type="text"
              class="input-editar" @keyup.enter="guardarEdicion(item)"
            />
            <span :class="item.activo ? 'badge-activo' : 'badge-inactivo'">
              {{ item.activo ? 'Activo' : 'Inactivo' }}
            </span>
          </div>
          <div class="item-acciones">
            <button v-if="!item.editando" class="btn-editar" @click="iniciarEdicion(item)">✏️</button>
            <button v-else class="btn-guardar" @click="guardarEdicion(item)">✅</button>
            <button v-if="!item.editando" class="btn-toggle" @click="toggleActivo(item)">
              {{ item.activo ? '🔴 Desactivar' : '🟢 Activar' }}
            </button>
            <button class="btn-eliminar" @click="eliminar(item)">🗑️</button>
          </div>
        </div>
      </div>
    </div>

    <!-- ── SECCIÓN CREAR PRODUCTO ──────────────────────────────── -->
    <div v-else-if="tipoActivo === 'producto'">
      <p v-if="mensajeProducto" :class="exitoProducto ? 'exito' : 'error'">{{ mensajeProducto }}</p>
      <form @submit.prevent="crearProducto" class="form-seccion">
        <div class="fila2">
          <div class="grupo">
            <label>SKU <span class="badge-auto">Autogenerado</span></label>
            <input v-model="formProducto.sku" type="text" placeholder="Se genera al seleccionar marca" readonly class="input-readonly" />
          </div>
          <div class="grupo">
            <label>Nombre</label>
            <input v-model="formProducto.nombre" type="text" placeholder="Ej: Nike Air Max" />
          </div>
        </div>
        <div class="fila3">
          <div class="grupo">
            <label>Categoría</label>
            <select v-model="formProducto.categoria">
              <option value="">Selecciona...</option>
              <option v-for="c in maestras.categoria" :key="c.id" :value="c.valor">{{ c.valor }}</option>
            </select>
          </div>
          <div class="grupo">
            <label>Marca</label>
            <select v-model="formProducto.marca" @change="generarSKU">
              <option value="">Selecciona...</option>
              <option v-for="m in maestras.marca" :key="m.id" :value="m.valor">{{ m.valor }}</option>
            </select>
          </div>
          <div class="grupo">
            <label>Precio de compra</label>
            <input v-model="formProducto.precio" type="number" placeholder="Ej: 250000" />
          </div>
        </div>
        <div class="fila2">
          <div class="grupo">
            <label>Proveedor</label>
            <select v-model="formProducto.proveedor">
              <option value="">Selecciona...</option>
              <option v-for="p in maestras.proveedor" :key="p.id" :value="p.valor">{{ p.valor }}</option>
            </select>
          </div>
        </div>
        <div class="grupo">
          <label>Foto del producto</label>
          <input type="file" accept="image/*" @change="seleccionarFoto" />
          <img v-if="preview" :src="preview" style="width:120px; margin-top:8px; border-radius:6px;" />
        </div>
        <div class="grupo">
          <label>Género</label>
          <div class="genero-wrap">
            <div
              v-for="g in maestras.genero" :key="g.id"
              class="genero-btn"
              :class="{ activo: formProducto.genero === g.valor }"
              @click="formProducto.genero = g.valor; unidadesPorTalla = {}"
            >
              {{ g.valor }}
            </div>
          </div>
        </div>
        <div class="seccion-tallas" v-if="formProducto.genero && tallasActuales.length">
          <p class="seccion-titulo">
            Tallas y unidades
            <span class="badge-genero">{{ formProducto.genero }}</span>
          </p>
          <table class="tabla-tallas">
            <thead>
              <tr><th>Talla</th><th>Unidades</th></tr>
            </thead>
            <tbody>
              <tr v-for="talla in tallasActuales" :key="talla">
                <td class="talla-label">{{ talla }}</td>
                <td>
                  <input class="talla-input" type="number" min="0" placeholder="0" v-model.number="unidadesPorTalla[talla]" />
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="formProducto.genero && tallasActuales.length === 0" class="aviso">
          ⚠️ No hay tallas configuradas para <strong>{{ formProducto.genero }}</strong>. Agrégalas en la pestaña Tallas.
        </div>
        <button type="submit" class="btn-submit" :disabled="cargandoProducto">
          {{ cargandoProducto ? 'Guardando...' : '✅ Guardar producto' }}
        </button>
      </form>
    </div>

    <!-- ── SECCIÓN CREAR ALMACÉN ──────────────────────────────── -->
    <div v-else-if="tipoActivo === 'almacen'">
      <p v-if="mensajeAlmacen" :class="exitoAlmacen ? 'exito' : 'error'">{{ mensajeAlmacen }}</p>
      <form @submit.prevent="crearAlmacen" class="form-seccion">
        <div class="grupo">
          <label>Nombre del almacén</label>
          <input v-model="formAlmacen.nombre" type="text" placeholder="Ej: Almacén Norte" />
        </div>
        <div class="grupo">
          <label>Dirección</label>
          <input v-model="formAlmacen.direccion" type="text" placeholder="Ej: Calle 123" />
        </div>
        <div class="fila2">
          <div class="grupo">
            <label>Ciudad</label>
            <input v-model="formAlmacen.ciudad" type="text" placeholder="Ej: Bogotá" />
          </div>
          <div class="grupo">
            <label>Responsable</label>
            <input v-model="formAlmacen.responsable" type="text" placeholder="Ej: Juan Pérez" />
          </div>
        </div>
        <div class="grupo">
          <label>Estado</label>
          <select v-model="formAlmacen.estado">
            <option value="activo">Activo</option>
            <option value="inactivo">Inactivo</option>
          </select>
        </div>
        <button type="submit" class="btn-submit" :disabled="cargandoAlmacen">
          {{ cargandoAlmacen ? 'Guardando...' : '✅ Guardar almacén' }}
        </button>
      </form>
    </div>

  </div>
</template>

<script>
import axios from 'axios'
import { createClient } from '@supabase/supabase-js'

const API = import.meta.env.VITE_API_URL
const supabase = createClient(
  'https://thcdadlejpdhaaekyost.supabase.co',
  'sb_publishable_d6fIfDVkO3SFZW4PBNr5Bw_6qgg9PKN'
)

export default {
  data() {
    return {
      tipoActivo: 'categoria',
      tipos: [
        { key: 'categoria',    label: 'Categorías' },
        { key: 'marca',        label: 'Marcas' },
        { key: 'proveedor',    label: 'Proveedores' },
        { key: 'genero',       label: 'Géneros' },
        { key: 'talla',        label: 'Tallas' },
        { key: 'metodo_pago',  label: 'Métodos de pago' },
        { key: 'producto',     label: 'Producto' },
        { key: 'almacen',      label: 'Almacén' },
      ],
      // Maestras simples
      items: [],
      cargando: false,
      nuevoValor: '',
      mensaje: '',
      exito: false,
      // Producto
      formProducto: {
        sku: '', nombre: '', categoria: '', marca: '',
        precio: 0, proveedor: '', foto_url: null, genero: ''
      },
      maestras: { categoria: [], marca: [], proveedor: [], genero: [], talla: [] },
      unidadesPorTalla: {},
      fotoArchivo: null,
      preview: null,
      mensajeProducto: '',
      exitoProducto: false,
      cargandoProducto: false,
      // Almacén
      formAlmacen: {
        nombre: '', direccion: '', ciudad: '', responsable: '', estado: 'activo'
      },
      mensajeAlmacen: '',
      exitoAlmacen: false,
      cargandoAlmacen: false,
    }
  },
  computed: {
    tipoLabel() {
      return this.tipos.find(t => t.key === this.tipoActivo)?.label || ''
    },
    esMaestraSimple() {
      return !['producto', 'almacen'].includes(this.tipoActivo)
    },
    tallasActuales() {
      if (!this.formProducto.genero) return []
      return this.maestras.talla
        .filter(t => !t.genero_relacionado || t.genero_relacionado.toLowerCase() === this.formProducto.genero.toLowerCase())
        .map(t => t.valor)
        .sort((a, b) => parseFloat(a) - parseFloat(b))
    }
  },
  methods: {
    async cambiarTipo(tipo) {
      this.tipoActivo = tipo
      this.nuevoValor = ''
      this.mensaje = ''
      if (this.esMaestraSimple) await this.cargar()
      if (tipo === 'producto') await this.cargarMaestras()
    },
    async cargar() {
      this.cargando = true
      try {
        const { data } = await axios.get(`${API}/maestras/${this.tipoActivo}`)
        this.items = data.map(i => ({ ...i, editando: false, valorTemp: i.valor }))
      } catch (error) {
        console.error('Error', error)
      }
      this.cargando = false
    },
    async cargarMaestras() {
      try {
        const tipos = ['categoria', 'marca', 'proveedor', 'genero', 'talla']
        const resultados = await Promise.all(tipos.map(t => axios.get(`${API}/maestras/${t}`)))
        tipos.forEach((t, i) => { this.maestras[t] = resultados[i].data.filter(m => m.activo) })
      } catch (error) {
        console.error('Error cargando maestras', error)
      }
    },
    async generarSKU() {
      if (!this.formProducto.marca) return
      try {
        const iniciales = this.formProducto.marca.replace(/[^a-zA-Z]/g, '').substring(0, 2).toUpperCase()
        const { data } = await axios.get(`${API}/productos`)
        const count = data.filter(p => p.marca && p.marca.toLowerCase() === this.formProducto.marca.toLowerCase()).length
        this.formProducto.sku = `${iniciales}-${String(count + 1).padStart(4, '0')}`
      } catch (error) {
        console.error('Error generando SKU', error)
      }
    },
    seleccionarFoto(event) {
      const archivo = event.target.files[0]
      if (archivo) {
        this.fotoArchivo = archivo
        this.preview = URL.createObjectURL(archivo)
      }
    },
    async crearProducto() {
      this.cargandoProducto = true
      try {
        if (this.fotoArchivo) {
          const nombre = `${Date.now()}_${this.fotoArchivo.name}`
          const { error } = await supabase.storage.from('fotos-productos').upload(nombre, this.fotoArchivo)
          if (error) throw error
          const { data } = supabase.storage.from('fotos-productos').getPublicUrl(nombre)
          this.formProducto.foto_url = data.publicUrl
        }
        const res = await axios.post(`${API}/productos`, {
          sku: this.formProducto.sku,
          nombre: this.formProducto.nombre,
          categoria: this.formProducto.categoria,
          marca: this.formProducto.marca,
          precio: this.formProducto.precio,
          stock: Object.values(this.unidadesPorTalla).reduce((a, b) => a + (b || 0), 0),
          proveedor: this.formProducto.proveedor,
          foto_url: this.formProducto.foto_url,
          genero: this.formProducto.genero
        })
        const productoId = res.data.id
        const tallas = this.tallasActuales
          .filter(t => this.unidadesPorTalla[t] > 0)
          .map(t => ({ producto_id: productoId, genero: this.formProducto.genero, talla: String(t), unidades: this.unidadesPorTalla[t] }))
        if (tallas.length > 0) await axios.post(`${API}/producto-tallas`, tallas)
        this.mensajeProducto = '¡Producto creado exitosamente!'
        this.exitoProducto = true
        this.formProducto = { sku: '', nombre: '', categoria: '', marca: '', precio: 0, proveedor: '', foto_url: null, genero: '' }
        this.unidadesPorTalla = {}
        this.preview = null
        this.fotoArchivo = null
      } catch (error) {
        this.mensajeProducto = 'Error al crear el producto'
        this.exitoProducto = false
      }
      this.cargandoProducto = false
    },
    async crearAlmacen() {
      this.cargandoAlmacen = true
      try {
        await axios.post(`${API}/almacenes`, this.formAlmacen)
        this.mensajeAlmacen = '¡Almacén creado exitosamente!'
        this.exitoAlmacen = true
        this.formAlmacen = { nombre: '', direccion: '', ciudad: '', responsable: '', estado: 'activo' }
      } catch (error) {
        this.mensajeAlmacen = 'Error al crear el almacén'
        this.exitoAlmacen = false
      }
      this.cargandoAlmacen = false
    },
    async agregar() {
      if (!this.nuevoValor.trim()) return
      try {
        await axios.post(`${API}/maestras`, { tipo: this.tipoActivo, valor: this.nuevoValor.trim(), activo: true })
        this.mensaje = '¡Agregado exitosamente!'
        this.exito = true
        this.nuevoValor = ''
        await this.cargar()
        setTimeout(() => { this.mensaje = '' }, 2000)
      } catch (error) {
        this.mensaje = 'Error al agregar'
        this.exito = false
      }
    },
    iniciarEdicion(item) { item.valorTemp = item.valor; item.editando = true },
    async guardarEdicion(item) {
      try {
        await axios.put(`${API}/maestras/${item.id}`, { tipo: this.tipoActivo, valor: item.valorTemp, activo: item.activo })
        item.valor = item.valorTemp
        item.editando = false
        this.mensaje = '¡Actualizado!'
        this.exito = true
        setTimeout(() => { this.mensaje = '' }, 2000)
      } catch (error) {
        this.mensaje = 'Error al actualizar'
        this.exito = false
      }
    },
    async toggleActivo(item) {
      try {
        await axios.put(`${API}/maestras/${item.id}`, { tipo: this.tipoActivo, valor: item.valor, activo: !item.activo })
        item.activo = !item.activo
      } catch (error) {
        console.error('Error', error)
      }
    },
    async eliminar(item) {
      if (!confirm(`¿Eliminar "${item.valor}"?`)) return
      try {
        await axios.delete(`${API}/maestras/${item.id}`)
        await this.cargar()
        this.mensaje = 'Eliminado correctamente'
        this.exito = true
        setTimeout(() => { this.mensaje = '' }, 2000)
      } catch (error) {
        this.mensaje = 'Error al eliminar'
        this.exito = false
      }
    }
  },
  mounted() {
    this.cargar()
  }
}
</script>

<style scoped>
h1 { margin-bottom: 24px; color: #1B3A6B; }
.tabs { display: flex; gap: 8px; margin-bottom: 24px; flex-wrap: wrap; }
.tab { padding: 8px 16px; border: 1px solid #ccc; background: white; border-radius: 20px; cursor: pointer; font-size: 13px; color: #555; }
.tab.activo { background: #1B3A6B; color: white; border-color: #1B3A6B; }
.form-wrap { display: flex; gap: 8px; margin-bottom: 16px; }
.form-wrap input { flex: 1; padding: 10px 14px; border: 1px solid #ccc; border-radius: 8px; font-size: 14px; }
.btn-agregar { padding: 10px 20px; background: #1B3A6B; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; }
.btn-agregar:disabled { background: #ccc; cursor: not-allowed; }
.lista { display: flex; flex-direction: column; gap: 8px; }
.vacio { text-align: center; padding: 32px; color: #888; background: white; border-radius: 8px; font-size: 14px; }
.item-row { display: flex; justify-content: space-between; align-items: center; background: white; border: 1px solid #eee; border-radius: 8px; padding: 12px 16px; }
.item-info { display: flex; align-items: center; gap: 12px; }
.item-valor { font-size: 14px; color: #333; font-weight: 500; }
.input-editar { padding: 6px 10px; border: 1px solid #2E5FA3; border-radius: 6px; font-size: 14px; width: 200px; }
.badge-activo { background: #d4edda; color: #1E7E50; padding: 2px 10px; border-radius: 12px; font-size: 12px; }
.badge-inactivo { background: #f8d7da; color: #c0392b; padding: 2px 10px; border-radius: 12px; font-size: 12px; }
.item-acciones { display: flex; gap: 8px; align-items: center; }
.btn-editar, .btn-guardar, .btn-eliminar, .btn-toggle { padding: 5px 10px; border: 1px solid #eee; background: white; border-radius: 6px; cursor: pointer; font-size: 12px; }
.btn-editar:hover { background: #D6E4F7; }
.btn-guardar { border-color: #1E7E50; color: #1E7E50; }
.btn-eliminar:hover { background: #f8d7da; }
.exito { color: #1E7E50; margin-bottom: 12px; }
.error { color: red; margin-bottom: 12px; }
/* Formularios */
.form-seccion { max-width: 600px; }
.grupo { margin-bottom: 16px; }
label { font-size: 13px; color: #555; display: block; margin-bottom: 6px; }
input, select {
  display: block; width: 100%;
  padding: 8px 12px; font-size: 14px;
  border: 1px solid #ccc; border-radius: 6px;
}
.fila2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.fila3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }
.input-readonly { background: #F2F4F7; color: #555; cursor: not-allowed; }
.badge-auto { display: inline-block; font-size: 11px; padding: 2px 8px; border-radius: 6px; background: #D6E4F7; color: #1B3A6B; margin-left: 8px; }
.genero-wrap { display: flex; gap: 12px; flex-wrap: wrap; }
.genero-btn { flex: 1; padding: 10px; text-align: center; border: 1px solid #ccc; border-radius: 6px; cursor: pointer; font-size: 14px; color: #555; min-width: 80px; }
.genero-btn.activo { border: 2px solid #1B3A6B; background: #D6E4F7; color: #1B3A6B; font-weight: 500; }
.seccion-tallas { margin-top: 24px; }
.seccion-titulo { font-size: 14px; font-weight: 500; color: #1B3A6B; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #eee; }
.badge-genero { display: inline-block; font-size: 11px; padding: 2px 8px; border-radius: 6px; background: #D6E4F7; color: #1B3A6B; margin-left: 8px; }
.tabla-tallas { width: 100%; border-collapse: collapse; }
.tabla-tallas th { font-size: 12px; color: #888; padding: 6px 8px; text-align: left; border-bottom: 1px solid #eee; }
.tabla-tallas td { padding: 6px 8px; border-bottom: 1px solid #eee; }
.talla-label { font-size: 14px; font-weight: 500; color: #333; }
.talla-input { width: 80px !important; }
.aviso { margin-top: 16px; padding: 12px 16px; background: #fff3cd; border-radius: 8px; font-size: 13px; color: #856404; border-left: 4px solid #ffc107; }
.btn-submit { margin-top: 24px; width: 100%; padding: 12px; background: #1B3A6B; color: white; border: none; border-radius: 6px; font-size: 15px; cursor: pointer; }
.btn-submit:disabled { background: #ccc; }
</style>