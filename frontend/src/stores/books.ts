import { defineStore } from 'pinia'
import type { Book, BookQuery, Category } from '@/types'
import { fetchBook, fetchBooks, fetchCategories } from '@/api'

export const useBooksStore = defineStore('books', {
  state: () => ({
    books: [] as Book[],
    categories: [] as Category[],
    total: 0,
    loaded: false,
    error: '' as string,
  }),
  getters: {
    onSale: (state): Book[] => state.books.filter((b) => b.onSale),
    featuredBooks: (state): Book[] => state.books.filter((b) => b.featured),
    byCategory: (state) => (categoryId: string): Book[] =>
      state.books.filter((b) => b.category === categoryId),
  },
  actions: {
    async loadBooks(params?: BookQuery) {
      try {
        const res = await fetchBooks(params)
        this.books = res.items
        this.total = res.total
        this.loaded = true
      } catch (e) {
        this.error = e instanceof Error ? e.message : 'unknown error'
      }
    },
    async loadCategories() {
      if (this.categories.length) return
      this.categories = await fetchCategories()
    },
    async loadBook(id: string): Promise<Book | undefined> {
      return fetchBook(id)
    },
  },
})
