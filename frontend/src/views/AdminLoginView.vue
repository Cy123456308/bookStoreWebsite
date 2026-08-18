<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const username = ref('')
const password = ref('')
const loading = ref(false)

async function onSubmit(e: Event) {
  e.preventDefault()
  loading.value = true
  const ok = await auth.login(username.value, password.value)
  loading.value = false
  if (ok) {
    router.push('/admin')
  }
}
</script>

<template>
  <div class="admin-login-page">
    <div class="admin-login-card">
      <h1 class="admin-login-title">管理画面ログイン</h1>
      <form class="admin-login-form" @submit="onSubmit">
        <div v-if="auth.error" class="admin-login-error">{{ auth.error }}</div>
        <div class="admin-login-field">
          <label>ユーザー名</label>
          <input v-model="username" type="text" autocomplete="username" required />
        </div>
        <div class="admin-login-field">
          <label>パスワード</label>
          <input v-model="password" type="password" autocomplete="current-password" required />
        </div>
        <button class="admin-login-btn" type="submit" :disabled="loading">
          {{ loading ? 'ログイン中…' : 'ログイン' }}
        </button>
      </form>
      <p class="admin-login-hint">初期値: admin / admin（環境変数 ADMIN_USER / ADMIN_PASS で変更）</p>
    </div>
  </div>
</template>

<style scoped>
.admin-login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f3f3;
  padding: 24px;
}

.admin-login-card {
  width: 100%;
  max-width: 360px;
  background: #fff;
  border: 1px solid #eee;
  padding: 32px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.admin-login-title {
  font-size: 20px;
  margin: 0 0 24px;
  text-align: center;
  border-left: 4px solid #333;
  padding-left: 10px;
}

.admin-login-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.admin-login-error {
  color: #c00;
  font-size: 13px;
  text-align: center;
}

.admin-login-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.admin-login-field label {
  font-size: 13px;
  color: #333;
}

.admin-login-field input {
  padding: 10px;
  border: 1px solid #ccc;
  font-size: 14px;
}

.admin-login-field input:focus {
  outline: none;
  border-color: #004b98;
}

.admin-login-btn {
  margin-top: 8px;
  padding: 12px;
  background: #333;
  color: #fff;
  border: none;
  font-size: 15px;
  cursor: pointer;
}

.admin-login-btn:hover:not(:disabled) {
  background: #000;
}

.admin-login-btn:disabled {
  opacity: 0.6;
  cursor: default;
}

.admin-login-hint {
  margin: 16px 0 0;
  font-size: 11px;
  color: #999;
  text-align: center;
}
</style>