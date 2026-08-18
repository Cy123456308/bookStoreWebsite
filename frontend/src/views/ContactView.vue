<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { submitContact } from '@/api'
import { useSiteStore } from '@/stores/site'

const site = useSiteStore()
onMounted(() => site.loadSite())

const subjects = ['書籍について', 'ご注文について', 'コラムについて', 'その他']

const form = reactive({
  name: '',
  email: '',
  phone: '',
  organization: '',
  postalCode: '',
  address: '',
  subject: '書籍について',
  message: '',
})

const submitted = ref(false)
const sending = ref(false)
const error = ref('')

async function onSubmit() {
  error.value = ''
  if (!form.name.trim()) {
    error.value = '氏名を入力してください。'
    return
  }
  if (!form.email.trim() && !form.phone.trim()) {
    error.value = 'メールアドレスまたは電話番号のいずれかを入力してください。'
    return
  }
  if (!form.message.trim()) {
    error.value = 'メッセージを入力してください。'
    return
  }
  sending.value = true
  try {
    const res = await submitContact({ ...form })
    if (res.ok) submitted.value = true
  } catch (e) {
    error.value = e instanceof Error ? e.message : '送信に失敗しました'
  } finally {
    sending.value = false
  }
}

function reset() {
  submitted.value = false
  form.name = ''
  form.email = ''
  form.phone = ''
  form.organization = ''
  form.postalCode = ''
  form.address = ''
  form.subject = '書籍について'
  form.message = ''
}
</script>

<template>
  <section class="contact">
    <header class="contact__header">
      <h1 class="contact__title">お問い合わせ</h1>
      <p class="contact__intro">
        ご意見・ご質問など、お気軽にお寄せ下さい。以下のフォーム、または直接のお電話・メールにてご連絡いただけます。
      </p>
    </header>

    <div class="contact__layout">
      <!-- フォーム -->
      <div class="contact__form-wrap">
        <p v-if="submitted" class="contact__done">
          送信しました。確認次第ご連絡いたします。
          <button type="button" class="contact__again" @click="reset">
            もう一度送信する
          </button>
        </p>

        <form v-else class="contact__form" @submit.prevent="onSubmit">
          <div class="contact__grid">
            <label class="contact__field">
              <span class="contact__label">氏名<span class="contact__req">＊</span></span>
              <input v-model="form.name" type="text" />
            </label>
            <label class="contact__field">
              <span class="contact__label">ご所属</span>
              <input v-model="form.organization" type="text" />
            </label>

            <label class="contact__field">
              <span class="contact__label">メール</span>
              <input v-model="form.email" type="email" placeholder="example@hirogawa.com" />
            </label>
            <label class="contact__field">
              <span class="contact__label">電話番号</span>
              <input v-model="form.phone" type="tel" placeholder="090-0000-0000" />
            </label>

            <label class="contact__field">
              <span class="contact__label">郵便番号</span>
              <input v-model="form.postalCode" type="text" placeholder="000-0000" />
            </label>
            <label class="contact__field">
              <span class="contact__label">ご住所</span>
              <input v-model="form.address" type="text" />
            </label>
          </div>

          <label class="contact__field">
            <span class="contact__label">お問い合わせ種別</span>
            <select v-model="form.subject">
              <option v-for="s in subjects" :key="s" :value="s">{{ s }}</option>
            </select>
          </label>

          <label class="contact__field">
            <span class="contact__label">メッセージ<span class="contact__req">＊</span></span>
            <textarea v-model="form.message" rows="6"></textarea>
          </label>

          <button class="contact__submit" type="submit" :disabled="sending">
            {{ sending ? '送信中…' : '送信する' }}
          </button>
          <p v-if="error" class="contact__error">{{ error }}</p>
        </form>
      </div>

      <!-- お問い合わせ先 -->
      <aside class="contact__info">
        <h2 class="contact__info-title">お問い合わせ先</h2>
        <ul class="contact__info-list">
          <li v-if="site.info?.email" class="contact__info-item">
            <span class="contact__info-label">メール</span>
            <a :href="`mailto:${site.info.email}`">{{ site.info.email }}</a>
          </li>
          <li v-if="site.info?.phone" class="contact__info-item">
            <span class="contact__info-label">電話</span>
            <span>{{ site.info.phone }}</span>
          </li>
          <li v-if="site.info?.address" class="contact__info-item">
            <span class="contact__info-label">所在地</span>
            <span>{{ site.info.address }}</span>
          </li>
          <li v-if="site.info?.twitterUrl" class="contact__info-item">
            <span class="contact__info-label">X（Twitter）</span>
            <a :href="site.info.twitterUrl" target="_blank" rel="noopener">
              {{ site.info.twitterUrl }}
            </a>
          </li>
        </ul>
        <p class="contact__info-note">
          ※ 郵便番号・ご住所の入力は任意です。メールまたは電話番号のいずれかをご入力ください。
        </p>
      </aside>
    </div>
  </section>
