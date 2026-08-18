import { defineStore } from 'pinia'
import type { DownloadFile } from '@/types'
import { fetchDownloads } from '@/api'

export const useDownloadsStore = defineStore('downloads', {
  state: () => ({
    downloads: [] as DownloadFile[],
    loaded: false,
  }),
  actions: {
    async loadDownloads() {
      if (this.loaded) return
      this.downloads = await fetchDownloads()
      this.loaded = true
    },
  },
})
