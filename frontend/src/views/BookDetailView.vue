<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useBooksStore } from '@/stores/books'
import { useAuthStore } from '@/stores/auth'
import { updateBook, uploadImage } from '@/api'
import type { Book } from '@/types'
import InlineEdit from '@/components/InlineEdit.vue'

const route = useRoute()
const books = useBooksStore()
const auth = useAuthStore()

const book = ref<Book | null>(null)
const notFound = ref(false)
const saving = ref(false)
const saveMsg = ref('')
const uploadRef = ref<HTMLInputElement | null>(null)

const bookId = computed(() => String(route.params.id))

const categoryName = computed(() => {
  if (!book.value) return ''
  const cat = books.categories.find((c) => c.id === book.value!.category)
  return cat?.name ?? book.value.category
})

const index = computed(() =>
  books.books.findIndex((b) => b.id === bookId.value),
)
const prevBook = computed(() =>
  index.value > 0 ? books.books[index.value - 1] : null,
)
const nextBook = computed(() =>
  index.value >= 0 && index.value < books.books.length - 1
    ? books.books[index.value + 1]
    : null,
)

async function load(id: string) {
  notFound.value = false
  book.value = null
  const [detail] = await Promise.all([
    books.loadBook(id),
    books.loadBooks(),
    books.loadCategories(),
  ])
  if (!detail) {
    notFound.value = true
    return
  }
  book.value = detail
}

async function saveField(field: string, value: string | number | boolean) {
  if (!book.value) return
  saving.value = true
  saveMsg.value = ''
  try {
    const updated = await updateBook(book.value.id, { [field]: value })
    book.value = { ...book.value, ...updated }
    saveMsg.value = '保存しました'
    setTimeout(() => (saveMsg.value = ''), 2000)
  } catch {
    saveMsg.value = '保存に失敗しました'
  } finally {
    saving.value = false
  }
}

async function onCoverChange(file: File) {
  if (!book.value) return
  saving.value = true
  saveMsg.value = ''
  try {
    const res = await uploadImage(file)
    const updated = await updateBook(book.value.id, { cover: res.url })
    book.value = { ...book.value, ...updated }
    saveMsg.value = '表紙を更新しました'
    setTimeout(() => (saveMsg.value = ''), 2000)
  } catch {
    saveMsg.value = 'アップロードに失敗しました'
  } finally {
    saving.value = false
  }
}

onMounted(() => load(bookId.value))
watch(
  () => route.params.id,
  (id) => {
    if (typeof id === 'string') load(id)
  },
)
</script>

<template>
  <section class="book-detail">
    <RouterLink class="book-detail__back" to="/books">‹ 書籍一覧へ</RouterLink>

    <p v-if="notFound" class="book-detail__empty">書籍が見つかりませんでした。</p>

    <template v-else-if="book">
      <!-- Admin save status -->
      <div v-if="auth.isLoggedIn && auth.editing" class="book-detail__save-status">
        <span v-if="saving">保存中…</span>
        <span v-else-if="saveMsg" class="book-detail__save-success">{{ saveMsg }}</span>
      </div>

      <div class="book-detail__main">
        <div class="book-detail__cover">
          <img v-if="book.cover" :src="book.cover" :alt="book.title" />
          <span v-else>封面占位</span>
          <!-- Admin cover upload -->
          <label v-if="auth.editing" class="book-detail__cover-upload">
            <input
              ref="uploadRef"
              type="file"
              accept="image/*"
              @change="(e) => {
                const t = e.target as HTMLInputElement
                if (t.files?.[0]) onCoverChange(t.files[0])
              }"
            />
            <span>表紙を変更</span>
          </label>
        </div>

        <div class="book-detail__info">
          <span v-if="categoryName" class="book-detail__tag">{{ categoryName }}</span>
          <h1 class="book-detail__title">
            <InlineEdit
              :model-value="book.title"
              :editing="auth.editing"
              placeholder="タイトル"
              @save="(v) => saveField('title', v)"
            />
          </h1>
          <p class="book-detail__author">
            <InlineEdit
              :model-value="book.author || ''"
              :editing="auth.editing"
              placeholder="著者"
              @save="(v) => saveField('author', v)"
            />
          </p>

          <dl class="book-detail__meta">
            <div class="book-detail__meta-row">
              <dt>価格</dt>
              <dd>
                ¥<InlineEdit
                  :model-value="String(book.price || 0)"
                  :editing="auth.editing"
                  placeholder="価格"
                  @save="(v) => saveField('price', Number(v) || 0)"
                />（税込）
              </dd>
            </div>
            <div class="book-detail__meta-row">
              <dt>ISBN</dt>
              <dd>
                <InlineEdit
                  :model-value="book.isbn || ''"
                  :editing="auth.editing"
                  placeholder="ISBN"
                  @save="(v) => saveField('isbn', v)"
                />
              </dd>
            </div>
            <div class="book-detail__meta-row">
              <dt>発行日</dt>
              <dd>
                <InlineEdit
                  :model-value="book.publishDate || ''"
                  :editing="auth.editing"
                  placeholder="YYYY-MM-DD"
                  @save="(v) => saveField('publishDate', v)"
                />
              </dd>
            </div>
            <div class="book-detail__meta-row">
              <dt>カテゴリ</dt>
              <dd>{{ categoryName }}</dd>
            </div>
          </dl>

          <div v-if="auth.editing" class="book-detail__field">
            <label class="book-detail__field-label">説明</label>
            <InlineEdit
              :model-value="book.description || ''"
              :editing="auth.editing"
              tag="textarea"
              placeholder="書籍の説明を入力"
              @save="(v) => saveField('description', v)"
            />
          </div>
          <p v-else-if="book.description" class="book-detail__desc">
            {{ book.description }}
          </p>

          <div v-if="auth.editing" class="book-detail__field">
            <label class="book-detail__field-label">Amazon URL</label>
            <InlineEdit
              :model-value="book.amazonUrl || ''"
              :editing="auth.editing"
              placeholder="https://..."
              @save="(v) => saveField('amazonUrl', v)"
            />
          </div>
          <a
            v-else-if="book.amazonUrl"
            class="book-detail__buy"
            :href="book.amazonUrl"
            target="_blank"
            rel="noopener"
          >
            購入はこちら（Amazon / 販売サイト）
          </a>
        </div>
      </div>

      <section v-if="book.sampleImages && book.sampleImages.length" class="book-detail__samples">
        <h2 class="book-detail__section-title">立ち読み</h2>
        <div class="book-detail__sample-grid">
          <img
            v-for="(src, i) in book.sampleImages"
            :key="i"
            class="book-detail__sample"
            :src="src"
            :alt="`${book.title} 立ち読み ${i + 1}`"
          />
        </div>
      </section>

      <nav class="book-detail__pager" aria-label="前後の書籍">
        <RouterLink v-if="prevBook" class="book-detail__nav" :to="`/book/${prevBook.id}`">
          <span class="book-detail__nav-label">前の書籍</span>
          <span class="book-detail__nav-title">{{ prevBook.title }}</span>
        </RouterLink>
        <span v-else></span>
        <RouterLink v-if="nextBook" class="book-detail__nav book-detail__nav--next" :to="`/book/${nextBook.id}`">
          <span class="book-detail__nav-label">次の書籍</span>
          <span class="book-detail__nav-title">{{ nextBook.title }}</span>
        </RouterLink>
      </nav>
    </template>

    <p v-else class="book-detail__empty">書籍を読み込み中…（占位）</p>
  </section>
