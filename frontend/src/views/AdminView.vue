<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useBooksStore } from '@/stores/books'
import { useArticlesStore } from '@/stores/articles'
import { useBannersStore } from '@/stores/banners'
import { useDownloadsStore } from '@/stores/downloads'
import { useSiteStore } from '@/stores/site'
import {
  fetchCategories,
  createBook, updateBook, deleteBook,
  createArticle, updateArticle, deleteArticle,
  createCategory, updateCategory, deleteCategory,
  createBanner, updateBanner, deleteBanner,
  createDownload, updateDownload, deleteDownload,
  updateSite,
  adminFetchNav, createNavItem, updateNavItem, deleteNavItem, reorderNavItems,
} from '@/api'
import type { Book, Article, Category, Banner, DownloadFile, SiteInfo, NavItem } from '@/types'
import ImageField from '@/components/ImageField.vue'

const auth = useAuthStore()
const router = useRouter()

// tabs
type Tab = 'nav' | 'books' | 'articles' | 'categories' | 'banners' | 'downloads' | 'site'
const activeTab = ref<Tab>('nav')

// Books
const books = useBooksStore()
const bookForm = ref<Partial<Book>>({})
const editingBook = ref<Book | null>(null)
const bookError = ref('')

// Articles
const articles = useArticlesStore()
const articleForm = ref<Partial<Article>>({})
const editingArticle = ref<Article | null>(null)
const articleError = ref('')

// Categories
const categories = ref<Category[]>([])
const categoryForm = ref<{ id?: string; name: string }>({ name: '' })
const editingCategory = ref<Category | null>(null)
const categoryError = ref('')

// Banners
const banners = useBannersStore()
const bannerForm = ref<Partial<Banner>>({})
const editingBanner = ref<Banner | null>(null)
const bannerError = ref('')

// Downloads
const downloads = useDownloadsStore()
const downloadForm = ref<Partial<DownloadFile>>({})
const editingDownload = ref<DownloadFile | null>(null)
const downloadError = ref('')

// Nav
const navItems = ref<NavItem[]>([])
const navForm = ref<Partial<NavItem>>({})
const editingNav = ref<NavItem | null>(null)
const navError = ref('')

// Site
const site = useSiteStore()
const siteForm = ref<Partial<SiteInfo>>({})
const siteError = ref('')

function setCompany(key: string, e: Event) {
  const value = (e.target as HTMLInputElement | HTMLTextAreaElement).value
  siteForm.value.company = { ...(siteForm.value.company || {}), [key]: value }
}

const saving = ref(false)

async function loadNavItems() {
  try {
    navItems.value = await adminFetchNav()
  } catch {
    navItems.value = []
  }
}

onMounted(async () => {
  if (!auth.isLoggedIn) {
    router.push('/admin/login')
    return
  }
  await Promise.all([
    books.loadBooks().catch(() => {}),
    articles.loadArticles({ pageSize: 100 }).catch(() => {}),
    banners.loadBanners().catch(() => {}),
    downloads.loadDownloads().catch(() => {}),
    site.loadSite().catch(() => {}),
    loadCategories().catch(() => {}),
    loadNavItems().catch(() => {}),
  ])
  if (site.info?.company) {
    siteForm.value = { ...site.info }
  }
})

async function loadCategories() {
  categories.value = await fetchCategories()
}

// Generic helpers
function startEdit<T extends { id: string }>(item: T, form: any, editing: any, clear: any) {
  editing.value = item
  form.value = { ...item }
  clear.value = ''
}

function cancelEdit(form: any, editing: any, clear: any) {
  editing.value = null
  form.value = {}
  clear.value = ''
}

// Books
async function saveBook() {
  bookError.value = ''
  saving.value = true
  try {
    if (editingBook.value?.id) {
      await updateBook(editingBook.value.id, bookForm.value)
    } else {
      await createBook(bookForm.value)
    }
    await books.loadBooks()
    cancelEdit(bookForm, editingBook, bookError)
  } catch (e) {
    bookError.value = e instanceof Error ? e.message : '保存に失敗しました'
  } finally {
    saving.value = false
  }
}

async function deleteBookAction(id: string) {
  if (!confirm('この書籍を削除しますか？')) return
  await deleteBook(id)
  await books.loadBooks()
}

