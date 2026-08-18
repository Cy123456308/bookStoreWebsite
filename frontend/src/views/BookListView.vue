<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import BookCard from '@/components/BookCard.vue'
import { useBooksStore } from '@/stores/books'
import { useAuthStore } from '@/stores/auth'
import { updateBook, createBook, deleteBook } from '@/api'
import type { Book } from '@/types'

const books = useBooksStore()
const auth = useAuthStore()

const PAGE_SIZE = 12
const activeCategory = ref('')
const query = ref('')
const searchInput = ref('')
const page = ref(1)
const savingId = ref('')

let debounceTimer: ReturnType<typeof setTimeout> | null = null

async function load(resetPage = true) {
  if (resetPage) page.value = 1
  await books.loadBooks({
    category: activeCategory.value || undefined,
    q: query.value || undefined,
    page: page.value,
    pageSize: PAGE_SIZE,
  })
}

function selectCategory(id: string) {
  activeCategory.value = id
  load()
}

function onSearchInput() {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    query.value = searchInput.value.trim()
    load()
  }, 300)
}

function changePage(p: number) {
  if (p < 1 || p > totalPages.value || p === page.value) return
  page.value = p
  books.loadBooks({
    category: activeCategory.value || undefined,
    q: query.value || undefined,
    page: p,
    pageSize: PAGE_SIZE,
  })
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const totalPages = computed(() => Math.max(1, Math.ceil(books.total / PAGE_SIZE)))

const pageItems = computed<(number | '...')[]>(() => {
  const tp = totalPages.value
  if (tp <= 7) return Array.from({ length: tp }, (_, i) => i + 1)
  const cur = page.value
  const out: (number | '...')[] = [1]
  const start = Math.max(2, cur - 1)
  const end = Math.min(tp - 1, cur + 1)
  if (start > 2) out.push('...')
  for (let i = start; i <= end; i++) out.push(i)
  if (end < tp - 1) out.push('...')
  out.push(tp)
  return out
})

async function saveBookField(book: Book, field: string, value: string | number) {
  savingId.value = book.id
  try {
    const updated = await updateBook(book.id, { [field]: value })
    // Update the book in the store
    const idx = books.books.findIndex((b) => b.id === book.id)
    if (idx !== -1) {
      books.books[idx] = { ...books.books[idx], ...updated }
    }
  } catch {
    // Could show error
  } finally {
    savingId.value = ''
  }
}

async function addBook() {
  savingId.value = 'new'
  try {
    const newBook = await createBook({
      title: '新しい書籍',
      author: '',
      category: books.categories[0]?.id || '',
      onSale: true,
      sortWeight: books.books.length,
      featured: false,
    })
    books.books.unshift(newBook)
  } catch (e) {
    console.error('addBook failed:', e)
    alert('書籍の追加に失敗しました: ' + (e instanceof Error ? e.message : ''))
  } finally {
    savingId.value = ''
  }
}

async function removeBook(book: Book) {
  savingId.value = book.id
  try {
    await deleteBook(book.id)
    books.books = books.books.filter((b) => b.id !== book.id)
  } catch (e) {
    console.error('removeBook failed:', e)
    alert('書籍の削除に失敗しました: ' + (e instanceof Error ? e.message : ''))
  } finally {
    savingId.value = ''
  }
}

async function toggleFeatured(book: Book) {
  savingId.value = book.id
  try {
    const updated = await updateBook(book.id, { featured: !book.featured })
    const idx = books.books.findIndex((b) => b.id === book.id)
    if (idx !== -1) {
      books.books[idx] = { ...books.books[idx], ...updated }
    }
  } catch (e) {
    console.error('toggleFeatured failed:', e)
  } finally {
    savingId.value = ''
  }
}

async function moveBook(book: Book, direction: 'up' | 'down') {
  const idx = books.books.findIndex((b) => b.id === book.id)
  if (idx === -1) return
  const targetIdx = direction === 'up' ? idx - 1 : idx + 1
  if (targetIdx < 0 || targetIdx >= books.books.length) return
  const other = books.books[targetIdx]
  savingId.value = book.id
  try {
    // Swap sortWeight
    const bookWeight = book.sortWeight
    const otherWeight = other.sortWeight
    await updateBook(book.id, { sortWeight: otherWeight })
    await updateBook(other.id, { sortWeight: bookWeight })
    // Update local
    books.books[idx] = { ...books.books[idx], sortWeight: otherWeight }
    books.books[targetIdx] = { ...books.books[targetIdx], sortWeight: bookWeight }
    // Reorder array
    books.books.splice(targetIdx, 0, books.books.splice(idx, 1)[0])
  } catch (e) {
    console.error('moveBook failed:', e)
  } finally {
    savingId.value = ''
  }
}

onMounted(async () => {
  await books.loadCategories()
  await load()
})
</script>

<template>
  <section class="book-list">
    <header class="book-list__header">
      <h1 class="book-list__title">書籍</h1>
      <p class="book-list__intro">
        中国の文芸・歴史・思想・哲学・文化・民俗などの書籍を取り扱っています。
      </p>
    </header>

    <div class="book-list__toolbar">
      <nav class="book-list__tabs" aria-label="カテゴリ">
        <button
          type="button"
          class="book-list__tab"
          :class="{ 'book-list__tab--active': activeCategory === '' }"
          @click="selectCategory('')"
        >
          すべて
        </button>
        <button
          v-for="cat in books.categories"
          :key="cat.id"
          type="button"
          class="book-list__tab"
          :class="{ 'book-list__tab--active': activeCategory === cat.id }"
          @click="selectCategory(cat.id)"
        >
          {{ cat.name }}
        </button>
      </nav>

      <div class="book-list__search">
        <input
          v-model="searchInput"
          class="book-list__search-input"
          type="search"
          placeholder="書名・著者で検索"
          aria-label="検索"
          @input="onSearchInput"
        />
      </div>
    </div>

    <div class="book-list__meta-row">
      <p class="book-list__meta">全 {{ books.total }} 冊</p>
      <div v-if="auth.editing" class="book-list__admin-actions">
        <button type="button" class="book-list__add-btn" @click="addBook" :disabled="savingId === 'new'">
          + 書籍追加
        </button>
      </div>
    </div>

    <div v-if="books.books.length" class="book-list__grid">
      <div v-for="(book, idx) in books.books" :key="book.id" class="book-list__card-wrap">
        <BookCard
          :book="book"
          :on-save="auth.editing ? saveBookField : undefined"
        />
        <div v-if="auth.editing" class="book-list__card-admin">
          <button
            type="button"
            class="book-list__feat-btn"
            :class="{ 'book-list__feat-btn--active': book.featured }"
            :title="book.featured ? '特集解除' : '特集設定'"
            @click="toggleFeatured(book)"
          >
            {{ book.featured ? '★' : '☆' }}
          </button>
          <button
            type="button"
            class="book-list__move-btn"
            :disabled="idx === 0"
            @click="moveBook(book, 'up')"
            title="上へ"
          >↑</button>
          <button
            type="button"
            class="book-list__move-btn"
            :disabled="idx === books.books.length - 1"
            @click="moveBook(book, 'down')"
            title="下へ"
          >↓</button>
          <button
            type="button"
            class="book-list__del-btn"
            @click="removeBook(book)"
            title="削除"
          >✕</button>
        </div>
      </div>
    </div>
    <p v-else-if="books.loaded" class="book-list__empty">
      該当する書籍が見つかりませんでした。
    </p>
    <p v-else class="book-list__empty">書籍データを読み込み中…（占位）</p>

    <nav v-if="totalPages > 1" class="book-list__pager" aria-label="ページ送り">
      <button
        type="button"
        class="book-list__page"
        :disabled="page <= 1"
        @click="changePage(page - 1)"
      >
        ‹
      </button>
      <template v-for="(item, i) in pageItems" :key="i">
        <span v-if="item === '...'" class="book-list__ellipsis">…</span>
        <button
          v-else
          type="button"
          class="book-list__page"
          :class="{ 'book-list__page--active': item === page }"
          @click="changePage(item)"
        >
          {{ item }}
        </button>
      </template>
      <button
        type="button"
        class="book-list__page"
        :disabled="page >= totalPages"
        @click="changePage(page + 1)"
      >
        ›
      </button>
    </nav>
  </section>
</template>

<style scoped>
.book-list__header {
  margin: 8px 0 20px;
}

.book-list__title {
  font-size: 24px;
  margin: 0 0 6px;
  border-left: 4px solid #333;
  padding-left: 10px;
}

.book-list__intro {
  margin: 0 0 0 14px;
  font-size: 12px;
  color: #666;
  line-height: 1.7;
}

.book-list__toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  border-bottom: 1px solid #ddd;
  padding-bottom: 12px;
  margin-bottom: 12px;
}

