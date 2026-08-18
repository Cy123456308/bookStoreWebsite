import { defineStore } from 'pinia'
import type { Banner } from '@/types'
import { fetchBanners } from '@/api'

export const useBannersStore = defineStore('banners', {
  state: () => ({
    banners: [] as Banner[],
    loaded: false,
  }),
  actions: {
    async loadBanners(force = false) {
      if (this.loaded && !force) return
      this.banners = await fetchBanners()
      this.loaded = true
    },
  },
})
