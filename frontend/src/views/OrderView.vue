<script setup lang="ts">
const faqs = [
  {
    q: 'ご購入方法',
    a: '各書籍の詳細ページより「購入はこちら」ボタンを押すと、Amazon などの販売サイトへ移動します。そちらでご注文ください。',
  },
  {
    q: '配送について',
    a: '配送・梱包・送料は各販売サイトの規定に準じます。詳細は購入画面にてご確認ください。',
  },
  {
    q: '団体・法人の皆様へ',
    a: '書店・法人・学校等でのまとまったご注文や翻訳出版に関するご相談は、お問い合わせフォームよりお気軽にご連絡ください。',
  },
  {
    q: '海外からのご注文',
    a: '各販売サイトにて対応しております。お住まいの国のAmazonなどをご利用ください。',
  },
]
</script>

<template>
  <section class="purchase">
    <header class="purchase__header">
      <h1 class="purchase__title">購入について</h1>
      <p class="purchase__intro">
        書籍のご購入方法や配送・まとまったご注文に関するよくあるご質問をまとめました。
      </p>
    </header>

    <dl class="purchase__faq">
      <div v-for="(item, i) in faqs" :key="i" class="purchase__row">
        <dt class="purchase__q">{{ item.q }}</dt>
        <dd class="purchase__a">{{ item.a }}</dd>
      </div>
    </dl>

    <div class="purchase__links">
      <RouterLink class="purchase__link" to="/books">書籍一覧を見る</RouterLink>
      <RouterLink class="purchase__link purchase__link--ghost" to="/contact">
        お問い合わせ
      </RouterLink>
    </div>
  </section>
</template>

<style scoped>
.purchase__header {
  margin: 8px 0 24px;
}

.purchase__title {
  font-size: 24px;
  margin: 0 0 6px;
  border-left: 4px solid #333;
  padding-left: 10px;
}

.purchase__intro {
  margin: 0 0 0 14px;
  font-size: 13px;
  color: #666;
  line-height: 1.8;
}

.purchase__faq {
  margin: 0;
  border-top: 1px solid #eee;
}

.purchase__row {
  padding: 18px 4px;
  border-bottom: 1px solid #eee;
}

.purchase__q {
  font-size: 15px;
  font-weight: 700;
  color: #333;
  margin-bottom: 8px;
}

.purchase__a {
  margin: 0;
  font-size: 14px;
  line-height: 1.9;
  color: #444;
}

.purchase__links {
  display: flex;
  gap: 12px;
  margin-top: 32px;
  flex-wrap: wrap;
}

.purchase__link {
  display: inline-block;
  padding: 11px 28px;
  background: #333;
  color: #fff;
  text-decoration: none;
  font-size: 14px;
  font-family: inherit;
}

.purchase__link:hover {
  background: #000;
}

.purchase__link--ghost {
  background: none;
  border: 1px solid #333;
  color: #333;
}

.purchase__link--ghost:hover {
  background: #f3f3f3;
}
</style>
