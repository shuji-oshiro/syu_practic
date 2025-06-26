<template>
<v-window v-model="onboarding" show-arrows="hover">
  <!-- <v-window-item
    v-for="(menuGroup, categoryId) in groupedMenus"
    :key="Number(categoryId)"
    :value="Number(categoryId)"
  > -->
  <v-window-item
    v-for="menuGroup in groupedMenus"
    :key="menuGroup.category_id"
    :value="menuGroup.category_id"
  >

  <h3>カテゴリ {{ menuGroup.category_name }}</h3>
  <v-container>
    <div style="max-height: 90vh; overflow-y: auto; overflow-x: hidden;">
        <v-row dense>
          <v-col
            v-for="menu in menuGroup.menues"
            :key="menu.id"
            cols="12"
            md="4"
          >
          <FoodCard :menu="menu" :onClick="() => selectMenu(menu)" />
          </v-col>
        </v-row>
      </div>
    </v-container>
  </v-window-item>
</v-window>

</template>

<script setup lang="ts">
  // Vuetify ダミーデータ
  //const variants = ['elevated', 'flat', 'tonal', 'outlined', 'text', 'plain'] as const  
  
  import axios from 'axios'
  import { ref, onMounted, watch, computed } from 'vue'
  import { useEventStore } from '@/stores/eventStore'
  import type { MenuOut_SP } from '@/types/menuTypes'
  const onboarding = ref(1)
  


  const store = useEventStore()
  const groupedMenus = ref<MenuOut_SP[]>([]) // カテゴリごとにグループ化されたメニュー

  // メニュー情報を更新するための関数
  // CSVファイルを受け取り、DBに送信する
  async function importMenus(formData: FormData) {
    // DBに送信するためのPOSTリクエスト
    try{
      const response = await axios.post('http://localhost:8000/menu', formData)
      groupedMenus.value = response.data.menus || []
    }catch (error) {
      if (axios.isAxiosError(error)) {
        // FastAPI 側の raise HTTPException(..., detail="...") を拾う
        const errorMessage = error.response?.data?.detail || 'サーバーからの応答がありません'
        store.reportError(`メニューの更新に失敗しました: ${errorMessage}`)
      } else {
        store.reportError('メニュー更新中に予期しないエラーが発生しました')
      }
    }
  }

  // メニューが選択された時の処理
  // 注文画面に遷移し、選択されたメニューを Pinia に記録
  async function selectMenu(menu: any) {
    await store.triggerShowNavigationAction('order', 'OrderConfirm') // 注文画面を表示
    await store.triggerMenuSelectAction(menu) // ← Pinia に記録！
  }
  
  // ナビゲーションバーよりカテゴリが選択された時、またはメニューがインポートされた時の処理を監視
  watch(
    () => [store.selectCategoryAction.timestamp, store.importMenusAction.timestamp],
    () => {
      if (store.selectCategoryAction.categoryId) {
        onboarding.value = store.selectCategoryAction.categoryId
      }
      if (store.importMenusAction.formData) {
        importMenus(store.importMenusAction.formData)
      }
    }
  )

    // コンポーネントがマウントされた時にメニュー情報を取得
  // 初期メニューを取得し、menusに格納 
  onMounted(async () => {
    try {
      // 初期メニューの取得
      const response = await axios.get('http://localhost:8000/menulist')
      if (response.status === 200) {
        groupedMenus.value = response.data || []
        
      } else {
        throw new Error('メニューの取得に失敗しました')
      }
    } catch (error) {
      alert('メニューの取得に失敗しました')
    }
  })

</script>