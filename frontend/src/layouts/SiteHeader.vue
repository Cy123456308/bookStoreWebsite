<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useSiteStore } from '@/stores/site'
import { updateSite } from '@/api'
import InlineEdit from '@/components/InlineEdit.vue'

const auth = useAuthStore()
const site = useSiteStore()

const saving = ref(false)
const saveMsg = ref('')

onMounted(() => {
  site.loadSite().catch(() => {})
})

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

</script>

<template>
  <header class="site-header">
    <div class="site-header__top">
      <RouterLink class="site-header__logo" to="/sy" aria-label="ホーム">
        <img
          v-if="site.info?.logoUrl"
          :src="site.info.logoUrl"
          alt="ロゴ"
          class="site-header__logo-img"
        />
        <span v-else class="site-header__logo-placeholder">LOGO</span>
      </RouterLink>

      <div class="site-header__right">
        <p class="site-header__intro">
          <InlineEdit
            :model-value="site.info?.intro || ''"
            :editing="auth.editing"
            tag="textarea"
            placeholder="紹介文を入力"
            @save="(v) => saveField('intro', v)"
          />
        </p>
        <a
          class="site-header__twitter"
          :href="site.info?.twitterUrl || '#'"
          target="_blank"
          rel="noopener"
        >
          <span class="site-header__twitter-icon">X</span>
          <span class="site-header__twitter-text">
            <InlineEdit
              :model-value="'X ツイッターを利用しています。'"
              :editing="auth.editing"
              placeholder="X 文案"
              @save="(v) => saveField('twitterUrl', v)"
            />
          </span>
        </a>
      </div>
    </div>
    <div v-if="auth.isLoggedIn && auth.editing" class="site-header__save-status">
      <span v-if="saving">保存中…</span>
      <span v-else-if="saveMsg" class="site-header__save-success">{{ saveMsg }}</span>
    </div>
  </header>
</template>

<style scoped>
.site-header {
  width: 1200px;
  height: 107px;
  margin: 0 auto;
  box-sizing: border-box;
}

.site-header__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 107px;
}

.site-header__logo {
  display: flex;
  align-items: center;
  text-decoration: none;
}

.site-header__logo-img {
  width: 207px;
  height: 73px;
  object-fit: contain;
}

.site-header__logo-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 207px;
  height: 73px;
  background: #ddd;
  border: 1px solid #ccc;
  color: #888;
  font-size: 18px;
  letter-spacing: 2px;
}

.site-header__right {
  display: flex;
  align-items: center;
  gap: 24px;
  flex: 1;
  justify-content: flex-end;
  min-width: 0;
}

.site-header__intro {
  margin: 0;
  max-width: 620px;
  text-align: right;
  font-size: 11.2px;
  line-height: 1.75;
  color: #333;
}

.site-header__twitter {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
  text-decoration: none;
  color: #333;
}

.site-header__twitter-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 41px;
  height: 41px;
  border-radius: 50%;
  background: #000;
  color: #fff;
  font-weight: 700;
}

.site-header__twitter-text {
  font-size: 8px;
  color: #666;
}

.site-header__save-status {
  text-align: right;
  padding: 4px 0;
  font-size: 12px;
  min-height: 20px;
}

.site-header__save-success {
  color: #2a7;
}
</style>
