<template>
<v-window v-model="onboarding" show-arrows="hover">
  <v-window-item
    v-for="(menuGroup, categoryId) in groupedMenus"
    :key="Number(categoryId)"
  >
  <h3>カテゴリ {{ categoryId }}</h3>
  <v-container>
    <div style="max-height: 90vh; overflow-y: auto; overflow-x: hidden;">
        <v-row dense>
          <v-col
            v-for="menu in menuGroup"
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
  const onboarding = ref(0)
  
  const store = useEventStore()
  const groupedMenus = ref<Record<number, any[]>>({}) // カテゴリごとにグループ化されたメニュー

  // メニュー情報をカテゴリごとにグループ化する関数
  // メニューのカテゴリIDをキーにしてグループ化
  function getGroupedMenus(menus: any[]) {
    const groups: Record<number, any[]> = {}
    for (const menu of menus) {
      const cid = menu.category_id || 0
      if (!groups[cid]) {
        groups[cid] = []
      }
      groups[cid].push(menu)
    }
    return groups
  }

  // メニュー情報を更新するための関数
  // CSVファイルを受け取り、DBに送信する
  async function importMenus(formData: FormData) {
    // DBに送信するためのPOSTリクエスト
    const response = await axios.post('http://localhost:8000/menu', formData)
    if (response.status !== 200) {
      throw new Error('メニューの更新に失敗しました')
    }
    const menus = response.data.menus || []
    groupedMenus.value = getGroupedMenus(menus)
    alert('メニューが更新されました')  // メニュー更新後のアラート
  }

  // メニューが選択された時の処理
  // 注文画面に遷移し、選択されたメニューを Pinia に記録
  async function selectMenu(menu: any) {
    await store.triggerShowNavigationAction('order', 'OrderConfirm') // 注文画面を表示
    await store.triggerMenuSelectAction(menu) // ← Pinia に記録！
  }
  
  watch(
    () => [store.categoryAction.timestamp, store.importMenusAction.timestamp],
    () => {
      if (store.categoryAction.categoryId) {
        onboarding.value = store.categoryAction.categoryId
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
      const response = await axios.get('http://localhost:8000/menu')
      if (response.status === 200) {
        const menus = response.data || []
        groupedMenus.value = getGroupedMenus(menus) // カテゴリごとにグループ化
      } else {
        throw new Error('メニューの取得に失敗しました')
      }
    } catch (error) {
      alert('メニューの取得に失敗しました')
    }
  })

</script>