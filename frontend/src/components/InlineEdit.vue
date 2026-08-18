<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'

const props = defineProps<{
  modelValue: string
  editing: boolean
  tag?: 'input' | 'textarea'
  placeholder?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'save', value: string): void
}>()

const localValue = ref(props.modelValue)
const inputRef = ref<HTMLInputElement | HTMLTextAreaElement | null>(null)

watch(
  () => props.modelValue,
  (v) => {
    localValue.value = v
  },
)

watch(
  () => props.editing,
  async (isEditing) => {
    if (isEditing) {
      await nextTick()
      inputRef.value?.focus()
      inputRef.value?.select()
    }
  },
)

function onBlur() {
  if (localValue.value !== props.modelValue) {
    emit('update:modelValue', localValue.value)
    emit('save', localValue.value)
  }
}

function onInput(e: Event) {
  const target = e.target as HTMLInputElement | HTMLTextAreaElement
  localValue.value = target.value
  emit('update:modelValue', target.value)
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && props.tag !== 'textarea') {
    ;(e.target as HTMLElement).blur()
  }
  if (e.key === 'Escape') {
    localValue.value = props.modelValue
    ;(e.target as HTMLElement).blur()
  }
}
</script>

<template>
  <div class="inline-edit">
    <div v-if="!editing" class="inline-edit__display">
      <slot>
        <span :class="{ 'inline-edit__placeholder': !modelValue }">
          {{ modelValue || placeholder || '未設定' }}
        </span>
      </slot>
      <span class="inline-edit__hint">編集するには「編集開始」をクリック</span>
    </div>
    <component
      v-else
      :is="tag || 'input'"
      ref="inputRef"
      class="inline-edit__input"
      :value="localValue"
      :placeholder="placeholder"
      @input="onInput"
      @blur="onBlur"
      @keydown="onKeydown"
    />
  </div>
</template>

<style scoped>
.inline-edit {
  display: inline-block;
  width: 100%;
}

.inline-edit__display {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: default;
}

.inline-edit__placeholder {
  color: #999;
  font-style: italic;
}

.inline-edit__hint {
  font-size: 10px;
  color: #bbb;
  white-space: nowrap;
  opacity: 0;
  transition: opacity 0.2s;
}

.inline-edit__display:hover .inline-edit__hint {
  opacity: 1;
}

.inline-edit__input {
  width: 100%;
  padding: 6px 8px;
  border: 2px solid #1a1a2e;
  font: inherit;
  font-size: inherit;
  color: inherit;
  background: #fffde7;
  box-sizing: border-box;
  border-radius: 3px;
}

.inline-edit__input:focus {
  outline: none;
  border-color: #e94560;
  background: #fff;
}

textarea.inline-edit__input {
  min-height: 60px;
  resize: vertical;
}
</style>
