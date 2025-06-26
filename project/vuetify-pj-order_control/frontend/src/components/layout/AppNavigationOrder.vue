<template>
  <v-navigation-drawer 
    v-model="isNavigation"
    temporary
  >
    <OrderConfirm />
    <MenuRecomend />
  </v-navigation-drawer>  
</template>

<script setup lang="ts">
  import { ref, watch } from 'vue'
  import { UseEventStore } from '@/stores/eventStore'

  const useEventStore = UseEventStore()

  const isNavigation = ref<boolean>(false)
  const isMenuRecomend = ref<boolean>(false)

  // 注文画面よりメニューが選択された時の処理を監視
  watch(
  () => useEventStore.menuSelectAction.timestamp,
  () => {
    isNavigation.value = true
  }
)
  </script>