// Articles
async function saveArticle() {
  articleError.value = ''
  saving.value = true
  try {
    if (editingArticle.value?.id) {
      await updateArticle(editingArticle.value.id, articleForm.value)
    } else {
      await createArticle(articleForm.value)
    }
    await articles.loadArticles({ pageSize: 100 })
    cancelEdit(articleForm, editingArticle, articleError)
  } catch (e) {
    articleError.value = e instanceof Error ? e.message : '保存に失敗しました'
  } finally {
    saving.value = false
  }
}

async function deleteArticleAction(id: string) {
  if (!confirm('この記事を削除しますか？')) return
  await deleteArticle(id)
  await articles.loadArticles({ pageSize: 100 })
}

// Categories
async function saveCategory() {
  categoryError.value = ''
  saving.value = true
  try {
    if (editingCategory.value?.id) {
      await updateCategory(editingCategory.value.id, categoryForm.value)
    } else {
      await createCategory(categoryForm.value)
    }
    await loadCategories()
    await books.loadCategories()
    cancelEdit(categoryForm, editingCategory, categoryError)
  } catch (e) {
    categoryError.value = e instanceof Error ? e.message : '保存に失敗しました'
  } finally {
    saving.value = false
  }
}

async function deleteCategoryAction(id: string) {
  if (!confirm('このカテゴリを削除しますか？')) return
  await deleteCategory(id)
  await loadCategories()
  await books.loadCategories()
}

// Banners
async function saveBanner() {
  bannerError.value = ''
  saving.value = true
  try {
    if (editingBanner.value?.id) {
      await updateBanner(editingBanner.value.id, bannerForm.value)
    } else {
      await createBanner(bannerForm.value)
    }
    await banners.loadBanners()
    cancelEdit(bannerForm, editingBanner, bannerError)
  } catch (e) {
    bannerError.value = e instanceof Error ? e.message : '保存に失敗しました'
  } finally {
    saving.value = false
  }
}

async function deleteBannerAction(id: string) {
  if (!confirm('このバナーを削除しますか？')) return
  await deleteBanner(id)
  await banners.loadBanners()
}

// Downloads
async function saveDownload() {
  downloadError.value = ''
  saving.value = true
  try {
    if (editingDownload.value?.id) {
      await updateDownload(editingDownload.value.id, downloadForm.value)
    } else {
      await createDownload(downloadForm.value)
    }
    await downloads.loadDownloads()
    cancelEdit(downloadForm, editingDownload, downloadError)
  } catch (e) {
    downloadError.value = e instanceof Error ? e.message : '保存に失敗しました'
  } finally {
    saving.value = false
  }
}

async function deleteDownloadAction(id: string) {
  if (!confirm('このダウンロードを削除しますか？')) return
  await deleteDownload(id)
  await downloads.loadDownloads()
}

// Nav
async function saveNav() {
  navError.value = ''
  saving.value = true
  try {
    if (editingNav.value?.id) {
      await updateNavItem(editingNav.value.id, navForm.value)
    } else {
      await createNavItem(navForm.value)
    }
    await loadNavItems()
    cancelEdit(navForm, editingNav, navError)
  } catch (e) {
    navError.value = e instanceof Error ? e.message : '保存に失敗しました'
  } finally {
    saving.value = false
  }
}

async function deleteNavAction(id: string) {
  if (!confirm('このナビ項目を削除しますか？')) return
  await deleteNavItem(id)
  await loadNavItems()
}

async function moveNav(item: NavItem, direction: -1 | 1) {
  const sorted = [...navItems.value].sort((a, b) => a.order - b.order)
  const idx = sorted.findIndex((n) => n.id === item.id)
  const swapIdx = idx + direction
  if (idx < 0 || swapIdx < 0 || swapIdx >= sorted.length) return
  const updates = sorted.map((n, i) => {
    if (i === idx) return { id: n.id, order: sorted[swapIdx].order }
    if (i === swapIdx) return { id: n.id, order: sorted[idx].order }
    return { id: n.id, order: n.order }
  })
  await reorderNavItems(updates)
  await loadNavItems()
}

