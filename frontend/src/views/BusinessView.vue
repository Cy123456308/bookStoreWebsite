<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import BookRow from '@/components/BookRow.vue'
import { useBooksStore } from '@/stores/books'
import { useAuthStore } from '@/stores/auth'
import { useSiteStore } from '@/stores/site'
import { updateSite } from '@/api'
import InlineEdit from '@/components/InlineEdit.vue'

const books = useBooksStore()
const auth = useAuthStore()
const site = useSiteStore()

const saving = ref(false)
const saveMsg = ref('')
const showAllBooks = ref(false)

const displayBooks = computed(() => {
  if (showAllBooks.value) return books.books
  return books.books.slice(0, 5)
})

function toggleShowAll() {
  showAllBooks.value = !showAllBooks.value
}

async function saveField(field: 'businessLead' | 'businessIntro' | 'businessNote', value: string) {
  if (!site.info) return
  saving.value = true
  saveMsg.value = ''
  try {
    const updated = await updateSite({ [field]: value })
    site.info = { ...site.info, ...updated }
    saveMsg.value = '保存しました'
    setTimeout(() => (saveMsg.value = ''), 2000)
  } catch (e) {
    console.error(e)
    saveMsg.value = '保存に失敗しました'
  } finally {
    saving.value = false
  }
}

async function saveServices() {
  saving.value = true
  saveMsg.value = ''
  try {
    await site.saveSite()
    saveMsg.value = '保存しました'
    setTimeout(() => (saveMsg.value = ''), 2000)
  } catch (e) {
    console.error(e)
    saveMsg.value = '保存に失敗しました'
  } finally {
    saving.value = false
  }
}

function addService() {
  if (!site.info) return
  site.info.services.push('新しい事業内容')
}

function removeService(index: number) {
  if (!site.info) return
  site.info.services.splice(index, 1)
}

function updateService(index: number, value: string) {
  if (!site.info) return
  site.info.services[index] = value
}

async function saveClients() {
  saving.value = true
  saveMsg.value = ''
  try {
    await site.saveSite()
    saveMsg.value = '保存しました'
    setTimeout(() => (saveMsg.value = ''), 2000)
  } catch (e) {
    console.error(e)
    saveMsg.value = '保存に失敗しました'
  } finally {
    saving.value = false
  }
}

function addClient() {
  if (!site.info) return
  site.info.clients.push('新しい取引先')
}

function removeClient(index: number) {
  if (!site.info) return
  site.info.clients.splice(index, 1)
}

function updateClient(index: number, value: string) {
  if (!site.info) return
  site.info.clients[index] = value
}

onMounted(async () => {
  await books.loadBooks().catch(() => {})
  await site.loadSite().catch(() => {})
})
</script>

<template>
  <section class="business">
    <header class="business__header">
      <h1 class="business__title">業務紹介</h1>
      <p class="business__lead">
        <InlineEdit
          :model-value="site.info?.businessLead || '近年、日本の作品は中国で注目を集めています。小社は、これからの実績とネットワークを生かし、日本で生まれた作品を中国へご紹介しています。著作権の仲介業務および関連のコンサルタント業務をご提供いたします。'"
          :editing="auth.editing"
          tag="textarea"
          placeholder="リード文"
          @save="(v) => saveField('businessLead', v)"
        />
      </p>
    </header>

    <!-- Admin save status -->
    <div v-if="auth.isLoggedIn && auth.editing" class="business__save-status">
      <span v-if="saving">保存中…</span>
      <span v-else-if="saveMsg" class="business__save-success">{{ saveMsg }}</span>
    </div>

    <!-- 出版物紹介：自社シリーズ -->
    <div v-if="auth.editing" class="business__book-select">
      <button type="button" class="business__toggle-btn" @click="toggleShowAll">
        {{ showAllBooks ? '最初の5件のみ表示' : '全書籍を表示' }}
      </button>
    </div>
    <BookRow :books="displayBooks" title="『８２４人の四次元事件簿』シリーズ" />

    <!-- 事業内容 -->
    <section class="business__block">
      <div class="business__section-header">
        <h2 class="business__section-title">事業内容</h2>
        <button v-if="auth.editing" type="button" class="business__add-btn" @click="addService">+ 追加</button>
      </div>
      <p class="business__block-intro">
        <InlineEdit
          :model-value="site.info?.businessIntro || '小社は、日本の作品の翻訳出版契約締結までのエージェント業務を迅速かつ安心できる著作権の仲介業務および関連のコンサルタント業務をご提供致しております。'"
          :editing="auth.editing"
          tag="textarea"
          placeholder="事業内容紹介"
          @save="(v) => saveField('businessIntro', v)"
        />
      </p>
      <ul class="business__services">
        <li v-for="(s, i) in (site.info?.services || [])" :key="i" class="business__service">
          <InlineEdit
            :model-value="s"
            :editing="auth.editing"
            @save="(v) => updateService(i, v)"
          />
          <button v-if="auth.editing" type="button" class="business__item-remove" @click="removeService(i)">✕</button>
        </li>
      </ul>
      <p class="business__block-note">
        <InlineEdit
          :model-value="site.info?.businessNote || 'また、日本と中国の出版社間の相互交流を深める目的で関連の文化交流活動の計画と推進を行っております。お気軽にお問い合わせください。'"
          :editing="auth.editing"
          @save="(v) => saveField('businessNote', v)"
        />
      </p>
      <div v-if="auth.editing" class="business__save-actions">
        <button type="button" class="business__save-btn" @click="saveServices">事業内容を保存</button>
      </div>
    </section>

    <!-- 主な取引先 -->
    <section class="business__block">
      <div class="business__section-header">
        <h2 class="business__section-title">主な取引先</h2>
        <button v-if="auth.editing" type="button" class="business__add-btn" @click="addClient">+ 追加</button>
      </div>
      <ul class="business__clients">
        <li v-for="(c, i) in (site.info?.clients || [])" :key="i" class="business__client">
          <InlineEdit
            :model-value="c"
            :editing="auth.editing"
            @save="(v) => updateClient(i, v)"
          />
          <button v-if="auth.editing" type="button" class="business__item-remove" @click="removeClient(i)">✕</button>
        </li>
      </ul>
      <p class="business__block-note">※50音順　敬称略</p>
      <div v-if="auth.editing" class="business__save-actions">
        <button type="button" class="business__save-btn" @click="saveClients">取引先を保存</button>
      </div>
    </section>
  </section>
