<template>
  <v-list-item
    title="おすすめメニュー"
  ></v-list-item>        
  <div style="max-height: 90vh; overflow-y: auto; overflow-x: hidden;">
    <v-row dense>
      <v-col
        v-for="menu in recomend_menus"
        :key="menu.id"
        cols="12"
        md="4"
      >
      <FoodCard :menu="menu" :onClick="() => selectMenu(menu)" />
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
  import axios from 'axios'
  import { ref, onMounted, watch } from 'vue'
  import { useEventStore } from '@/stores/eventStore'
  import type { MenuOut } from '@/types/menuTypes'

  const recomend_menus  = ref<MenuOut[]>([]) // 注文リスト
  const store = useEventStore()

  const selectMenu = (menu: MenuOut) => {
    store.triggerMenuSelectAction(menu)
  }


  // 情報を取得する関数
  // 注文情報は、座席IDを指定して取得する
  async function getRecomendMenu() {
    try {
      // シート単位の現在の注文状況を取得
      const response = await axios.get('http://localhost:8000/menu/category/1')
      recomend_menus.value = response.data || []

    } catch (error) {
      if (axios.isAxiosError(error)) {
        const errorMessage = error.response?.data?.detail || 'サーバーからの応答がありません'
        store.reportError("注文履歴情報の取得中にエラーが発生しました", errorMessage)
      } else {
        store.reportError('注文履歴情報の取得中に予期しないエラーが発生しました')
      }
    }
  }

  // 初期化時に注文情報を取得
  onMounted(
    getRecomendMenu
  )

  // // 注文情報が更新されたときに再取得
  // watch(
  //   () => store.updateOrderAction.timestamp,
  //   () => {
  //     if (store.updateOrderAction.timestamp) {
  //       getOrderInfo()
  //     }
  //   }
  // ) 
</script>