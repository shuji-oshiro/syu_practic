<template>
  <v-btn @click="openFileDialog">
    <v-icon >mdi-import</v-icon>
    <span>更新</span>
  </v-btn>
</template>

<script setup lang="ts">
  import { ref } from 'vue'
  import { useEventStore } from '@/stores/eventStore'
  const store = useEventStore()

  // CSVファイルを選択するダイアログを開く関数
  // ファイル選択後、選択されたファイルを FormData に追加し、Pinia のアクションを呼び出す
  const openFileDialog = () => {
      const input = document.createElement('input')
      input.type = 'file'
      input.accept = '.csv'
      input.addEventListener('change', (event) => {
        const file = (event.target as HTMLInputElement).files?.[0]
        if (file) {
          const formData = new FormData()
          formData.append('file', file)
          store.triggerImportMenusAction(formData)
        }
      })
      input.click()
  }

</script>
