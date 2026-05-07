import { onMounted, onUnmounted } from 'vue'
import axios from 'axios'

export function useKeepAlive(intervalMinutes = 10) {
  let intervalId = null

  const ping = async () => {
    try {
      await axios.get(`${import.meta.env.VITE_API_URL}/health`)
      console.log('[KeepAlive] Backend activo ✓')
    } catch (e) {
      console.warn('[KeepAlive] Backend no responde:', e.message)
    }
  }

  onMounted(() => {
    ping()
    intervalId = setInterval(ping, intervalMinutes * 60 * 1000)
  })

  onUnmounted(() => {
    clearInterval(intervalId)
  })
}