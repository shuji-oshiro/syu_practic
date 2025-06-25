<template>
  <v-list-item
      title="メニューカテゴリ"
  ></v-list-item>
  <v-divider></v-divider>
  
  <v-list density="compact" nav>
    <!-- <v-list-item v-for="(category, index) in categories" 
      :key="category.id" 
      :prepend-icon="category.icon" 
      :title="category.name" @click="selectCategory(index)">
      {{ category.description }}
    </v-list-item> -->
    <v-card
        v-for="(category, index) in categories"
        :key="category.id"
        :title="category.name"
        :subtitle="category.description"
        @click="selectCategory(index)"
      ></v-card>
  </v-list>
</template>

<script setup lang="ts">
  import axios from 'axios'
  import { ref, onMounted } from 'vue'
  import { useEventStore } from '@/stores/eventStore'
  const store = useEventStore()
  const categories = ref([] as any[])

  function selectCategory(id: number) {
    console.log('カテゴリが選択されました:', id)
    store.triggerCategoryAction(id) // ← Pinia に記録！
  }

  async function getCategoryInfo() {
    try {
      // カテゴリ単位の現在のメニュー状況を取得
      const response = await axios.get(`http://localhost:8000/category`)
      
      if (response.status === 200) {
        categories.value = response.data || []
      } else {
        throw new Error('カテゴリの取得に失敗しました')
      }
    } catch (error) {
      // errorMessage.value = error instanceof Error ? error.message : '不明なエラーが発生しました'
    }
  }

  onMounted(() => {
    getCategoryInfo()
  })

</script>