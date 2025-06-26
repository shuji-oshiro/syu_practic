<template>
    <v-list-item
        title="注文確認"
    ></v-list-item>
    <v-list density="compact">
      <!-- 今後リストでの注文更新する際は検討 -->
      <!-- <v-list-item 
        v-for="menu in menus"
        :key="menu.id"
        class="menu-item"
        lines="three"
      > -->
        <v-card
          elevated
          class="mx-auto"
          color="surface-variant"
          max-width="200px"
        >
          <template #title>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>{{ menus?.name }}</span>
              <span style="font-weight: bold;">¥{{ menus?.price }}</span>
            </div>
          </template>
          <v-img
            height="100px"
            src="https://cdn.vuetifyjs.com/images/cards/sunshine.jpg"
            cover
          ></v-img>
        </v-card>
      <!-- </v-list-item> -->
    </v-list>
    <div class="d-flex align-center mt-2" style="gap: 8px; width: 100%;">
      <v-number-input
        control-variant="split"
        v-model="quantity"
        :min="1"
        :max="10"
        hide-details
      >
      </v-number-input>
    </div>
    <div>
      <v-btn color="primary" :width="'100%'" @click="on_order_commit">
          注文
      </v-btn>
    </div>
</template>

<script setup lang="ts">
    import axios from 'axios'
    import { ref ,watch} from 'vue'
    import { useEventStore } from '@/stores/eventStore'
    import type { MenuOut } from '@/types/menuTypes'
    
    const store = useEventStore()
    const menus = ref<MenuOut>() // 選択されたメニュー
    const quantity = ref<number>(0)
    
    // メニュー画面より商品が選択された時を検知
    watch(
        () => store.menuSelectAction.timestamp,
        () => {
            if (store.menuSelectAction.menu){
              quantity.value = 1 // 数量を初期化
              menus.value = store.menuSelectAction.menu // 選択されたメニューをセット
            }
        }
    )

    // 注文確定ボタンのクリックイベント
    async function on_order_commit() {
      try{
        // 注文データをサーバーに送信
        const response = await axios.post('http://localhost:8000/order', [{
            "seat_id": 1,
            "menu_id": menus.value?.id,
            "order_cnt": quantity.value
        }])      
        store.reportInfo("ご注文ありがとうございました", menus.value?.name + "*" + quantity.value )
        // 注文が成功したら、注文履歴を更新
        store.triggerUpdateOrderAction() 
        //store.clearMenuAction() // Pinia の状態をクリア

      } catch (error) {
        if (axios.isAxiosError(error)) {
          const errorMessage = error.response?.data?.detail || 'サーバーからの応答がありません'
          store.reportError("注文登録中にエラーが発生しました", errorMessage)
        } else {
          store.reportError('注文登録中に予期しないエラーが発生しました')
        }
      }
    }  
  </script>