async function toggleNavVisible(item: NavItem) {
  await updateNavItem(item.id, { ...item, visible: !item.visible })
  await loadNavItems()
}

// Site
async function saveSite() {
  siteError.value = ''
  saving.value = true
  try {
    await updateSite(siteForm.value)
    await site.loadSite()
    siteError.value = '保存しました'
    setTimeout(() => (siteError.value = ''), 2000)
  } catch (e) {
    siteError.value = e instanceof Error ? e.message : '保存に失敗しました'
  } finally {
    saving.value = false
  }
}

// Category names for select
type CategoryOption = { value: string; label: string }
const categoryOptions = computed<CategoryOption[]>(() =>
  categories.value.map((c) => ({ value: c.id, label: c.name })),
)

// Nav
const sortedNavItems = computed(() =>
  [...navItems.value].sort((a, b) => a.order - b.order),
)
const navModel = computed({
  get() {
    return navForm.value.visible !== false
  },
  set(val: boolean) {
    navForm.value = { ...navForm.value, visible: val }
  },
})

// Featured toggle helpers for select elements
const featuredBookModel = computed({
  get() {
    return bookForm.value.featured ? 'true' : 'false'
  },
  set(val: string) {
    bookForm.value = { ...bookForm.value, featured: val === 'true' }
  },
})
const featuredArticleModel = computed({
  get() {
    return articleForm.value.featured ? 'true' : 'false'
  },
  set(val: string) {
    articleForm.value = { ...articleForm.value, featured: val === 'true' }
  },
})
</script>

