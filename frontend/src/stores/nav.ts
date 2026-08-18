import { defineStore } from 'pinia'
import type { NavItem } from '@/types'
import { fetchNav } from '@/api'

export const useNavStore = defineStore('nav', {
  state: () => ({
    items: [] as NavItem[],
    loaded: false,
  }),
  actions: {
    async loadNav() {
      if (this.loaded) return
      try {
        this.items = await fetchNav()
        this.loaded = true
      } catch {
        this.items = []
        this.loaded = true
      }
    },
  },
})