</template>

<style scoped>
.contact__header {
  margin: 8px 0 24px;
}

.contact__title {
  font-size: 24px;
  margin: 0 0 6px;
  border-left: 4px solid #333;
  padding-left: 10px;
}

.contact__intro {
  margin: 0 0 0 14px;
  font-size: 13px;
  color: #666;
  line-height: 1.8;
}

.contact__layout {
  display: flex;
  gap: 40px;
  align-items: flex-start;
}

.contact__form-wrap {
  flex: 1 1 auto;
  min-width: 0;
}

.contact__form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.contact__grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.contact__field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.contact__label {
  font-size: 13px;
  color: #333;
}

.contact__req {
  color: #c00;
  margin-left: 4px;
}

.contact__field input,
.contact__field select,
.contact__field textarea {
  padding: 9px 10px;
  border: 1px solid #ccc;
  font: inherit;
  color: #333;
  box-sizing: border-box;
  width: 100%;
}

.contact__field input:focus,
.contact__field select:focus,
.contact__field textarea:focus {
  outline: none;
  border-color: #004b98;
}

.contact__submit {
  align-self: flex-start;
  padding: 11px 36px;
  background: #333;
  color: #fff;
  border: none;
  font-size: 15px;
  cursor: pointer;
  font-family: inherit;
}

.contact__submit:hover:not(:disabled) {
  background: #000;
}

.contact__submit:disabled {
  opacity: 0.6;
  cursor: default;
}

.contact__error {
  color: #c00;
  font-size: 13px;
  margin: 0;
}

.contact__done {
  color: #2a7;
  font-size: 15px;
  line-height: 2;
}

.contact__again {
  display: inline-block;
  margin-left: 12px;
  background: none;
  border: 1px solid #2a7;
  color: #2a7;
  font-size: 13px;
  padding: 4px 14px;
  cursor: pointer;
  font-family: inherit;
}

.contact__info {
  flex: 0 0 300px;
  border: 1px solid #eee;
  padding: 20px;
  background: #fafafa;
}

.contact__info-title {
  font-size: 16px;
  margin: 0 0 14px;
  padding-bottom: 8px;
  border-bottom: 2px solid #333;
}

.contact__info-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.contact__info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
  font-size: 13px;
  word-break: break-all;
}

.contact__info-label {
  font-size: 11px;
  color: #999;
}

.contact__info-item a {
  color: #004b98;
  text-decoration: none;
}

.contact__info-item a:hover {
  color: #000;
}

.contact__info-note {
  margin: 14px 0 0;
  font-size: 11px;
  color: #999;
  line-height: 1.7;
}

@media (max-width: 860px) {
  .contact__layout {
    flex-direction: column;
  }
  .contact__info {
    flex: 1 1 auto;
    width: 100%;
    box-sizing: border-box;
  }
}

@media (max-width: 560px) {
  .contact__grid {
    grid-template-columns: 1fr;
  }
}
</style>
