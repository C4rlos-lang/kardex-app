<template>
  <div class="layout">
    <Sidebar :visible="sidebarVisible" />
    <div class="main" :class="{ expandido: !sidebarVisible }">
      <button class="toggle-btn" @click="sidebarVisible = !sidebarVisible">
        {{ sidebarVisible ? '◀' : '▶' }}
      </button>
      <router-view />
    </div>
  </div>
</template>

<script>
import Sidebar from './components/Sidebar.vue'

export default {
  components: { Sidebar },
  data() {
    return {
      sidebarVisible: true
    }
  }
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: Arial; background: #F2F4F7; }
.layout { display: flex; }
.main {
  margin-left: 220px;
  padding: 40px;
  width: 100%;
  min-height: 100vh;
  transition: margin-left 0.3s ease;
  position: relative;
}
.main.expandido {
  margin-left: 0;
}
.toggle-btn {
  position: fixed;
  top: 15px;
  left: 225px;
  z-index: 200;
  background: #1B3A6B;
  color: white;
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  cursor: pointer;
  font-size: 12px;
  transition: left 0.3s ease;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}
.main.expandido .toggle-btn {
  left: 10px;
}
</style>