.book-list__tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.book-list__tab {
  border: none;
  background: none;
  padding: 6px 14px;
  font-size: 14px;
  color: #004b98;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  font-family: inherit;
}

.book-list__tab:hover {
  color: #000;
}

.book-list__tab--active {
  color: #000;
  border-bottom-color: #333;
  font-weight: 700;
}

.book-list__search-input {
  width: 240px;
  max-width: 100%;
  padding: 6px 10px;
  font-size: 14px;
  border: 1px solid #ccc;
  font-family: inherit;
  box-sizing: border-box;
}

.book-list__search-input:focus {
  outline: none;
  border-color: #004b98;
}

.book-list__meta-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.book-list__meta {
  font-size: 12px;
  color: #666;
  margin: 0;
}

.book-list__admin-actions {
  display: flex;
  gap: 8px;
}

.book-list__add-btn {
  padding: 6px 14px;
  background: #1a1a2e;
  color: #fff;
  border: none;
  font-size: 12px;
  cursor: pointer;
  border-radius: 3px;
}

.book-list__add-btn:hover {
  background: #e94560;
}

.book-list__add-btn:disabled {
  opacity: 0.5;
  cursor: default;
}

.book-list__card-wrap {
  position: relative;
}

.book-list__card-admin {
  display: flex;
  gap: 4px;
  margin-top: 6px;
  justify-content: center;
}

