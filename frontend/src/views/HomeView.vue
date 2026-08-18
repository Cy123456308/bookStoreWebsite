<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import BannerCarousel from '@/components/BannerCarousel.vue'
import BookCard from '@/components/BookCard.vue'
import BookRow from '@/components/BookRow.vue'
import { useBannersStore } from '@/stores/banners'
import { useBooksStore } from '@/stores/books'
import { useArticlesStore } from '@/stores/articles'
import { useAuthStore } from '@/stores/auth'
import { useSiteStore } from '@/stores/site'
import { updateBanner, updateBook, uploadImage, createBanner, deleteBanner } from '@/api'
import InlineEdit from '@/components/InlineEdit.vue'
import type { Banner, Book, HomeSection } from '@/types'

const banners = useBannersStore()
const books = useBooksStore()
const articles = useArticlesStore()
const auth = useAuthStore()
const site = useSiteStore()

const saving = ref(false)
const saveMsg = ref('')

// Map of bookId -> Book for quick lookup
const bookMap = computed(() => {
  const m = new Map<string, Book>()
  for (const b of books.books) m.set(b.id, b)
  return m
})

function getSectionBook(section: HomeSection): Book | undefined {
  return bookMap.value.get(section.bookId)
}

onMounted(() => {
  banners.loadBanners().catch(() => {})
  books.loadBooks().catch(() => {})
  articles.loadArticles({ pageSize: 5 }).catch(() => {})
  site.loadSite().catch(() => {})
})

// --- Banner management ---
async function saveBannerField(banner: Banner, field: string, value: string) {
  saving.value = true
  saveMsg.value = ''
  try {
    console.log('[Banner] saving', banner.id, field, value)
    const updated = await updateBanner(banner.id, { [field]: value })
    console.log('[Banner] save response:', updated)
    const idx = banners.banners.findIndex((b) => b.id === banner.id)
    if (idx !== -1) {
      banners.banners[idx] = { ...banners.banners[idx], ...updated }
    }
    saveMsg.value = '保存しました'
    setTimeout(() => (saveMsg.value = ''), 2000)
  } catch (e) {
    console.error('[Banner] save failed:', e)
    saveMsg.value = '保存に失敗: ' + (e instanceof Error ? e.message : '')
  } finally {
    saving.value = false
  }
}

async function addBanner() {
  saving.value = true
  saveMsg.value = ''
  try {
    console.log('[Banner] creating new banner')
    const created = await createBanner({ image: '', title: '新しいバナー', link: '', order: banners.banners.length + 1 })
    console.log('[Banner] created:', created)
    banners.banners.push(created)
    saveMsg.value = 'バナーを追加しました'
    setTimeout(() => (saveMsg.value = ''), 2000)
  } catch (e) {
    console.error('[Banner] add failed:', e)
    saveMsg.value = '追加に失敗: ' + (e instanceof Error ? e.message : '')
  } finally {
    saving.value = false
  }
}

async function removeBanner(banner: Banner) {
  saving.value = true
  saveMsg.value = ''
  try {
    await deleteBanner(banner.id)
    banners.banners = banners.banners.filter((b) => b.id !== banner.id)
    saveMsg.value = 'バナーを削除しました'
    setTimeout(() => (saveMsg.value = ''), 2000)
  } catch (e) {
    console.error('[Banner] remove failed:', e)
    saveMsg.value = '削除に失敗: ' + (e instanceof Error ? e.message : '')
  } finally {
    saving.value = false
  }
}

async function onBannerImageUpload(banner: Banner, file: File) {
  saving.value = true
  saveMsg.value = ''
  try {
    const res = await uploadImage(file)
    const updated = await updateBanner(banner.id, { image: res.url })
    const idx = banners.banners.findIndex((b) => b.id === banner.id)
    if (idx !== -1) {
      banners.banners[idx] = { ...banners.banners[idx], ...updated }
    }
    saveMsg.value = 'バナー画像を更新しました'
    setTimeout(() => (saveMsg.value = ''), 2000)
  } catch (e) {
    console.error('[Banner] upload failed:', e)
    saveMsg.value = 'アップロードに失敗: ' + (e instanceof Error ? e.message : '')
  } finally {
    saving.value = false
  }
}

