<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import type { Banner } from '@/types'

const props = defineProps<{ banners: Banner[] }>()

const current = ref(0)
let timer: ReturnType<typeof setInterval> | null = null

function go(i: number) {
  if (!props.banners.length) return
  current.value = (i + props.banners.length) % props.banners.length
}
function next() {
  go(current.value + 1)
}
function prev() {
  go(current.value - 1)
}

onMounted(() => {
  if (props.banners.length > 1) {
    timer = setInterval(next, 5000)
  }
})
onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<template>
  <section class="banner" aria-label="banner">
    <template v-if="banners.length">
      <div class="banner__track" :style="{ transform: `translateX(-${current * 100}%)` }">
        <div v-for="b in banners" :key="b.id" class="banner__slide">
          <a v-if="b.link" :href="b.link" class="banner__slide-inner">
            <img v-if="b.image" :src="b.image" :alt="b.title ?? ''" class="banner__img" />
            <span v-else class="banner__placeholder">{{ b.title ?? 'Banner' }}</span>
          </a>
          <template v-else>
            <img v-if="b.image" :src="b.image" :alt="b.title ?? ''" class="banner__img" />
            <span v-else class="banner__placeholder">{{ b.title ?? 'Banner' }}</span>
          </template>
        </div>
      </div>

      <button
        v-if="banners.length > 1"
        class="banner__nav banner__nav--prev"
        type="button"
        @click="prev"
        aria-label="前へ"
      >
        ‹
      </button>
      <button
        v-if="banners.length > 1"
        class="banner__nav banner__nav--next"
        type="button"
        @click="next"
        aria-label="次へ"
      >
        ›
      </button>

      <div class="banner__dots">
        <button
          v-for="(b, i) in banners"
          :key="b.id"
          type="button"
          class="banner__dot"
          :class="{ 'banner__dot--active': i === current }"
          :aria-label="`スライド ${i + 1}`"
          @click="go(i)"
        />
      </div>
    </template>

    <div v-else class="banner__slide">
      <span class="banner__placeholder">Banner 占位（轮播区）</span>
    </div>
  </section>
</template>

<style scoped>
.banner {
  position: relative;
  width: 100%;
  height: 389px;
  overflow: hidden;
  background: #ddd;
}

.banner__track {
  display: flex;
  height: 100%;
  transition: transform 0.5s ease;
}

.banner__slide {
  flex: 0 0 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.banner__slide-inner {
  display: flex;
  width: 100%;
  height: 100%;
  align-items: center;
  justify-content: center;
  text-decoration: none;
}

.banner__img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.banner__placeholder {
  font-size: 24px;
  color: #fff;
  background: linear-gradient(135deg, #d9c3b0, #b89b7e);
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.banner__nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 40px;
  height: 60px;
  border: none;
  background: rgba(0, 0, 0, 0.3);
  color: #fff;
  font-size: 28px;
  cursor: pointer;
}
.banner__nav--prev {
  left: 0;
}
.banner__nav--next {
  right: 0;
}

.banner__dots {
  position: absolute;
  bottom: 12px;
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  gap: 8px;
}

.banner__dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  padding: 0;
}
.banner__dot--active {
  background: #fff;
}
</style>
