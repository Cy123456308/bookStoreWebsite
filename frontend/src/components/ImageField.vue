<script setup lang="ts">
import { ref } from 'vue'
import { uploadImage } from '@/api'

const props = defineProps<{
  modelValue?: string
  label?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const previewUrl = ref(props.modelValue || '')
const uploading = ref(false)

async function onFileChange(e: Event) {
  const target = e.target as HTMLInputElement
  if (!target.files || !target.files[0]) return
  uploading.value = true
  try {
    const res = await uploadImage(target.files[0])
    const url = res.url
    previewUrl.value = url
    emit('update:modelValue', url)
  } finally {
    uploading.value = false
    target.value = ''
  }
}

function clear() {
  previewUrl.value = ''
  emit('update:modelValue', '')
}
</script>

<template>
  <div class="image-field">
    <label class="image-field__label">{{ label || '画像' }}</label>
    <div class="image-field__preview" v-if="previewUrl">
      <img :src="previewUrl" :alt="label" />
      <button type="button" class="image-field__clear" @click="clear" title="削除">×</button>
    </div>
    <label class="image-field__upload">
      <input type="file" accept="image/*,.pdf" @change="onFileChange" :disabled="uploading" />
      <span>{{ uploading ? 'アップロード中…' : (previewUrl ? '画像を変更' : '画像を選択') }}</span>
    </label>
    <input v-if="previewUrl" type="hidden" :value="previewUrl" />
  </div>
</template>

<style scoped>
.image-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.image-field__label {
  font-size: 13px;
  color: #333;
  font-weight: 600;
}

.image-field__preview {
  position: relative;
  width: 200px;
  aspect-ratio: 3 / 4;
  background: #eee;
  overflow: hidden;
}

.image-field__preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-field__clear {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 22px;
  height: 22px;
  border: none;
  border-radius: 50%;
  background: rgba(0,0,0,0.6);
  color: #fff;
  font-size: 14px;
  line-height: 22px;
  cursor: pointer;
}

.image-field__upload {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  border: 1px dashed #ccc;
  background: #fafafa;
  color: #333;
  font-size: 13px;
  cursor: pointer;
  width: fit-content;
}

.image-field__upload:hover {
  border-color: #004b98;
  color: #004b98;
}

.image-field__upload input {
  display: none;
}
</style>