<template>
  <div class="admin">
    <header class="admin__header">
      <nav class="admin__tabs" role="tablist">
        <button role="tab" :class="{ active: activeTab === 'nav' }" @click="activeTab = 'nav'">ナビ</button>
        <button role="tab" :class="{ active: activeTab === 'books' }" @click="activeTab = 'books'">書籍</button>
        <button role="tab" :class="{ active: activeTab === 'articles' }" @click="activeTab = 'articles'">コラム</button>
        <button role="tab" :class="{ active: activeTab === 'categories' }" @click="activeTab = 'categories'">カテゴリ</button>
        <button role="tab" :class="{ active: activeTab === 'banners' }" @click="activeTab = 'banners'">バナー</button>
        <button role="tab" :class="{ active: activeTab === 'downloads' }" @click="activeTab = 'downloads'">ダウンロード</button>
        <button role="tab" :class="{ active: activeTab === 'site' }" @click="activeTab = 'site'">会社概要</button>
      </nav>
    </header>

    <main class="admin__content">
      <!-- Nav -->
      <section v-if="activeTab === 'nav'" class="admin__panel">
        <div class="admin__panel-head">
          <h2>ナビ管理</h2>
          <button class="admin__btn admin__btn--primary" @click="startEdit({} as NavItem, navForm, editingNav, navError)">新規作成</button>
        </div>

        <form v-if="editingNav" class="admin__form" @submit.prevent="saveNav">
          <div class="admin__grid">
            <div class="admin__field">
              <label>ID</label>
              <input v-model="navForm.id" :disabled="!!editingNav.id" placeholder="nav1" />
            </div>
            <div class="admin__field">
              <label>表示順</label>
              <input v-model.number="navForm.order" type="number" />
            </div>
            <div class="admin__field">
              <label>ラベル</label>
              <input v-model="navForm.label" placeholder="例：ホーム" />
            </div>
            <div class="admin__field">
              <label>リンク先</label>
              <input v-model="navForm.to" placeholder="例：/sy" />
            </div>
            <div class="admin__field">
              <label>表示</label>
              <select v-model="navModel">
                <option :value="true">表示する</option>
                <option :value="false">非表示</option>
              </select>
            </div>
          </div>
          <div class="admin__form-actions">
            <button type="button" class="admin__btn" @click="cancelEdit(navForm, editingNav, navError)">キャンセル</button>
            <button type="submit" class="admin__btn admin__btn--primary" :disabled="saving">{{ saving ? '保存中…' : (editingNav.id ? '更新' : '作成') }}</button>
          </div>
          <p v-if="navError" class="admin__error">{{ navError }}</p>
        </form>

        <table class="admin__table" v-else>
          <thead>
            <tr>
              <th>順序</th>
              <th>ラベル</th>
              <th>リンク</th>
              <th>表示</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in sortedNavItems" :key="item.id" :class="{ 'admin__row--hidden': !item.visible }">
              <td>{{ item.order }}</td>
              <td>{{ item.label }}</td>
              <td>{{ item.to }}</td>
              <td>
                <button class="admin__visibility" :class="{ 'admin__visibility--off': !item.visible }" @click="toggleNavVisible(item)">
                  {{ item.visible ? '表示中' : '非表示' }}
                </button>
              </td>
              <td>
                <button class="admin__action" @click="moveNav(item, -1)">▲</button>
                <button class="admin__action" @click="moveNav(item, 1)">▼</button>
                <button class="admin__action" @click="startEdit(item, navForm, editingNav, navError)">編集</button>
                <button class="admin__action admin__action--danger" @click="deleteNavAction(item.id)">削除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <!-- Books -->
      <section v-if="activeTab === 'books'" class="admin__panel">
        <div class="admin__panel-head">
          <h2>書籍管理</h2>
          <button class="admin__btn admin__btn--primary" @click="startEdit({} as Book, bookForm, editingBook, bookError)">新規作成</button>
        </div>

        <form v-if="editingBook" class="admin__form" @submit.prevent="saveBook">
          <div class="admin__grid">
            <div class="admin__field">
              <label>ID</label>
              <input v-model="bookForm.id" :disabled="!!editingBook.id" />
            </div>
            <div class="admin__field">
              <label>カテゴリ</label>
              <select v-model="bookForm.category">
                <option v-for="c in categoryOptions" :key="c.value" :value="c.value">{{ c.label }}</option>
              </select>
            </div>
            <div class="admin__field">
              <label>タイトル</label>
              <input v-model="bookForm.title" />
            </div>
            <div class="admin__field">
              <label>著者</label>
              <input v-model="bookForm.author" />
            </div>
            <div class="admin__field">
              <label>価格</label>
              <input v-model.number="bookForm.price" type="number" />
            </div>
            <div class="admin__field">
              <label>ISBN</label>
              <input v-model="bookForm.isbn" />
            </div>
            <div class="admin__field">
              <label>発行日</label>
              <input v-model="bookForm.publishDate" type="date" />
            </div>
            <div class="admin__field">
              <label>販売中</label>
              <select v-model="bookForm.onSale">
                <option :value="true">はい</option>
                <option :value="false">いいえ</option>
              </select>
            </div>
            <div class="admin__field">
              <label>並び順</label>
              <input v-model.number="bookForm.sortWeight" type="number" />
            </div>
            <div class="admin__field">
              <label>ホームおすすめ</label>
              <select v-model="featuredBookModel">
                <option value="true">はい</option>
                <option value="false">いいえ</option>
              </select>
            </div>
          </div>
          <div class="admin__field admin__field--full">
            <label>説明</label>
            <textarea v-model="bookForm.description" rows="4"></textarea>
          </div>
          <div class="admin__field admin__field--full">
            <label>Amazon URL</label>
            <input v-model="bookForm.amazonUrl" type="url" />
          </div>
          <ImageField v-model="bookForm.cover" label="表紙画像" />
          <div class="admin__form-actions">
            <button type="button" class="admin__btn" @click="cancelEdit(bookForm, editingBook, bookError)">キャンセル</button>
            <button type="submit" class="admin__btn admin__btn--primary" :disabled="saving">{{ saving ? '保存中…' : (editingBook.id ? '更新' : '作成') }}</button>
          </div>
          <p v-if="bookError" class="admin__error">{{ bookError }}</p>
        </form>

        <table class="admin__table" v-else>
          <thead>
            <tr>
              <th>表紙</th>
              <th>ID</th>
              <th>タイトル</th>
              <th>著者</th>
              <th>カテゴリ</th>
              <th>価格</th>
              <th>販売中</th>
              <th>おすすめ</th>
              <th>並び順</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="b in books.books" :key="b.id">
              <td><img v-if="b.cover" :src="b.cover" alt="" style="height:40px" /></td>
              <td>{{ b.id }}</td>
              <td>{{ b.title }}</td>
              <td>{{ b.author }}</td>
              <td>{{ categoryOptions.find((c) => c.value === b.category)?.label || b.category }}</td>
              <td>¥{{ b.price }}</td>
              <td>{{ b.onSale ? '○' : '×' }}</td>
              <td>{{ b.featured ? '★' : '' }}</td>
              <td>{{ b.sortWeight }}</td>
              <td>
                <button class="admin__action" @click="startEdit(b, bookForm, editingBook, bookError)">編集</button>
                <button class="admin__action admin__action--danger" @click="deleteBookAction(b.id)">削除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <!-- Articles -->
      <section v-if="activeTab === 'articles'" class="admin__panel">
        <div class="admin__panel-head">
          <h2>コラム管理</h2>
          <button class="admin__btn admin__btn--primary" @click="startEdit({} as Article, articleForm, editingArticle, articleError)">新規作成</button>
        </div>

        <form v-if="editingArticle" class="admin__form" @submit.prevent="saveArticle">
          <div class="admin__grid">
            <div class="admin__field">
              <label>ID</label>
              <input v-model="articleForm.id" :disabled="!!editingArticle.id" />
            </div>
            <div class="admin__field">
              <label>カテゴリ</label>
              <select v-model="articleForm.category">
                <option v-for="c in categoryOptions" :key="c.value" :value="c.value">{{ c.label }}</option>
              </select>
            </div>
            <div class="admin__field">
              <label>タイトル</label>
              <input v-model="articleForm.title" />
            </div>
            <div class="admin__field">
              <label>公開日</label>
              <input v-model="articleForm.publishedAt" type="date" />
            </div>
            <div class="admin__field">
              <label>並び順</label>
              <input v-model.number="articleForm.sortWeight" type="number" />
            </div>
            <div class="admin__field">
              <label>ホームおすすめ</label>
              <select v-model="featuredArticleModel">
                <option value="true">はい</option>
                <option value="false">いいえ</option>
              </select>
            </div>
          </div>
          <div class="admin__field admin__field--full">
            <label>概要</label>
            <textarea v-model="articleForm.excerpt" rows="2"></textarea>
          </div>
          <div class="admin__field admin__field--full">
            <label>本文</label>
            <textarea v-model="articleForm.body" rows="6"></textarea>
          </div>
          <ImageField v-model="articleForm.cover" label="サムネイル" />
          <div class="admin__form-actions">
            <button type="button" class="admin__btn" @click="cancelEdit(articleForm, editingArticle, articleError)">キャンセル</button>
            <button type="submit" class="admin__btn admin__btn--primary" :disabled="saving">{{ saving ? '保存中…' : (editingArticle.id ? '更新' : '作成') }}</button>
          </div>
          <p v-if="articleError" class="admin__error">{{ articleError }}</p>
        </form>

        <table class="admin__table" v-else>
          <thead>
            <tr><th>サムネイル</th><th>ID</th><th>タイトル</th><th>カテゴリ</th><th>公開日</th><th>おすすめ</th><th>並び順</th><th>操作</th></tr>
          </thead>
          <tbody>
            <tr v-for="a in articles.articles" :key="a.id">
              <td><img v-if="a.cover" :src="a.cover" alt="" style="height:40px" /></td>
              <td>{{ a.id }}</td>
              <td>{{ a.title }}</td>
              <td>{{ categoryOptions.find((c) => c.value === a.category)?.label || a.category }}</td>
              <td>{{ a.publishedAt }}</td>
              <td>{{ a.featured ? '★' : '' }}</td>
              <td>{{ a.sortWeight }}</td>
              <td>
                <button class="admin__action" @click="startEdit(a, articleForm, editingArticle, articleError)">編集</button>
                <button class="admin__action admin__action--danger" @click="deleteArticleAction(a.id)">削除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <!-- Categories -->
      <section v-if="activeTab === 'categories'" class="admin__panel">
        <div class="admin__panel-head">
          <h2>カテゴリ管理</h2>
          <button class="admin__btn admin__btn--primary" @click="startEdit({ id: '', name: '' } as Category, categoryForm, editingCategory, categoryError)">新規作成</button>
        </div>

        <form v-if="editingCategory" class="admin__form admin__form--narrow" @submit.prevent="saveCategory">
          <div class="admin__field">
            <label>ID</label>
            <input v-model="categoryForm.id" :disabled="!!editingCategory.id" />
          </div>
          <div class="admin__field">
            <label>名称</label>
            <input v-model="categoryForm.name" required />
          </div>
          <div class="admin__form-actions">
            <button type="button" class="admin__btn" @click="cancelEdit(categoryForm, editingCategory, categoryError)">キャンセル</button>
            <button type="submit" class="admin__btn admin__btn--primary" :disabled="saving">{{ saving ? '保存中…' : (editingCategory.id ? '更新' : '作成') }}</button>
          </div>
          <p v-if="categoryError" class="admin__error">{{ categoryError }}</p>
        </form>

        <table class="admin__table" v-else>
          <thead><tr><th>ID</th><th>名称</th><th>操作</th></tr></thead>
          <tbody>
            <tr v-for="c in categories" :key="c.id">
              <td>{{ c.id }}</td>
              <td>{{ c.name }}</td>
              <td>
                <button class="admin__action" @click="startEdit(c, categoryForm, editingCategory, categoryError)">編集</button>
                <button class="admin__action admin__action--danger" @click="deleteCategoryAction(c.id)">削除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <!-- Banners -->
      <section v-if="activeTab === 'banners'" class="admin__panel">
        <div class="admin__panel-head">
          <h2>バナー管理</h2>
          <button class="admin__btn admin__btn--primary" @click="startEdit({} as Banner, bannerForm, editingBanner, bannerError)">新規作成</button>
        </div>

        <form v-if="editingBanner" class="admin__form" @submit.prevent="saveBanner">
          <div class="admin__grid">
            <div class="admin__field">
              <label>ID</label>
              <input v-model="bannerForm.id" :disabled="!!editingBanner.id" />
            </div>
            <div class="admin__field">
              <label>並び順（sortWeight）</label>
              <input v-model.number="bannerForm.sortWeight" type="number" />
            </div>
            <div class="admin__field">
              <label>タイトル</label>
              <input v-model="bannerForm.title" />
            </div>
            <div class="admin__field">
              <label>リンク</label>
              <input v-model="bannerForm.link" />
            </div>
          </div>
          <ImageField v-model="bannerForm.image" label="バナー画像" />
          <div class="admin__form-actions">
            <button type="button" class="admin__btn" @click="cancelEdit(bannerForm, editingBanner, bannerError)">キャンセル</button>
            <button type="submit" class="admin__btn admin__btn--primary" :disabled="saving">{{ saving ? '保存中…' : (editingBanner.id ? '更新' : '作成') }}</button>
          </div>
          <p v-if="bannerError" class="admin__error">{{ bannerError }}</p>
        </form>

        <table class="admin__table" v-else>
          <thead><tr><th>画像</th><th>ID</th><th>タイトル</th><th>リンク</th><th>順序</th><th>操作</th></tr></thead>
          <tbody>
            <tr v-for="b in banners.banners" :key="b.id">
              <td><img v-if="b.image" :src="b.image" alt="" style="height:40px" /></td>
              <td>{{ b.id }}</td>
              <td>{{ b.title }}</td>
              <td>{{ b.link }}</td>
              <td>{{ b.order }}</td>
              <td>
                <button class="admin__action" @click="startEdit(b, bannerForm, editingBanner, bannerError)">編集</button>
                <button class="admin__action admin__action--danger" @click="deleteBannerAction(b.id)">削除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <!-- Downloads -->
      <section v-if="activeTab === 'downloads'" class="admin__panel">
        <div class="admin__panel-head">
          <h2>ダウンロード管理</h2>
          <button class="admin__btn admin__btn--primary" @click="startEdit({} as DownloadFile, downloadForm, editingDownload, downloadError)">新規作成</button>
        </div>

        <form v-if="editingDownload" class="admin__form" @submit.prevent="saveDownload">
          <div class="admin__grid">
            <div class="admin__field">
              <label>ID</label>
              <input v-model="downloadForm.id" :disabled="!!editingDownload.id" />
            </div>
            <div class="admin__field">
              <label>名称</label>
              <input v-model="downloadForm.name" />
            </div>
            <div class="admin__field">
              <label>URL</label>
              <input v-model="downloadForm.url" />
            </div>
            <div class="admin__field">
              <label>公開日</label>
              <input v-model="downloadForm.publishedAt" type="date" />
            </div>
          </div>
          <div class="admin__field admin__field--full">
            <label>説明</label>
            <textarea v-model="downloadForm.description" rows="3"></textarea>
          </div>
          <div class="admin__field admin__field--full">
            <label>ファイルサイズ</label>
            <input v-model="downloadForm.size" />
          </div>
          <div class="admin__form-actions">
            <button type="button" class="admin__btn" @click="cancelEdit(downloadForm, editingDownload, downloadError)">キャンセル</button>
            <button type="submit" class="admin__btn admin__btn--primary" :disabled="saving">{{ saving ? '保存中…' : (editingDownload.id ? '更新' : '作成') }}</button>
          </div>
          <p v-if="downloadError" class="admin__error">{{ downloadError }}</p>
        </form>

        <table class="admin__table" v-else>
          <thead><tr><th>ID</th><th>名称</th><th>URL</th><th>サイズ</th><th>公開日</th><th>操作</th></tr></thead>
          <tbody>
            <tr v-for="d in downloads.downloads" :key="d.id">
              <td>{{ d.id }}</td>
              <td>{{ d.name }}</td>
              <td>{{ d.url }}</td>
              <td>{{ d.size }}</td>
              <td>{{ d.publishedAt }}</td>
              <td>
                <button class="admin__action" @click="startEdit(d, downloadForm, editingDownload, downloadError)">編集</button>
                <button class="admin__action admin__action--danger" @click="deleteDownloadAction(d.id)">削除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <!-- Site / Company -->
      <section v-if="activeTab === 'site'" class="admin__panel">
        <div class="admin__panel-head"><h2>会社概要・サイト設定</h2></div>
        <form class="admin__form" @submit.prevent="saveSite">
          <h3 style="margin:0 0 16px; font-size:15px;">基本情報</h3>
          <div class="admin__grid">
            <div class="admin__field"><label>サイト名</label><input v-model="siteForm.name" /></div>
            <div class="admin__field"><label>Twitter URL</label><input v-model="siteForm.twitterUrl" type="url" /></div>
            <div class="admin__field"><label>メール</label><input v-model="siteForm.email" type="email" /></div>
            <div class="admin__field"><label>電話</label><input v-model="siteForm.phone" /></div>
          </div>
          <ImageField v-model="siteForm.logoUrl" label="ロゴ画像" />
          <div class="admin__field admin__field--full"><label>紹介文</label><textarea v-model="siteForm.intro" rows="3"></textarea></div>
          <div class="admin__field admin__field--full"><label>住所</label><input v-model="siteForm.address" /></div>

          <h3 style="margin:24px 0 16px; font-size:15px; border-top:1px solid #eee; padding-top:16px;">会社情報</h3>
          <div class="admin__grid">
            <div class="admin__field"><label>英文社名</label><input :value="siteForm.company?.englishName || ''" @input="setCompany('englishName', $event)" /></div>
            <div class="admin__field"><label>ホームページ</label><input :value="siteForm.company?.homepageUrl || ''" type="url" @input="setCompany('homepageUrl', $event)" /></div>
          </div>
          <div class="admin__field admin__field--full"><label>所在地</label><input :value="siteForm.company?.address || ''" @input="setCompany('address', $event)" /></div>
          <div class="admin__field admin__field--full"><label>アクセス</label><input :value="siteForm.company?.access || ''" @input="setCompany('access', $event)" /></div>
          <div class="admin__field admin__field--full"><label>設立</label><input :value="siteForm.company?.established || ''" @input="setCompany('established', $event)" /></div>
          <div class="admin__field admin__field--full"><label>連絡所</label><input :value="siteForm.company?.contactOffice || ''" @input="setCompany('contactOffice', $event)" /></div>
          <div class="admin__field admin__field--full"><label>代表者</label><input :value="siteForm.company?.representative || ''" @input="setCompany('representative', $event)" /></div>
          <div class="admin__field admin__field--full"><label>事業内容</label><textarea :value="siteForm.company?.business || ''" rows="4" @input="setCompany('business', $event)"></textarea></div>

          <div class="admin__form-actions">
            <button type="submit" class="admin__btn admin__btn--primary" :disabled="saving">{{ saving ? '保存中…' : '保存' }}</button>
          </div>
          <p v-if="siteError" :class="['admin__msg', siteError === '保存しました' ? 'admin__success' : 'admin__error']">{{ siteError }}</p>
        </form>
      </section>
    </main>
  </div>
