<template>
  <v-card>
    <v-layout>
      <AppNavigation />
      <v-main style="height: 100vh;" >  
        <v-alert
          v-if="showAlert"
          closable
          :title="title"
          :text="message"
          :type="alertType"
          variant="tonal"
          @click:close="showAlert = false"
        ></v-alert>
        <MenuWindow />
        <AppBottomNavigation />
      </v-main>
    </v-layout>
  </v-card>
</template>
<script setup lang="ts">
  import { ref, watch} from 'vue'
  import { useEventStore } from '@/stores/eventStore'
  const showAlert = ref(false)
  const store = useEventStore()
  const message = ref('')
  const icon = ref('mdi-alert-circle')
  const title = ref('')
  const alertType = ref<'success' | 'info' | 'warning' | 'error'>('success')
  // ナビゲーションバーよりカテゴリが選択された時、またはメニューがインポートされた時の処理を監視
  watch(
    () => [store.lastError.timestamp, store.lastInfo.timestamp, store.lastWarning.timestamp],
    () => {
      showAlert.value = true  
      if (store.lastError.message) {
        title.value = store.lastError.message
        message.value = store.lastError.detail
        icon.value = 'mdi-alert-circle'
        alertType.value = 'error' // エラータイプ
      } else if (store.lastInfo.message) {
        title.value = store.lastInfo.message
        message.value = store.lastInfo.detail
        icon.value = 'mdi-information'
        alertType.value = 'info' // 情報タイプ
      } else if (store.lastWarning.message) {
        title.value = store.lastWarning.message
        message.value = store.lastWarning.detail
        icon.value = 'mdi-alert-circle'
        alertType.value = 'warning' // 警告タイプ
      }
    }
  )
</script>