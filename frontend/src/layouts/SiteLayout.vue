<script setup lang="ts">
import SiteHeader from './SiteHeader.vue'
import SiteNav from './SiteNav.vue'
import SiteFooter from './SiteFooter.vue'
import AdminToolbar from '@/components/AdminToolbar.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
</script>

<template>
  <div class="site-root">
    <AdminToolbar v-if="auth.isLoggedIn" />
    <SiteHeader />
    <SiteNav />
    <main class="site-main">
      <RouterView />
    </main>
    <SiteFooter />
  </div>
</template>

<style scoped>
.site-root {
  min-width: 1200px;
  background-color: #f3f3f3;
  color: #333;
}

.site-main {
  width: 1200px;
  margin: 0 auto;
  min-height: 400px;
  padding: 24px 0;
  box-sizing: border-box;
}
</style>
