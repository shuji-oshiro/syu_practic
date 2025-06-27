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
  import { NavigationType } from '@/types/enums'
  import type { MenuOut_GP, MenuOut } from '@/types/menuTypes'
  import { UseEventStore, CommonEventStore } from '@/stores/eventStore'


  const emit = defineEmits<{
    (e: 'click', value: MenuOut, navigation: NavigationType): void
  }>()
  
  const onboarding = ref(1)

  const useEventStore = UseEventStore()
  const commonEventStore = CommonEventStore()
  const groupedMenus = ref<MenuOut_GP[]>([]) // カテゴリごとにグループ化されたメニュー

  // メニューが選択された時の処理
  // 親コンポーネントに選択されたメニューを通知する
  async function selectMenu(menu: MenuOut) {
    emit('click', menu, NavigationType.Order)
  }
  
  // ナビゲーションバーよりカテゴリが選択された時の処理を監視
  watch(
    () => [useEventStore.selectCategoryAction.timestamp],
    () => {
      if (useEventStore.selectCategoryAction.categoryId) {
        onboarding.value = useEventStore.selectCategoryAction.categoryId
      }
    }
  )

  // コンポーネントがマウントされた時にメニュー情報を取得
  // 初期メニューを取得し、menusに格納 
  onMounted(async () => {
    try {
      // 初期メニューの取得
      const response = await axios.get('http://localhost:8000/menulist')
      groupedMenus.value = response.data || []
        
    } catch (error) {
      if (axios.isAxiosError(error)) {
        // FastAPI 側の raise HTTPException(..., detail="...") を拾う
        const errorMessage = error.response?.data?.detail || 'サーバーからの応答がありません'
        commonEventStore.reportError("メニュー情報の取得中にエラーが発生しました", errorMessage)
      } else {
        commonEventStore.reportError('メニュー情報の取得中に予期しないエラーが発生しました')
      }
    }
  })

</script>