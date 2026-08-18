import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { adminLogin, adminLogout } from '@/api'

const TOKEN_KEY = 'hirogawa_admin_token'
const USERNAME_KEY = 'hirogawa_admin_username'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string>(localStorage.getItem(TOKEN_KEY) || '')
  const username = ref<string>(localStorage.getItem(USERNAME_KEY) || '')
  const error = ref('')
  const editing = ref(false)

  const isLoggedIn = computed(() => !!token.value)

  function setToken(t: string) {
    token.value = t
    localStorage.setItem(TOKEN_KEY, t)
  }

  async function login(u: string, p: string): Promise<boolean> {
    error.value = ''
    try {
      const res = await adminLogin(u, p)
      setToken(res.token)
      username.value = u
      localStorage.setItem(USERNAME_KEY, u)
      return true
    } catch {
      error.value = 'ユーザー名またはパスワードが違います'
      return false
    }
  }

  function logout() {
    if (token.value) adminLogout(token.value).catch(() => undefined)
    token.value = ''
    username.value = ''
    editing.value = false
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USERNAME_KEY)
  }

  function toggleEditing() {
    editing.value = !editing.value
  }

  return { token, username, error, isLoggedIn, editing, login, logout, toggleEditing }
})
