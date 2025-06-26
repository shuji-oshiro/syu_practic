<template>
  <v-card>
    <v-layout>
      <AppNavigation />
      <v-main style="height: 100vh;" >  
        <v-alert
          v-if="showAlert"
          closable
          icon="$vuetify"
          title="Alert title"
          text="..aaaaaaaaaa."
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

  // ナビゲーションバーよりカテゴリが選択された時、またはメニューがインポートされた時の処理を監視
  watch(
    () => store.lastError.timestamp,
    () => {
      if (store.lastError.message) {
        showAlert.value = true
        message.value = store.lastError.message
      }
    }
  )
</script>