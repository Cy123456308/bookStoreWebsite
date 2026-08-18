<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

function handleLogout() {
  auth.logout()
  router.push('/admin/login')
}
</script>

<template>
  <div class="admin-layout">
    <header class="admin-header">
      <h1 class="admin-title">宏河書房 管理画面</h1>
      <div class="admin-user">
        <span>管理者: {{ auth.username }}</span>
        <button class="admin-logout" @click="handleLogout">ログアウト</button>
      </div>
    </header>
    <main class="admin-main">
      <slot />
    </main>
  </div>
</template>

<style scoped>
.admin-layout {
  min-height: 100vh;
  background: #f3f3f3;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #fff;
  border-bottom: 1px solid #eee;
}

.admin-title {
  font-size: 18px;
  margin: 0;
}

.admin-user {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 13px;
  color: #666;
}

.admin-logout {
  padding: 6px 14px;
  background: #333;
  color: #fff;
  border: none;
  cursor: pointer;
  font-size: 13px;
}

.admin-logout:hover {
  background: #000;
}

.admin-main {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}
</style>