<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useSiteStore } from '@/stores/site'
import { useAuthStore } from '@/stores/auth'
import { updateSite } from '@/api'
import InlineEdit from '@/components/InlineEdit.vue'

const site = useSiteStore()
const auth = useAuthStore()

const saving = ref(false)
const saveMsg = ref('')

onMounted(() => site.loadSite().catch(() => {}))

const company = computed(() => site.info?.company)

async function saveField(field: string, value: string) {
  if (!site.info) return
  saving.value = true
  saveMsg.value = ''
  try {
    const updated = await updateSite({ [field]: value })
    site.info = { ...site.info, ...updated }
    saveMsg.value = '保存しました'
    setTimeout(() => (saveMsg.value = ''), 2000)
  } catch {
    saveMsg.value = '保存に失敗しました'
  } finally {
    saving.value = false
  }
}

function saveCompanyField(key: string, value: string) {
  if (!site.info) return
  saving.value = true
  saveMsg.value = ''
  updateSite({ company: { ...(site.info.company || {}), [key]: value } })
    .then((updated) => {
      site.info = { ...site.info, ...updated }
      saveMsg.value = '保存しました'
      setTimeout(() => (saveMsg.value = ''), 2000)
    })
    .catch(() => {
      saveMsg.value = '保存に失敗しました'
    })
    .finally(() => {
      saving.value = false
    })
}
</script>

<template>
  <section class="company">
    <header class="company__header">
      <h1 class="company__title">会社概要</h1>
      <p class="company__intro">
        <InlineEdit
          :model-value="site.info?.intro || ''"
          :editing="auth.editing"
          tag="textarea"
          placeholder="会社紹介文を入力"
          @save="(v) => saveField('intro', v)"
        />
      </p>
    </header>

    <!-- Admin save status -->
    <div v-if="auth.isLoggedIn && auth.editing" class="company__save-status">
      <span v-if="saving">保存中…</span>
      <span v-else-if="saveMsg" class="company__save-success">{{ saveMsg }}</span>
    </div>

    <p v-if="!site.loaded" class="company__empty">会社情報を読み込み中…（占位）</p>

    <template v-else-if="company">
      <dl class="company__table">
        <div class="company__row">
          <dt>社名</dt>
          <dd>
            <InlineEdit
              :model-value="site.info?.name || ''"
              :editing="auth.editing"
              placeholder="社名"
              @save="(v) => saveField('name', v)"
            />
            <span v-if="company.englishName" class="company__en">
              （<InlineEdit
                :model-value="company.englishName"
                :editing="auth.editing"
                placeholder="英文社名"
                @save="(v) => saveCompanyField('englishName', v)"
              />）
            </span>
          </dd>
        </div>
        <div v-if="company.homepageUrl || auth.editing" class="company__row">
          <dt>ホームページ</dt>
          <dd>
            <InlineEdit
              :model-value="company.homepageUrl || ''"
              :editing="auth.editing"
              placeholder="https://..."
              @save="(v) => saveCompanyField('homepageUrl', v)"
            />
          </dd>
        </div>
        <div v-if="company.address || auth.editing" class="company__row">
          <dt>所在地</dt>
          <dd>
            <InlineEdit
              :model-value="company.address || ''"
              :editing="auth.editing"
              placeholder="所在地"
              @save="(v) => saveCompanyField('address', v)"
            />
            <p v-if="company.access || auth.editing" class="company__sub">
              <InlineEdit
                :model-value="company.access || ''"
                :editing="auth.editing"
                placeholder="アクセス方法"
                @save="(v) => saveCompanyField('access', v)"
              />
            </p>
          </dd>
        </div>
        <div v-if="company.established || auth.editing" class="company__row">
          <dt>設立</dt>
          <dd>
            <InlineEdit
              :model-value="company.established || ''"
              :editing="auth.editing"
              placeholder="設立日"
              @save="(v) => saveCompanyField('established', v)"
            />
          </dd>
        </div>
        <div v-if="company.contactOffice || auth.editing" class="company__row">
          <dt>連絡所</dt>
          <dd>
            <InlineEdit
              :model-value="company.contactOffice || ''"
              :editing="auth.editing"
              placeholder="連絡所"
              @save="(v) => saveCompanyField('contactOffice', v)"
            />
          </dd>
        </div>
        <div v-if="company.representative || auth.editing" class="company__row">
          <dt>代表者</dt>
          <dd>
            <InlineEdit
              :model-value="company.representative || ''"
              :editing="auth.editing"
              placeholder="代表者"
              @save="(v) => saveCompanyField('representative', v)"
            />
          </dd>
        </div>
        <div v-if="company.business || auth.editing" class="company__row">
          <dt>事業内容</dt>
          <dd class="company__business">
            <InlineEdit
              :model-value="company.business || ''"
              :editing="auth.editing"
              tag="textarea"
              placeholder="事業内容"
              @save="(v) => saveCompanyField('business', v)"
            />
          </dd>
        </div>
      </dl>
    </template>

    <p v-else class="company__empty">会社情報を取得できませんでした。</p>
  </section>
</template>

<style scoped>
.company__header {
  margin: 8px 0 24px;
}

.company__title {
  font-size: 24px;
  margin: 0 0 6px;
  border-left: 4px solid #333;
  padding-left: 10px;
}

.company__intro {
  margin: 0 0 0 14px;
  font-size: 13px;
  color: #666;
  line-height: 1.8;
}

.company__save-status {
  text-align: right;
  padding: 4px 0 8px;
  font-size: 12px;
  min-height: 20px;
}

.company__save-success {
  color: #2a7;
}

.company__table {
  margin: 0;
  border-top: 1px solid #eee;
}

.company__row {
  display: flex;
  gap: 24px;
  padding: 16px 4px;
  border-bottom: 1px solid #eee;
}

.company__row dt {
  width: 120px;
  flex-shrink: 0;
  font-size: 13px;
  font-weight: 700;
  color: #333;
}

.company__row dd {
  margin: 0;
  flex: 1;
  font-size: 14px;
  color: #333;
  line-height: 1.8;
}

.company__en {
  color: #666;
  font-weight: 400;
}

.company__sub {
  margin: 6px 0 0;
  font-size: 12px;
  color: #888;
}

.company__business {
  line-height: 1.9;
}

.company__row dd a {
  color: #004b98;
  text-decoration: none;
  word-break: break-all;
}

.company__row dd a:hover {
  color: #000;
}

.company__empty {
  color: #888;
  padding: 24px 0;
}
</style>
