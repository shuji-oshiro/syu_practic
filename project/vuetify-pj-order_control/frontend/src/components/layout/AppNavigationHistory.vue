<template>
  <v-navigation-drawer 
    v-model="isNavigation"
    temporary
  >
    <OrderHistory />
  </v-navigation-drawer>  
</template>

<script setup lang="ts">
  import { ref, watch } from 'vue'
  import { EventAppNavigation } from '@/stores/eventStore'

  const appNavigation = EventAppNavigation()
  const isNavigation = ref<boolean>(false)

  // メニュー、注文履歴、注文画面の表示状態を監視
//   watch(
//   () => appNavigation.isHistory,
//   () => {
//     isNavigation.value = true
//   }
// )
  </script>