// --- Home sections management ---
async function saveHomeSections() {
  saving.value = true
  saveMsg.value = ''
  try {
    await site.saveSite()
    saveMsg.value = '保存しました'
    setTimeout(() => (saveMsg.value = ''), 2000)
  } catch {
    saveMsg.value = '保存に失敗しました'
  } finally {
    saving.value = false
  }
}

function addHomeSection() {
  if (!site.info) return
  const newId = 'sec_' + Date.now()
  // Pick first available book
  const firstBook = books.books[0]
  site.info.homeSections.push({
    id: newId,
    title: '新しいセクション',
    bookId: firstBook?.id || '',
  })
}

function removeHomeSection(index: number) {
  if (!site.info) return
  site.info.homeSections.splice(index, 1)
}

function updateSectionTitle(index: number, value: string) {
  if (!site.info) return
  site.info.homeSections[index].title = value
}

function selectSectionBook(index: number, bookId: string) {
  if (!site.info) return
  site.info.homeSections[index].bookId = bookId
}
</script>

<template>
  <div class="home">
    <!-- Admin save status -->
    <div v-if="auth.isLoggedIn && auth.editing" class="home__save-status">
      <span v-if="saving">保存中…</span>
      <span v-else-if="saveMsg" class="home__save-success">{{ saveMsg }}</span>
    </div>

    <!-- Banner Carousel -->
    <BannerCarousel :banners="banners.banners" />

    <!-- Admin banner editing overlay -->
    <div v-if="auth.editing" class="home__admin-banners">
      <div class="home__admin-header">
        <h3 class="home__admin-title">バナー管理</h3>
        <button type="button" class="home__admin-add" @click="addBanner">+ バナー追加</button>
      </div>
      <div v-for="b in banners.banners" :key="b.id" class="home__admin-banner-item">
        <div class="home__admin-banner-preview">
          <img v-if="b.image" :src="b.image" :alt="b.title" />
          <span v-else>画像なし</span>
        </div>
        <div class="home__admin-banner-fields">
          <label class="home__admin-banner-upload">
            <input
              type="file"
              accept="image/*"
              @change="(e) => {
                const t = e.target as HTMLInputElement
                if (t.files?.[0]) onBannerImageUpload(b, t.files[0])
              }"
            />
            <span>画像変更</span>
          </label>
          <InlineEdit
            :model-value="b.title || ''"
            :editing="true"
            placeholder="バナータイトル"
            @save="(v) => saveBannerField(b, 'title', v)"
          />
          <InlineEdit
            :model-value="b.link || ''"
            :editing="true"
            placeholder="リンクURL"
            @save="(v) => saveBannerField(b, 'link', v)"
          />
        </div>
        <button type="button" class="home__admin-remove" @click="removeBanner(b)">削除</button>
      </div>
    </div>

    <!-- Featured Sections (新刊紹介, 热销书介绍, etc.) -->
    <section
      v-for="(section, idx) in (site.info?.homeSections || [])"
      :key="section.id"
      class="home__featured"
    >
      <div class="home__featured-book">
        <div class="home__label-wrap">
          <span v-if="!auth.editing" class="home__label">{{ section.title }}</span>
          <input
            v-else
            class="home__label-input"
            :value="section.title"
            @input="(e) => updateSectionTitle(idx, (e.target as HTMLInputElement).value)"
          />
          <button v-if="auth.editing" type="button" class="home__section-remove" @click="removeHomeSection(idx)">✕</button>
        </div>
        <div v-if="getSectionBook(section)" class="home__book-promo">
          <RouterLink class="home__book-promo-link" :to="`/book/${getSectionBook(section)!.id}`">
            <div class="home__book-promo-cover">
              <img v-if="getSectionBook(section)!.cover" :src="getSectionBook(section)!.cover" :alt="getSectionBook(section)!.title" />
              <span v-else>封面占位</span>
            </div>
            <div class="home__book-promo-info">
              <h3 class="home__book-promo-title">{{ getSectionBook(section)!.title }}</h3>
              <p v-if="getSectionBook(section)!.author" class="home__book-promo-author">
                {{ getSectionBook(section)!.author }}
              </p>
              <p v-if="getSectionBook(section)!.price" class="home__book-promo-price">
                ¥{{ getSectionBook(section)!.price }}
              </p>
            </div>
          </RouterLink>
        </div>
        <!-- Book selector in edit mode -->
        <div v-if="auth.editing" class="home__book-selector">
          <label class="home__selector-label">書籍を選択:</label>
          <select
            class="home__selector-select"
            :value="section.bookId"
            @change="(e) => selectSectionBook(idx, (e.target as HTMLSelectElement).value)"
          >
            <option value="">-- 選択してください --</option>
            <option v-for="b in books.books" :key="b.id" :value="b.id">{{ b.title }}</option>
          </select>
        </div>
      </div>

      <!-- Show articles only for first section -->
      <div v-if="idx === 0" class="home__featured-news">
        <div class="home__news-head">
          <h2 class="home__news-title">コラム</h2>
          <RouterLink class="home__news-more" to="/shhy">もっと見る&gt;&gt;</RouterLink>
        </div>
        <ul class="home__news-list">
          <li v-for="a in articles.articles" :key="a.id" class="home__news-item">
            <RouterLink class="home__news-link" :to="`/shhy/${a.id}`">
              <span class="home__news-thumb">
                <img v-if="a.cover" :src="a.cover" :alt="a.title" />
                <span v-else>图</span>
              </span>
              <span class="home__news-text">
                <span class="home__news-item-title">{{ a.title }}</span>
                <span v-if="a.excerpt" class="home__news-item-desc">{{ a.excerpt }}</span>
              </span>
            </RouterLink>
          </li>
        </ul>
      </div>
    </section>

    <!-- Add section button -->
    <div v-if="auth.editing" class="home__section-actions">
      <button type="button" class="home__add-section-btn" @click="addHomeSection">+ セクション追加</button>
      <button type="button" class="home__save-btn" @click="saveHomeSections">セクション設定を保存</button>
    </div>

    <!-- 在售書籍グリッド -->
    <h2 class="home__section-title">
      書籍（在售）
      <span v-if="auth.isLoggedIn && auth.editing" class="home__edit-hint">
        書籍の編集は「書籍」ページで行います
      </span>
    </h2>
    <div v-if="books.onSale.length" class="home__book-grid">
      <BookCard
        v-for="book in books.onSale"
        :key="book.id"
        :book="book"
        :on-save="auth.editing ? (b, field, val) => updateBook(b.id, { [field]: val }).then((u) => { const idx = books.books.findIndex(x => x.id === b.id); if (idx !== -1) books.books[idx] = { ...books.books[idx], ...u } }) : undefined"
      />
    </div>
    <p v-else class="home__empty">書籍データを読み込み中…（占位）</p>

    <!-- 書籍シリーズ：横向き一覧行 -->
    <BookRow :books="books.books" title="書籍シリーズ" />
  </div>
