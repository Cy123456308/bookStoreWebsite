<script setup lang="ts">
import type { Book } from '@/types'

defineProps<{
  books: Book[]
  title?: string
}>()
</script>

<template>
  <section class="book-row" v-if="books.length">
    <div class="book-row__head" v-if="title">
      <h2 class="book-row__title">{{ title }}</h2>
      <RouterLink class="book-row__more" to="/books">もっと見る&gt;&gt;</RouterLink>
    </div>

    <div class="book-row__scroller">
      <RouterLink
        v-for="book in books"
        :key="book.id"
        class="book-row__item"
        :to="`/book/${book.id}`"
      >
        <div class="book-row__cover">
          <img v-if="book.cover" :src="book.cover" :alt="book.title" />
          <span v-else>封面占位</span>
        </div>
        <h3 class="book-row__item-title">{{ book.title }}</h3>
        <p v-if="book.author" class="book-row__author">{{ book.author }}</p>
        <p v-if="book.description" class="book-row__desc">{{ book.description }}</p>
        <p v-if="book.price" class="book-row__price">¥{{ book.price }}</p>
      </RouterLink>
    </div>
  </section>
</template>

<style scoped>
.book-row {
  margin-top: 32px;
}

.book-row__head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  border-bottom: 1px solid #ddd;
  padding-bottom: 6px;
  margin-bottom: 16px;
}

.book-row__title {
  font-size: 20px;
  margin: 0;
  border-left: 4px solid #333;
  padding-left: 10px;
}

.book-row__more {
  font-size: 12px;
  color: #004b98;
  text-decoration: none;
}

.book-row__scroller {
  display: flex;
  gap: 20px;
  overflow-x: auto;
  padding-bottom: 8px;
}

.book-row__item {
  flex: 0 0 175px;
  text-decoration: none;
  color: inherit;
}

.book-row__cover {
  width: 175px;
  height: 280px;
  background: #ddd;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #888;
  overflow: hidden;
}

.book-row__cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.book-row__item-title {
  font-size: 14px;
  margin: 8px 0 4px;
}

.book-row__author,
.book-row__price {
  font-size: 12px;
  color: #666;
  margin: 0 0 4px;
}

.book-row__desc {
  font-size: 12px;
  color: #666;
  line-height: 1.6;
  margin: 0 0 4px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
