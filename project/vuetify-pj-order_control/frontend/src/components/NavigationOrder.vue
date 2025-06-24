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

  watch(
  () => [store.menuAction.timestamp, store.showNavigationAction.timestamp],
  ([menuTime, navTime]) => {
    
    if (!menuTime && !navTime) return
    
    // どちらが新しいイベントかを比較
    if ((menuTime || 0) > (navTime || 0)) {
      // menuAction の方が新しい → 注文処理を優先
      if (store.menuAction.menu) {
        isOrder.value = true
        isHistory.value = true
        isMenuCategory.value = false
      }
    } else {
      // showNavigationAction の方が新しい → targetによる分岐
      const target = store.showNavigationAction.target
      if (target === 'history') {
        isOrder.value = false
        isHistory.value = true
        isMenuCategory.value = false
      } else if (target === 'category') {
        isOrder.value = false
        isHistory.value = false
        isMenuCategory.value = true
      }
    }
    isNavigation.value = true
  }
)
  </script>