</template>

<style scoped>
.business__header {
  margin: 8px 0 8px;
}

.business__save-status {
  text-align: right;
  padding: 4px 0;
  font-size: 12px;
  min-height: 20px;
}

.business__save-success {
  color: #2a7;
}

.business__book-select {
  margin-bottom: 8px;
}

.business__toggle-btn {
  padding: 4px 12px;
  background: #f5f5f5;
  border: 1px solid #ddd;
  font-size: 12px;
  cursor: pointer;
  border-radius: 3px;
}

.business__toggle-btn:hover {
  border-color: #004b98;
  color: #004b98;
}

.business__title {
  font-size: 24px;
  margin: 0 0 12px;
  border-left: 4px solid #333;
  padding-left: 10px;
}

.business__lead {
  font-size: 14px;
  line-height: 1.9;
  color: #333;
  margin: 0 0 8px;
}

.business__block {
  margin-top: 40px;
}

.business__section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.business__section-title {
  font-size: 20px;
  margin: 0;
  border-left: 4px solid #333;
  padding-left: 10px;
}

.business__add-btn {
  padding: 4px 12px;
  background: #1a1a2e;
  color: #fff;
  border: none;
  font-size: 12px;
  cursor: pointer;
  border-radius: 3px;
}

.business__add-btn:hover {
  background: #e94560;
}

.business__block-intro {
  font-size: 14px;
  line-height: 1.9;
  color: #333;
  margin: 0 0 16px;
}

.business__services {
  list-style: none;
  margin: 0;
  padding: 0;
}

.business__service {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 0 10px 20px;
  border-bottom: 1px solid #eee;
  font-size: 14px;
  line-height: 1.8;
  color: #333;
}

.business__service::before {
  content: '●';
  position: absolute;
  left: 0;
  color: #004b98;
  font-size: 10px;
  top: 14px;
}

.business__service .inline-edit {
  flex: 1;
}

.business__item-remove {
  padding: 2px 6px;
  background: #fff;
  color: #c00;
  border: 1px solid #c00;
  font-size: 11px;
  cursor: pointer;
  border-radius: 3px;
  flex-shrink: 0;
}

.business__item-remove:hover {
  background: #c00;
  color: #fff;
}

.business__block-note {
  margin: 16px 0 0;
  font-size: 12px;
  color: #888;
  line-height: 1.8;
}

.business__clients {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.business__client {
  position: relative;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #333;
  border: 1px solid #ddd;
  background: #fafafa;
  padding: 8px 14px;
}

.business__client .inline-edit {
  min-width: 60px;
}

.business__client .business__item-remove {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 18px;
  height: 18px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 10px;
}

.business__save-actions {
  margin-top: 16px;
}

.business__save-btn {
  padding: 8px 20px;
  background: #1a1a2e;
  color: #fff;
  border: none;
  font-size: 13px;
  cursor: pointer;
  border-radius: 3px;
}

.business__save-btn:hover {
  background: #e94560;
}
</style>
