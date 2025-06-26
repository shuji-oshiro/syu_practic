<template>
  <v-navigation-drawer 
    v-model="isNavigation"
    temporary
  >
  <OrderConfirm v-if="isOrder"/>
  <OrderHistory v-if="isHistory"/>
  <MenuCategory v-if="isMenuCategory"/>
  </v-navigation-drawer>  
</template>

<script setup lang="ts">
  import { ref, watch } from 'vue'
  import { useEventStore } from '@/stores/eventStore'
  const store = useEventStore()

  const isNavigation = ref<boolean>(false)
  const isOrder = ref<boolean>(false)
  const isHistory = ref<boolean>(false)
  const isMenuCategory = ref<boolean>(false)

  // メニュー、注文履歴、注文画面の表示状態を監視
  watch(
  () => store.showNavigationAction.timestamp,
  () => {
      const target = store.showNavigationAction.target
      if (target === 'history') {
        isOrder.value = false
        isHistory.value = true
        isMenuCategory.value = false
      } else if (target === 'category') {
        isOrder.value = false
        isHistory.value = false
        isMenuCategory.value = true
      }else if (target === 'order') {
        isOrder.value = true
        isHistory.value = false
        isMenuCategory.value = false
      } else {
        isOrder.value = false
        isHistory.value = false
        isMenuCategory.value = false
    }
    isNavigation.value = true
  }
)
  </script>