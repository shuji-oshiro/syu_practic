<template>
  <v-list-item
      title="メニューカテゴリ"
  ></v-list-item>
  <v-divider></v-divider>
  
  <v-list density="compact" nav>
    <v-card
        v-for="(category, index) in categories"
        :key="category.id"
        :title="category.name"
        :subtitle="category.description"
        @click="selectCategory(category.id)"
      ></v-card>
  </v-list>
</template>

<script setup lang="ts">
  import axios from 'axios'
  import { ref, onMounted } from 'vue'
  import { useEventStore } from '@/stores/eventStore'
  const store = useEventStore()
  const categories = ref([] as any[])

  // カテゴリが選択された時の処理
  // 注文画面に遷移し、選択されたカテゴリを Pinia に記録
  // カテゴリIDを引数に受け取り、Pinia のアクションを呼び出す
  function selectCategory(id: number) {
    store.triggerSelectCategoryAction(id) 
  }

  // カテゴリ情報を取得する関数
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

  // コンポーネントがマウントされた時にカテゴリ情報を取得
  onMounted(() => {
    getCategoryInfo()
  })

</script>