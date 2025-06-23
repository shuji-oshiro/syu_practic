<template>
  <v-btn @click="openFileDialog">
    <v-icon >mdi-import</v-icon>
    <span>CSV更新</span>
  </v-btn>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const emit = defineEmits<{
  (e: 'csvdata', contents: FormData): void
  (e: 'error', message: string): void
}>()

const errorMessage = ref<string | null>(null)
// CSVファイルを選択するダイアログを開く関数
// ファイル選択後、内容を親コンポーネントに送信する
const openFileDialog = () => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = '.csv'
    input.addEventListener('change', (event) => {
        const file = (event.target as HTMLInputElement).files?.[0]
        if (file) {
          const formData = new FormData()
          formData.append('file', file)
          emit('csvdata', formData)  // CSVデータを親コンポーネントに送信
        }
    })
    input.click()
}

</script>
