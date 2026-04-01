<template>
  <div class="sidebar">
    <div class="logo">📦 Kardex</div>
    <nav>
      <router-link to="/productos">➕ Crear Producto</router-link>
      <router-link to="/lista">📋 Lista de Productos</router-link>
      <router-link to="/almacenes">🏪 Almacenes</router-link>
    </nav>
  </div>
</template>

<style scoped>
.sidebar {
  width: 220px;
  min-height: 100vh;
  background: #1B3A6B;
  padding: 20px 0;
  position: fixed;
  left: 0;
  top: 0;
}
.logo {
  color: white;
  font-size: 20px;
  font-weight: bold;
  padding: 0 20px 30px;
  border-bottom: 1px solid #2E5FA3;
}
nav {
  margin-top: 20px;
}
nav a {
  display: block;
  color: #D6E4F7;
  text-decoration: none;
  padding: 12px 20px;
  font-size: 15px;
  transition: background 0.2s;
}
nav a:hover, nav a.router-link-active {
  background: #2E5FA3;
  color: white;
}
</style>