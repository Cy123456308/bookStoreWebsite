<script setup lang="ts">
import type { Book } from '@/types'
import { useAuthStore } from '@/stores/auth'
import InlineEdit from '@/components/InlineEdit.vue'

defineProps<{
  book: Book
  onSave?: (book: Book, field: string, value: string | number) => void
}>()

const auth = useAuthStore()
</script>

<template>
  <article class="book-card" :class="{ 'book-card--editing': auth.editing }">
    <component
      :is="auth.editing ? 'div' : 'RouterLink'"
      class="book-card__link"
      v-bind="auth.editing ? {} : { to: `/book/${book.id}` }"
    >
      <div class="book-card__cover">
        <img v-if="book.cover" :src="book.cover" :alt="book.title" />
        <span v-else>封面占位</span>
      </div>
      <h3 class="book-card__title">
        <InlineEdit
          :model-value="book.title"
          :editing="auth.editing"
          placeholder="タイトル"
          @save="(v) => onSave?.(book, 'title', v)"
        />
      </h3>
      <p class="book-card__author">
        <InlineEdit
          :model-value="book.author || ''"
          :editing="auth.editing"
          placeholder="著者"
          @save="(v) => onSave?.(book, 'author', v)"
        />
      </p>
      <p class="book-card__price">
        ¥<InlineEdit
          :model-value="String(book.price || 0)"
          :editing="auth.editing"
          placeholder="価格"
          @save="(v) => onSave?.(book, 'price', Number(v) || 0)"
        />
      </p>
    </component>
  </article>
</template>

<style scoped>
.book-card__link {
  display: block;
  text-decoration: none;
  color: inherit;
}

.book-card__cover {
  width: 100%;
  max-width: 100%;
  aspect-ratio: 3 / 4;
  background: #ddd;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #888;
  overflow: hidden;
}

.book-card {
  min-width: 0;
  overflow: hidden;
}

.book-card--editing {
  border: 1px dashed #ccc;
  padding: 8px;
  border-radius: 4px;
}

.book-card__cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.book-card__title {
  font-size: 14px;
  margin: 8px 0 4px;
}

.book-card__author,
.book-card__price {
  font-size: 12px;
  color: #666;
  margin: 0;
}
</style>
