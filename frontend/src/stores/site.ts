import { defineStore } from 'pinia'
import type { SiteInfo } from '@/types'
import { fetchSite, updateSite } from '@/api'

export const useSiteStore = defineStore('site', {
  state: () => ({
    info: null as SiteInfo | null,
    loaded: false,
  }),
  actions: {
    async loadSite() {
      if (this.loaded) return
      this.info = await fetchSite()
      this.loaded = true
    },
    async saveSite() {
      if (!this.info) return
      const updated = await updateSite({
        services: this.info.services,
        clients: this.info.clients,
        homeSections: this.info.homeSections,
      })
      this.info = { ...this.info, ...updated }
    },
  },
})
