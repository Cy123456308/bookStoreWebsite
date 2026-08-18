<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useArticlesStore } from '@/stores/articles'
import { useAuthStore } from '@/stores/auth'
import { updateArticle, uploadImage, createArticle, deleteArticle } from '@/api'
import InlineEdit from '@/components/InlineEdit.vue'
import type { Article } from '@/types'

const articles = useArticlesStore()
const auth = useAuthStore()

const PAGE_SIZE = 8
const page = ref(1)
const saving = ref(false)
const saveMsg = ref('')

async function load() {
  await articles.loadArticles({ page: page.value, pageSize: PAGE_SIZE })
}

function changePage(p: number) {
  if (p < 1 || p > totalPages.value || p === page.value) return
  page.value = p
  articles.loadArticles({ page: p, pageSize: PAGE_SIZE })
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const totalPages = computed(() => Math.max(1, Math.ceil(articles.total / PAGE_SIZE)))

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

async function saveArticleField(article: Article, field: string, value: string) {
  saving.value = true
  saveMsg.value = ''
  try {
    const updated = await updateArticle(article.id, { [field]: value })
    const idx = articles.articles.findIndex((a) => a.id === article.id)
    if (idx !== -1) {
      articles.articles[idx] = { ...articles.articles[idx], ...updated }
    }
    saveMsg.value = '保存しました'
    setTimeout(() => (saveMsg.value = ''), 2000)
  } catch {
    saveMsg.value = '保存に失敗しました'
  } finally {
    saving.value = false
  }
}

async function addArticle() {
  saving.value = true
  saveMsg.value = ''
  try {
    const created = await createArticle({
      title: '新しいコラム',
      excerpt: '',
      body: '',
      publishedAt: new Date().toISOString().slice(0, 10),
      sortWeight: articles.articles.length,
      featured: false,
    })
    articles.articles.unshift(created)
    saveMsg.value = 'コラムを追加しました'
    setTimeout(() => (saveMsg.value = ''), 2000)
  } catch (e) {
    console.error('addArticle failed:', e)
    saveMsg.value = '追加に失敗しました: ' + (e instanceof Error ? e.message : '')
  } finally {
    saving.value = false
  }
}

async function removeArticle(article: Article) {
  saving.value = true
  saveMsg.value = ''
  try {
    await deleteArticle(article.id)
    articles.articles = articles.articles.filter((a) => a.id !== article.id)
    saveMsg.value = 'コラムを削除しました'
    setTimeout(() => (saveMsg.value = ''), 2000)
  } catch (e) {
    console.error('removeArticle failed:', e)
    saveMsg.value = '削除に失敗しました: ' + (e instanceof Error ? e.message : '')
  } finally {
    saving.value = false
  }
}

async function onCoverUpload(article: Article, file: File) {
  saving.value = true
  saveMsg.value = ''
  try {
    const res = await uploadImage(file)
    const updated = await updateArticle(article.id, { cover: res.url })
    const idx = articles.articles.findIndex((a) => a.id === article.id)
    if (idx !== -1) {
      articles.articles[idx] = { ...articles.articles[idx], ...updated }
    }
    saveMsg.value = '画像を更新しました'
    setTimeout(() => (saveMsg.value = ''), 2000)
  } catch {
    saveMsg.value = 'アップロードに失敗しました'
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<template>
  <section class="column">
    <header class="column__header">
      <h1 class="column__title">コラム</h1>
      <p class="column__intro">
        出版活動や書籍にまつわる話題をお届けします。
      </p>
    </header>

    <div v-if="auth.editing" class="column__admin-actions">
      <button type="button" class="column__add-btn" @click="addArticle">+ コラム追加</button>
    </div>

    <!-- Admin save status -->
    <div v-if="auth.isLoggedIn && auth.editing" class="column__save-status">
      <span v-if="saving">保存中…</span>
      <span v-else-if="saveMsg" class="column__save-success">{{ saveMsg }}</span>
    </div>

    <ul v-if="articles.articles.length" class="column__list">
      <li v-for="a in articles.articles" :key="a.id" class="column__item">
        <RouterLink class="column__link" :to="auth.editing ? '#' : `/shhy/${a.id}`">
          <span class="column__thumb">
            <img v-if="a.cover" :src="a.cover" :alt="a.title" />
            <span v-else>图</span>
            <label v-if="auth.editing" class="column__thumb-upload">
              <input
                type="file"
                accept="image/*"
                @change="(e) => {
                  const t = e.target as HTMLInputElement
                  if (t.files?.[0]) onCoverUpload(a, t.files[0])
                }"
              />
              <span>変更</span>
            </label>
          </span>
          <span class="column__body">
            <span class="column__item-title">
              <InlineEdit
                :model-value="a.title"
                :editing="auth.editing"
                placeholder="タイトル"
                @save="(v) => saveArticleField(a, 'title', v)"
              />
            </span>
            <span class="column__item-excerpt">
              <InlineEdit
                :model-value="a.excerpt || ''"
                :editing="auth.editing"
                tag="textarea"
                placeholder="概要"
                @save="(v) => saveArticleField(a, 'excerpt', v)"
              />
            </span>
            <span class="column__date">
              <InlineEdit
                :model-value="a.publishedAt || ''"
                :editing="auth.editing"
                placeholder="公開日"
                @save="(v) => saveArticleField(a, 'publishedAt', v)"
              />
            </span>
          </span>
        </RouterLink>
        <button v-if="auth.editing" type="button" class="column__remove-btn" @click="removeArticle(a)">削除</button>
      </li>
    </ul>
    <p v-else-if="articles.loaded" class="column__empty">
      コラム記事がまだありません。
    </p>
    <p v-else class="column__empty">コラムを読み込み中…（占位）</p>

    <nav v-if="totalPages > 1" class="column__pager" aria-label="ページ送り">
      <button
        type="button"
        class="column__page"
        :disabled="page <= 1"
        @click="changePage(page - 1)"
      >
        ‹
      </button>
      <template v-for="(item, i) in pageItems" :key="i">
        <span v-if="item === '...'" class="column__ellipsis">…</span>
        <button
          v-else
          type="button"
          class="column__page"
          :class="{ 'column__page--active': item === page }"
          @click="changePage(item)"
        >
          {{ item }}
        </button>
      </template>
      <button
        type="button"
        class="column__page"
        :disabled="page >= totalPages"
        @click="changePage(page + 1)"
      >
        ›
      </button>
    </nav>
  </section>
</template>

<style scoped>
.column__header {
  margin: 8px 0 20px;
}

.column__admin-actions {
  margin-bottom: 16px;
}

.column__add-btn {
  padding: 6px 14px;
  background: #1a1a2e;
  color: #fff;
  border: none;
  font-size: 12px;
  cursor: pointer;
  border-radius: 3px;
}

.column__add-btn:hover {
  background: #e94560;
}

.column__remove-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 2px 8px;
  background: #fff;
  color: #c00;
  border: 1px solid #c00;
  font-size: 11px;
  cursor: pointer;
  border-radius: 3px;
}

.column__remove-btn:hover {
  background: #c00;
  color: #fff;
}

.column__title {
  font-size: 24px;
  margin: 0 0 6px;
  border-left: 4px solid #333;
  padding-left: 10px;
}

.column__intro {
  margin: 0 0 0 14px;
  font-size: 12px;
  color: #666;
  line-height: 1.7;
}

.column__save-status {
  text-align: right;
  padding: 4px 0 8px;
  font-size: 12px;
  min-height: 20px;
}

.column__save-success {
  color: #2a7;
}

.column__list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.column__item {
  border-bottom: 1px solid #eee;
  position: relative;
}

.column__item:first-child {
  border-top: 1px solid #eee;
}

.column__link {
  display: flex;
  gap: 20px;
  padding: 18px 4px;
  text-decoration: none;
  color: inherit;
}

.column__link:hover .column__item-title {
  color: #004b98;
}

.column__thumb {
  width: 160px;
  height: 105px;
  flex-shrink: 0;
  background: #ddd;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #888;
  overflow: hidden;
  font-size: 12px;
  position: relative;
}

.column__thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.column__thumb-upload {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
  text-align: center;
  padding: 4px;
  font-size: 11px;
  cursor: pointer;
}

.column__thumb-upload input {
  display: none;
}

.column__body {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
}

.column__item-title {
  font-size: 17px;
  font-weight: 600;
}

.column__item-excerpt {
  font-size: 13px;
  color: #666;
  line-height: 1.7;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.column__date {
  font-size: 11px;
  color: #999;
  margin-top: 2px;
}

.column__empty {
  color: #888;
  padding: 24px 0;
}

.column__pager {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 6px;
  margin: 32px 0 8px;
}

.column__page {
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

.column__page:hover:not(:disabled):not(.column__page--active) {
  border-color: #999;
  color: #000;
}

.column__page--active {
  background: #333;
  border-color: #333;
  color: #fff;
  font-weight: 700;
  cursor: default;
}

.column__page:disabled {
  color: #ccc;
  cursor: default;
}

.column__ellipsis {
  color: #999;
  padding: 0 4px;
}
</style>
