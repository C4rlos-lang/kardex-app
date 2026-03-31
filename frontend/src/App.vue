<template>
  <div class="layout">
    <Sidebar />
    <div class="main">
      <router-view />
    </div>
  </div>
</template>

<script>
import Sidebar from './components/Sidebar.vue'

export default {
  components: { Sidebar }
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: Arial; background: #F2F4F7; }
.layout {
  display: flex;
}
.main {
  margin-left: 220px;
  padding: 40px;
  width: 100%;
  min-height: 100vh;
}
</style>