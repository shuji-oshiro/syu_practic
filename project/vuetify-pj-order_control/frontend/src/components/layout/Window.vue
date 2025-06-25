<template>
  <v-window
    v-model="onboarding"
    show-arrows="hover"
  >
    <v-window-item>
        <FoodMenusList />
    </v-window-item>
    <v-window-item>
        <DrinkMenusList />
    </v-window-item>
  </v-window>
</template>

<script setup>
  import { ref } from 'vue'
  import { watch } from 'vue'
  import { useEventStore } from '@/stores/eventStore'
  const onboarding = ref(0)
  
  const store = useEventStore()
  watch(
    () => store.categoryAction,
    (newVal, oldVal) => {
      console.log('カテゴリアクションが更新されました:', newVal)
      if (newVal.categoryId !== oldVal?.categoryId) {
        onboarding.value = newVal.categoryId // カテゴリーIDに基づいてウィンドウを切り替える
      }
    },
    { deep: true }
  )
</script>