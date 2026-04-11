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

    <!-- Formulario agregar -->
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

    <!-- Lista -->
    <p v-if="cargando">Cargando...</p>
    <div v-else class="lista">
      <div v-if="items.length === 0" class="vacio">
        No hay {{ tipoLabel }} registradas. Agrega la primera arriba.
      </div>
      <div
        v-for="item in items" :key="item.id"
        class="item-row"
      >
        <div class="item-info">
          <span v-if="!item.editando" class="item-valor">{{ item.valor }}</span>
          <input
            v-else
            v-model="item.valorTemp"
            type="text"
            class="input-editar"
            @keyup.enter="guardarEdicion(item)"
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
</template>

<script>
import axios from 'axios'

const API = import.meta.env.VITE_API_URL

export default {
  data() {
    return {
      tipoActivo: 'categoria',
      tipos: tipos: [
        { key: 'categoria', label: 'Categorías' },
        { key: 'marca', label: 'Marcas' },
        { key: 'proveedor', label: 'Proveedores' },
        { key: 'genero', label: 'Géneros' },
        { key: 'talla', label: 'Tallas' },
        { key: 'metodo_pago', label: 'Métodos de pago' },
      ],
      items: [],
      cargando: false,
      nuevoValor: '',
      mensaje: '',
      exito: false
    }
  },
  computed: {
    tipoLabel() {
      return this.tipos.find(t => t.key === this.tipoActivo)?.label || ''
    }
  },
  methods: {
    async cambiarTipo(tipo) {
      this.tipoActivo = tipo
      this.nuevoValor = ''
      this.mensaje = ''
      await this.cargar()
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
    async agregar() {
      if (!this.nuevoValor.trim()) return
      try {
        await axios.post(`${API}/maestras`, {
          tipo: this.tipoActivo,
          valor: this.nuevoValor.trim(),
          activo: true
        })
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
    iniciarEdicion(item) {
      item.valorTemp = item.valor
      item.editando = true
    },
    async guardarEdicion(item) {
      try {
        await axios.put(`${API}/maestras/${item.id}`, {
          tipo: this.tipoActivo,
          valor: item.valorTemp,
          activo: item.activo
        })
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
        await axios.put(`${API}/maestras/${item.id}`, {
          tipo: this.tipoActivo,
          valor: item.valor,
          activo: !item.activo
        })
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
.tabs {
  display: flex; gap: 8px; margin-bottom: 24px;
  flex-wrap: wrap;
}
.tab {
  padding: 8px 16px; border: 1px solid #ccc;
  background: white; border-radius: 20px;
  cursor: pointer; font-size: 13px; color: #555;
}
.tab.activo {
  background: #1B3A6B; color: white; border-color: #1B3A6B;
}
.form-wrap {
  display: flex; gap: 8px; margin-bottom: 16px;
}
.form-wrap input {
  flex: 1; padding: 10px 14px;
  border: 1px solid #ccc; border-radius: 8px; font-size: 14px;
}
.btn-agregar {
  padding: 10px 20px; background: #1B3A6B;
  color: white; border: none; border-radius: 8px;
  cursor: pointer; font-size: 14px;
}
.btn-agregar:disabled { background: #ccc; cursor: not-allowed; }
.lista { display: flex; flex-direction: column; gap: 8px; }
.vacio {
  text-align: center; padding: 32px;
  color: #888; background: white;
  border-radius: 8px; font-size: 14px;
}
.item-row {
  display: flex; justify-content: space-between;
  align-items: center; background: white;
  border: 1px solid #eee; border-radius: 8px;
  padding: 12px 16px;
}
.item-info { display: flex; align-items: center; gap: 12px; }
.item-valor { font-size: 14px; color: #333; font-weight: 500; }
.input-editar {
  padding: 6px 10px; border: 1px solid #2E5FA3;
  border-radius: 6px; font-size: 14px; width: 200px;
}
.badge-activo {
  background: #d4edda; color: #1E7E50;
  padding: 2px 10px; border-radius: 12px; font-size: 12px;
}
.badge-inactivo {
  background: #f8d7da; color: #c0392b;
  padding: 2px 10px; border-radius: 12px; font-size: 12px;
}
.item-acciones { display: flex; gap: 8px; align-items: center; }
.btn-editar, .btn-guardar, .btn-eliminar, .btn-toggle {
  padding: 5px 10px; border: 1px solid #eee;
  background: white; border-radius: 6px;
  cursor: pointer; font-size: 12px;
}
.btn-editar:hover { background: #D6E4F7; }
.btn-guardar { border-color: #1E7E50; color: #1E7E50; }
.btn-eliminar:hover { background: #f8d7da; }
.exito { color: #1E7E50; margin-bottom: 12px; }
.error { color: red; margin-bottom: 12px; }
</style>