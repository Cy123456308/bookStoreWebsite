<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useNavStore } from '@/stores/nav'

const nav = useNavStore()

onMounted(() => {
  nav.loadNav().catch(() => {})
})

const fallbackItems = [
  { id: 'f1', label: 'ホーム', to: '/sy' },
  { id: 'f2', label: '書籍', to: '/books' },
  { id: 'f3', label: '業務紹介', to: '/shjs' },
  { id: 'f4', label: 'コラム', to: '/shhy' },
  { id: 'f5', label: '購入について', to: '/shxw' },
  { id: 'f6', label: '会社概要', to: '/zpxx' },
  { id: 'f7', label: 'お問い合わせ', to: '/contact' },
  { id: 'f8', label: 'ダウンロード', to: '/information' },
]

const displayItems = computed(() => {
  return nav.items.length > 0 ? nav.items : fallbackItems
})
</script>

<template>
  <nav class="site-nav">
    <ul class="site-nav__list">
      <li v-for="item in displayItems" :key="item.id" class="site-nav__item">
        <RouterLink class="site-nav__link" :to="item.to">
          {{ item.label }}
        </RouterLink>
      </li>
    </ul>
  </nav>
</template>

<style scoped>
.site-nav {
  width: 1200px;
  height: 50px;
  margin: 0 auto;
}

.site-nav__list {
  display: flex;
  height: 50px;
  list-style: none;
  margin: 0;
  padding: 0;
}

.site-nav__item {
  flex: 1;
  height: 50px;
  line-height: 50px;
  text-align: center;
  border-left: 1px solid #e6e6e6;
}

.site-nav__item:first-child {
  border-left: none;
}

.site-nav__link {
  display: block;
  height: 50px;
  line-height: 50px;
  font-size: 14px;
  font-family: 'Noto Sans CJK', 'Hiragino Sans', 'Yu Gothic', 'Microsoft YaHei', sans-serif;
  color: #004b98;
  text-decoration: none;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.site-nav__link:hover {
  color: #000;
}

.site-nav__link.router-link-active {
  color: #000;
}
</style>
