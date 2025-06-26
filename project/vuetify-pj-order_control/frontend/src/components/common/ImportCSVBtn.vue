<template>
  <v-btn @click="openFileDialog">
    <v-icon >mdi-import</v-icon>
    <span>更新</span>
  </v-btn>
</template>

<script setup lang="ts">
import { UseEventStore } from '@/stores/eventStore'
const useEventStore = UseEventStore()

const openFileDialog = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.csv'
  input.addEventListener('change', async (event) => {
    const file = (event.target as HTMLInputElement).files?.[0]
    if (file) {
      const formData = new FormData()
      formData.append('file', file)
      await useEventStore.triggerImportMenusAction(formData)
    }
  })
  input.click()
}
</script>
