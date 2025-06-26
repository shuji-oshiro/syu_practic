<template>
<v-window v-model="onboarding" show-arrows="hover">
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
  import { ref, onMounted, watch } from 'vue'
  import { UseEventStore, CommonEventStore } from '@/stores/eventStore'
  import { NavigationType } from '@/types/enums'
  import type { MenuOut_GP, MenuOut } from '@/types/menuTypes'


  const emit = defineEmits<{
    (e: 'click', value: MenuOut, navigation: NavigationType): void
  }>()
  
  const onboarding = ref(1)

  const useEventStore = UseEventStore()
  const commonEventStore = CommonEventStore()
  const groupedMenus = ref<MenuOut_GP[]>([]) // カテゴリごとにグループ化されたメニュー

  // メニュー情報を更新するための関数
  // CSVファイルを受け取り、DBに送信する
  async function importMenus(formData: FormData) {
    // DBに送信するためのPOSTリクエスト
    try{
      const response = await axios.post('http://localhost:8000/menu', formData)
      // TODO:　メニュー画面更新処理は後日実装
    }catch (error) {
      if (axios.isAxiosError(error)) {
        // FastAPI 側の raise HTTPException(..., detail="...") を拾う
        const errorMessage = error.response?.data?.detail || 'サーバーからの応答がありません'
        commonEventStore.reportError("メニューの一括更新中にエラーが発生しました", errorMessage)
      } else {
        commonEventStore.reportError('メニュー更新中に予期しないエラーが発生しました')
      }
    }
  }

  // メニューが選択された時の処理
  // 親コンポーネントに選択されたメニューを通知する
  async function selectMenu(menu: MenuOut) {
    emit('click', menu, NavigationType.Order)
  }
  
  // ナビゲーションバーよりカテゴリが選択された時、またはメニューがインポートされた時の処理を監視
  watch(
    () => [useEventStore.selectCategoryAction.timestamp, useEventStore.importMenusAction.timestamp],
    () => {
      if (useEventStore.selectCategoryAction.categoryId) {
        onboarding.value = useEventStore.selectCategoryAction.categoryId
      }
      if (useEventStore.importMenusAction.formData) {
        importMenus(useEventStore.importMenusAction.formData)
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