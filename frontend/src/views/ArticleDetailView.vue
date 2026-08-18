<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useArticlesStore } from '@/stores/articles'
import { useAuthStore } from '@/stores/auth'
import { updateArticle, uploadImage } from '@/api'
import type { Article } from '@/types'
import InlineEdit from '@/components/InlineEdit.vue'

const route = useRoute()
const articles = useArticlesStore()
const auth = useAuthStore()

const article = ref<Article | null>(null)
const notFound = ref(false)
const saving = ref(false)
const saveMsg = ref('')

async function load(id: string) {
  notFound.value = false
  article.value = null
  const res = await articles.loadArticle(id)
  if (!res) {
    notFound.value = true
    return
  }
  article.value = res
}

async function saveField(field: string, value: string) {
  if (!article.value) return
  saving.value = true
  saveMsg.value = ''
  try {
    const updated = await updateArticle(article.value.id, { [field]: value })
    article.value = { ...article.value, ...updated }
    saveMsg.value = '保存しました'
    setTimeout(() => (saveMsg.value = ''), 2000)
  } catch {
    saveMsg.value = '保存に失敗しました'
  } finally {
    saving.value = false
  }
}

async function onCoverUpload(file: File) {
  if (!article.value) return
  saving.value = true
  saveMsg.value = ''
  try {
    const res = await uploadImage(file)
    const updated = await updateArticle(article.value.id, { cover: res.url })
    article.value = { ...article.value, ...updated }
    saveMsg.value = '画像を更新しました'
    setTimeout(() => (saveMsg.value = ''), 2000)
  } catch {
    saveMsg.value = 'アップロードに失敗しました'
  } finally {
    saving.value = false
  }
}

onMounted(() => load(route.params.id as string))
watch(
  () => route.params.id,
  (id) => {
    if (typeof id === 'string') load(id)
  },
)
</script>

<template>
  <section class="article">
    <RouterLink class="article__back" to="/shhy">‹ コラム一覧へ</RouterLink>

    <p v-if="notFound" class="article__empty">記事が見つかりませんでした。</p>

    <article v-else-if="article" class="article__body">
      <!-- Admin save status -->
      <div v-if="auth.isLoggedIn && auth.editing" class="article__save-status">
        <span v-if="saving">保存中…</span>
        <span v-else-if="saveMsg" class="article__save-success">{{ saveMsg }}</span>
      </div>

      <span v-if="article.cover || auth.editing" class="article__cover">
        <img v-if="article.cover" :src="article.cover" :alt="article.title" />
        <label class="article__cover-upload">
          <input
            type="file"
            accept="image/*"
            @change="(e) => {
              const t = e.target as HTMLInputElement
              if (t.files?.[0]) onCoverUpload(t.files[0])
            }"
          />
          <span>{{ article.cover ? '画像を変更' : '画像を追加' }}</span>
        </label>
      </span>
      <h1 class="article__title">
        <InlineEdit
          :model-value="article.title"
          :editing="auth.editing"
          placeholder="タイトル"
          @save="(v) => saveField('title', v)"
        />
      </h1>
      <p class="article__date">
        <InlineEdit
          :model-value="article.publishedAt || ''"
          :editing="auth.editing"
          placeholder="公開日"
          @save="(v) => saveField('publishedAt', v)"
        />
      </p>
      <div class="article__text">
        <InlineEdit
          :model-value="article.body || ''"
          :editing="auth.editing"
          tag="textarea"
          placeholder="本文を入力"
          @save="(v) => saveField('body', v)"
        />
      </div>
    </article>

    <p v-else class="article__empty">記事を読み込み中…（占位）</p>
  </section>
</template>

<style scoped>
.article__back {
  display: inline-block;
  font-size: 13px;
  color: #004b98;
  text-decoration: none;
  margin: 8px 0 20px;
}

.article__back:hover {
  color: #000;
}

.article__save-status {
  text-align: right;
  padding: 4px 0 8px;
  font-size: 12px;
  min-height: 20px;
}

.article__save-success {
  color: #2a7;
}

.article__cover {
  display: block;
  width: 100%;
  max-width: 480px;
  margin: 0 0 20px;
  position: relative;
}

.article__cover img {
  width: 100%;
  height: auto;
  display: block;
}

.article__cover-upload {
  display: block;
  text-align: center;
  padding: 8px;
  background: #f5f5f5;
  border: 1px dashed #ccc;
  font-size: 12px;
  color: #666;
  cursor: pointer;
  margin-top: 4px;
}

.article__cover-upload:hover {
  border-color: #004b98;
  color: #004b98;
}

.article__cover-upload input {
  display: none;
}

.article__title {
  font-size: 24px;
  margin: 0 0 8px;
  line-height: 1.4;
}

.article__date {
  font-size: 12px;
  color: #999;
  margin: 0 0 20px;
}

.article__text {
  font-size: 14px;
  line-height: 1.9;
  color: #333;
  white-space: pre-wrap;
}

.article__empty {
  color: #888;
  padding: 24px 0;
}
</style>