.book-list__feat-btn {
  padding: 2px 6px;
  border: 1px solid #ddd;
  background: #fff;
  font-size: 14px;
  cursor: pointer;
  border-radius: 3px;
  color: #999;
}

.book-list__feat-btn--active {
  color: #f5a623;
  border-color: #f5a623;
}

.book-list__feat-btn:hover {
  border-color: #f5a623;
}

.book-list__move-btn {
  padding: 2px 6px;
  border: 1px solid #ddd;
  background: #fff;
  font-size: 12px;
  cursor: pointer;
  border-radius: 3px;
}

.book-list__move-btn:hover:not(:disabled) {
  border-color: #004b98;
  color: #004b98;
}

.book-list__move-btn:disabled {
  opacity: 0.3;
  cursor: default;
}

.book-list__del-btn {
  padding: 2px 6px;
  border: 1px solid #ddd;
  background: #fff;
  font-size: 12px;
  cursor: pointer;
  border-radius: 3px;
  color: #c00;
}

.book-list__del-btn:hover {
  background: #c00;
  color: #fff;
  border-color: #c00;
}

.book-list__grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 20px;
}

.book-list__empty {
  color: #888;
  padding: 24px 0;
}

.book-list__pager {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 6px;
  margin: 32px 0 8px;
}

.book-list__page {
  min-width: 34px;
  height: 34px;
  padding: 0 8px;
  border: 1px solid #ddd;
  background: #fff;
  color: #004b98;
  font-size: 14px;
  cursor: pointer;
  font-family: inherit;
}

.book-list__page:hover:not(:disabled):not(.book-list__page--active) {
  border-color: #999;
  color: #000;
}

.book-list__page--active {
  background: #333;
  border-color: #333;
  color: #fff;
  font-weight: 700;
  cursor: default;
}

.book-list__page:disabled {
  color: #ccc;
  cursor: default;
}

.book-list__ellipsis {
  color: #999;
  padding: 0 4px;
}
</style>