</template>

<style scoped>
.book-detail__back {
  display: inline-block;
  font-size: 13px;
  color: #004b98;
  text-decoration: none;
  margin: 8px 0 20px;
}

.book-detail__back:hover {
  color: #000;
}

.book-detail__save-status {
  text-align: right;
  padding: 4px 0 8px;
  font-size: 12px;
  min-height: 20px;
}

.book-detail__save-success {
  color: #2a7;
}

.book-detail__main {
  display: flex;
  gap: 32px;
}

.book-detail__cover {
  width: 300px;
  flex-shrink: 0;
  aspect-ratio: 3 / 4;
  background: #ddd;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #888;
  overflow: hidden;
  position: relative;
}

.book-detail__cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.book-detail__cover-upload {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
  text-align: center;
  padding: 8px;
  font-size: 12px;
  cursor: pointer;
}

.book-detail__cover-upload:hover {
  background: rgba(0, 0, 0, 0.85);
}

.book-detail__cover-upload input {
  display: none;
}

.book-detail__info {
  flex: 1;
  min-width: 0;
}

.book-detail__tag {
  display: inline-block;
  font-size: 12px;
  color: #004b98;
  border: 1px solid #004b98;
  padding: 2px 10px;
  margin-bottom: 12px;
}

.book-detail__title {
  font-size: 26px;
  margin: 0 0 8px;
  line-height: 1.4;
}

.book-detail__author {
  font-size: 15px;
  color: #555;
  margin: 0 0 20px;
}

.book-detail__meta {
  margin: 0 0 20px;
  border-top: 1px solid #eee;
}

.book-detail__meta-row {
  display: flex;
  gap: 16px;
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}

.book-detail__meta-row dt {
  width: 80px;
  flex-shrink: 0;
  font-size: 12px;
  color: #999;
}

.book-detail__meta-row dd {
  margin: 0;
  font-size: 13px;
  color: #333;
}

.book-detail__desc {
  font-size: 14px;
  line-height: 1.9;
  color: #333;
  margin: 0 0 24px;
  white-space: pre-wrap;
}

.book-detail__field {
  margin-bottom: 16px;
}

.book-detail__field-label {
  display: block;
  font-size: 12px;
  color: #999;
  margin-bottom: 4px;
  font-weight: 600;
}

.book-detail__buy {
  display: inline-block;
  background: #004b98;
  color: #fff;
  font-size: 15px;
  font-weight: 700;
  padding: 12px 28px;
  text-decoration: none;
}

.book-detail__buy:hover {
  background: #003a78;
}

.book-detail__section-title {
  font-size: 20px;
  margin: 40px 0 16px;
  border-left: 4px solid #333;
  padding-left: 10px;
}

.book-detail__sample-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.book-detail__sample {
  width: 100%;
  aspect-ratio: 3 / 4;
  object-fit: cover;
  background: #ddd;
}

.book-detail__pager {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-top: 48px;
  border-top: 1px solid #eee;
  padding-top: 20px;
}

.book-detail__nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
  text-decoration: none;
  color: #004b98;
  max-width: 48%;
}

.book-detail__nav--next {
  text-align: right;
  align-items: flex-end;
}

.book-detail__nav-label {
  font-size: 11px;
  color: #999;
}

.book-detail__nav-title {
  font-size: 14px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-detail__nav:hover .book-detail__nav-title {
  color: #000;
}

.book-detail__empty {
  color: #888;
  padding: 24px 0;
}
</style>