</template>

<style scoped>
.home__save-status {
  text-align: right;
  padding: 4px 0;
  font-size: 12px;
  min-height: 20px;
}

.home__save-success {
  color: #2a7;
}

.home__admin-banners {
  background: #f9f9f9;
  border: 1px solid #eee;
  padding: 16px;
  margin-top: 16px;
}

.home__admin-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.home__admin-title {
  font-size: 14px;
  margin: 0;
  color: #666;
}

.home__admin-add {
  padding: 4px 12px;
  background: #1a1a2e;
  color: #fff;
  border: none;
  font-size: 12px;
  cursor: pointer;
  border-radius: 3px;
}

.home__admin-add:hover {
  background: #e94560;
}

.home__admin-remove {
  align-self: flex-start;
  padding: 4px 10px;
  background: #fff;
  color: #c00;
  border: 1px solid #c00;
  font-size: 11px;
  cursor: pointer;
  border-radius: 3px;
}

.home__admin-remove:hover {
  background: #c00;
  color: #fff;
}

.home__admin-banner-item {
  display: flex;
  gap: 16px;
  padding: 12px 0;
  border-bottom: 1px solid #eee;
}

.home__admin-banner-item:last-child {
  border-bottom: none;
}

.home__admin-banner-preview {
  width: 160px;
  height: 60px;
  background: #ddd;
  overflow: hidden;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.home__admin-banner-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.home__admin-banner-preview span {
  font-size: 11px;
  color: #888;
}

.home__admin-banner-fields {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.home__admin-banner-upload {
  display: inline-block;
  padding: 4px 10px;
  background: #333;
  color: #fff;
  font-size: 11px;
  cursor: pointer;
  width: fit-content;
  border-radius: 3px;
}

.home__admin-banner-upload input {
  display: none;
}

.home__featured {
  display: flex;
  gap: 20px;
  margin-top: 24px;
}

.home__featured-book {
  width: 415px;
  flex-shrink: 0;
}

.home__label-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.home__label {
  display: inline-block;
  font-size: 14px;
  font-weight: 700;
  padding: 4px 12px;
  background: #333;
  color: #fff;
}

.home__label-input {
  font-size: 14px;
  font-weight: 700;
  padding: 4px 12px;
  border: 2px solid #333;
  background: #fffde7;
  font-family: inherit;
}

.home__label-input:focus {
  outline: none;
  border-color: #e94560;
}

.home__section-remove {
  padding: 2px 6px;
  background: #fff;
  color: #c00;
  border: 1px solid #c00;
  font-size: 11px;
  cursor: pointer;
  border-radius: 3px;
}

.home__section-remove:hover {
  background: #c00;
  color: #fff;
}

.home__book-promo-link {
  display: flex;
  gap: 16px;
  text-decoration: none;
  color: inherit;
}

.home__book-promo-cover {
  width: 104px;
  height: 153px;
  flex-shrink: 0;
  background: #ddd;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #888;
  overflow: hidden;
}

.home__book-promo-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.home__book-promo-title {
  font-size: 16px;
  margin: 0 0 6px;
}

.home__book-promo-author,
.home__book-promo-price {
  font-size: 13px;
  color: #666;
  margin: 0 0 4px;
}

.home__book-selector {
  margin-top: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.home__selector-label {
  font-size: 12px;
  color: #666;
}

.home__selector-select {
  padding: 4px 8px;
  border: 1px solid #ccc;
  font-size: 12px;
  font-family: inherit;
  border-radius: 3px;
  max-width: 240px;
}

.home__featured-news {
  flex: 1;
  min-width: 0;
}

.home__news-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  border-bottom: 1px solid #ddd;
  padding-bottom: 6px;
  margin-bottom: 12px;
}

.home__news-title {
  font-size: 18px;
  margin: 0;
}

.home__news-more {
  font-size: 12px;
  color: #004b98;
  text-decoration: none;
}

.home__news-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.home__news-item {
  border-bottom: 1px solid #eee;
}

.home__news-link {
  display: flex;
  gap: 12px;
  padding: 10px 0;
  text-decoration: none;
  color: inherit;
}

.home__news-thumb {
  width: 64px;
  height: 84px;
  flex-shrink: 0;
  background: #ddd;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #888;
  overflow: hidden;
  font-size: 12px;
}

.home__news-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.home__news-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.home__news-item-title {
  font-size: 14px;
  font-weight: 600;
}

.home__news-item-desc {
  font-size: 12px;
  color: #666;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.home__section-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.home__add-section-btn {
  padding: 6px 14px;
  background: #1a1a2e;
  color: #fff;
  border: none;
  font-size: 12px;
  cursor: pointer;
  border-radius: 3px;
}

.home__add-section-btn:hover {
  background: #e94560;
}

.home__save-btn {
  padding: 6px 14px;
  background: #2a7;
  color: #fff;
  border: none;
  font-size: 12px;
  cursor: pointer;
  border-radius: 3px;
}

.home__save-btn:hover {
  background: #1a6;
}

.home__section-title {
  font-size: 20px;
  margin: 32px 0 16px;
  border-left: 4px solid #333;
  padding-left: 10px;
}

.home__edit-hint {
  font-size: 12px;
  font-weight: 400;
  color: #e94560;
  margin-left: 12px;
}

.home__book-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 20px;
}

.home__empty {
  color: #888;
}
</style>
