<template>
  <v-list-item
      prepend-avatar="https://randomuser.me/api/portraits/men/78.jpg"
      title="メニューカテゴリ"
  ></v-list-item>
  <v-divider></v-divider>
  <v-list density="compact" nav>
      <v-list-item prepend-icon="mdi-view-dashboard" title="カテゴリ1" value="home" @click="selectCategory(0)"></v-list-item>
      <v-list-item prepend-icon="mdi-forum" title="カテゴリ2" value="about" @click="selectCategory(1)"></v-list-item>
  </v-list>
</template>

<script setup lang="ts">
  import { useEventStore } from '@/stores/eventStore'
  const store = useEventStore()

  function selectCategory(id: number) {
    console.log('カテゴリが選択されました:', id)
    store.triggerCategoryAction(id) // ← Pinia に記録！
  }
</script>