</template>

<style scoped>
.admin__header {
  border-bottom: 1px solid #eee;
  background: #fff;
  position: sticky;
  top: 0;
  z-index: 10;
}

.admin__tabs {
  display: flex;
  gap: 2px;
  padding: 0 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.admin__tabs button {
  padding: 12px 20px;
  border: none;
  background: none;
  color: #666;
  font-size: 14px;
  cursor: pointer;
  border-bottom: 3px solid transparent;
  font-family: inherit;
}

.admin__tabs button:hover {
  color: #333;
  background: #fafafa;
}

.admin__tabs button.active {
  color: #333;
  border-bottom-color: #333;
  font-weight: 700;
}

.admin__content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 0 0;
}

.admin__panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.admin__panel-head h2 {
  font-size: 20px;
  margin: 0;
  border-left: 4px solid #333;
  padding-left: 10px;
}

.admin__form {
  background: #fff;
  border: 1px solid #eee;
  padding: 24px;
  margin-bottom: 24px;
}

.admin__form--narrow {
  max-width: 480px;
}

.admin__grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

@media (max-width: 700px) {
  .admin__grid {
    grid-template-columns: 1fr;
  }
}

.admin__field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.admin__field--full {
  grid-column: 1 / -1;
}

.admin__field label {
  font-size: 13px;
  color: #333;
  font-weight: 600;
}

