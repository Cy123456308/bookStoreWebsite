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
  <div class="admin-toolbar">
    <div class="admin-toolbar__inner">
      <span class="admin-toolbar__badge">管理モード</span>
      <span class="admin-toolbar__user">{{ auth.username }}</span>
      <button
        class="admin-toolbar__toggle"
        :class="{ 'admin-toolbar__toggle--active': auth.editing }"
        @click="auth.toggleEditing()"
      >
        {{ auth.editing ? '編集終了' : '編集開始' }}
      </button>
      <button class="admin-toolbar__logout" @click="handleLogout">
        ログアウト
      </button>
    </div>
  </div>
</template>

<style scoped>
.admin-toolbar {
  background: #1a1a2e;
  color: #fff;
  position: sticky;
  top: 0;
  z-index: 1000;
}

.admin-toolbar__inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  font-size: 13px;
}

.admin-toolbar__badge {
  background: #e94560;
  color: #fff;
  padding: 2px 8px;
  border-radius: 3px;
  font-weight: 700;
  font-size: 11px;
  letter-spacing: 0.5px;
}

.admin-toolbar__user {
  color: #aaa;
}

.admin-toolbar__toggle {
  margin-left: auto;
  padding: 4px 14px;
  border: 1px solid #555;
  background: transparent;
  color: #fff;
  cursor: pointer;
  font-size: 12px;
  border-radius: 3px;
}

.admin-toolbar__toggle:hover {
  border-color: #888;
}

.admin-toolbar__toggle--active {
  background: #e94560;
  border-color: #e94560;
  color: #fff;
}

.admin-toolbar__toggle--active:hover {
  background: #c0392b;
  border-color: #c0392b;
}

.admin-toolbar__logout {
  padding: 4px 14px;
  border: 1px solid #555;
  background: transparent;
  color: #fff;
  cursor: pointer;
  font-size: 12px;
  border-radius: 3px;
}

.admin-toolbar__logout:hover {
  border-color: #888;
}
</style>
