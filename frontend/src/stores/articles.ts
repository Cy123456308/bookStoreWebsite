import { defineStore } from 'pinia'
import type { Article, ArticleQuery } from '@/types'
import { fetchArticle, fetchArticles } from '@/api'

export const useArticlesStore = defineStore('articles', {
  state: () => ({
    articles: [] as Article[],
    total: 0,
    loaded: false,
  }),
  actions: {
    async loadArticles(params?: ArticleQuery) {
      const res = await fetchArticles(params)
      this.articles = res.items
      this.total = res.total
      this.loaded = true
    },
    async loadArticle(id: string): Promise<Article | undefined> {
      return fetchArticle(id)
    },
  },
})