.admin__field input,
.admin__field select,
.admin__field textarea {
  padding: 9px 10px;
  border: 1px solid #ccc;
  font: inherit;
  font-size: 14px;
  box-sizing: border-box;
  width: 100%;
}

.admin__field input:focus,
.admin__field select:focus,
.admin__field textarea:focus {
  outline: none;
  border-color: #004b98;
}

.admin__form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.admin__btn {
  padding: 10px 22px;
  border: none;
  font-size: 14px;
  cursor: pointer;
  font-family: inherit;
}

.admin__btn--primary {
  background: #333;
  color: #fff;
}

.admin__btn--primary:hover:not(:disabled) {
  background: #000;
}

.admin__btn:not(.admin__btn--primary) {
  background: #fafafa;
  border: 1px solid #ddd;
  color: #333;
}

.admin__btn:not(.admin__btn--primary):hover:not(:disabled) {
  background: #f0f0f0;
}

.admin__btn:disabled {
  opacity: 0.6;
  cursor: default;
}

.admin__error {
  color: #c00;
  font-size: 13px;
  margin-top: 8px;
}

.admin__msg {
  font-size: 13px;
  margin-top: 8px;
}

.admin__success {
  color: #2a7;
}

.admin__table {
  width: 100%;
  border-collapse: collapse;
  background: #fff;
  border: 1px solid #eee;
}

.admin__table th,
.admin__table td {
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
  text-align: left;
  font-size: 13px;
}

.admin__table th {
  background: #fafafa;
  font-weight: 700;
  color: #333;
}

.admin__table tr:last-child td {
  border-bottom: none;
}

.admin__action {
  margin-right: 8px;
  padding: 5px 12px;
  font-size: 12px;
  border: 1px solid #ddd;
  background: #fff;
  color: #333;
  cursor: pointer;
}

.admin__action:hover {
  border-color: #999;
}

.admin__action--danger {
  color: #c00;
  border-color: #fcc;
}

.admin__action--danger:hover {
  background: #fff0f0;
  border-color: #c00;
  color: #c00;
}

.admin__visibility {
  padding: 4px 10px;
  font-size: 12px;
  border: 1px solid #2a7;
  background: #f0fff4;
  color: #2a7;
  cursor: pointer;
}

.admin__visibility--off {
  border-color: #ccc;
  background: #fafafa;
  color: #999;
}

.admin__row--hidden {
  opacity: 0.5;
}
</style>