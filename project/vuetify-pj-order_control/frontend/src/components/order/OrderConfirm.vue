<template>
    <v-list-item
        title="注文確認"
    ></v-list-item>
    <v-list density="compact">
      <v-list-item 
        v-for="(item, index) in order_list"
        :key="item.order_menu.id"
        class="menu-item"
        lines="three"
      >
        <v-card
          elevated
          class="mx-auto"
          color="surface-variant"
          max-width="200px"
        >
          <template #title>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>{{ item.order_menu?.name }}</span>
              <span style="font-weight: bold;">¥{{ item.order_menu?.price }}</span>
            </div>
            <v-number-input
              control-variant="split"
              v-model="item.order_cnt"
              :min="0"
              :max="10"
              hide-details
            >
            </v-number-input>
          </template>
        </v-card>
      </v-list-item>
    </v-list>
    <div>
      <v-btn color="primary" :width="'100%'" @click="on_order_commit">
          注文
      </v-btn>
    </div>
</template>

<script setup lang="ts">
  import axios from 'axios'
  import { ref ,watch} from 'vue'
  import { AlertType } from '@/types/enums'
  import { UseEventStore, CommonEventStore } from '@/stores/eventStore'
  import type { MenuOut } from '@/types/menuTypes'

  const useEventStore = UseEventStore()
  const commonEventStore = CommonEventStore()

  // 注文リストを管理するための型定義　ここでしか使用しないので、コンポーネント内で定義
  interface typeList {
    order_menu: MenuOut,
    order_cnt: number
  }

  const order_list = ref<typeList[]>([]) // 注文リスト

  // メニュー画面より商品が選択された時を検知
  watch(
      () => [useEventStore.menuSelectAction.timestamp],
      () => {
          if (useEventStore.menuSelectAction.menu){
            const selectedMenu = useEventStore.menuSelectAction.menu // 選択されたメニューをセット
            // 注文リストに選択されたメニューが存在しない場合、追加
            if (!order_list.value.some(item => item.order_menu.id === selectedMenu.id)) {
              order_list.value.push({
                order_menu: selectedMenu,
                order_cnt: 1
              })
            }
              // order_cntが1以上のものだけを残す
              order_list.value = order_list.value.filter(item => item.order_cnt >= 1)
          }
      }
  )

  // 注文確定ボタンのクリックイベント
  async function on_order_commit() {
    try{
      // 注文データをサーバーに送信
      // order_cntが1以上のものだけを残す
      order_list.value = order_list.value.filter(item => item.order_cnt >= 1)
      // 保存用にデータを加工
      const orders = order_list.value.map(item => ({
        seat_id: 1, // 仮の座席ID、実際のアプリケーションでは適切な値を使用
        menu_id: item.order_menu.id,
        order_cnt: item.order_cnt
      }))

      const response = await axios.post('http://localhost:8000/order', orders)      

      commonEventStore.EventAlertInformation(
        AlertType.Success,
        "ご注文ありがとうございました",
        order_list.value
          .map(order => `${order.order_menu.name} × ${order.order_cnt}`)
          .join('\n') 
      )

      // 注文が成功したら、注文履歴を更新
      useEventStore.triggerUpdateOrderAction(true) 
    
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const errorMessage = error.response?.data?.detail || 'サーバーからの応答がありません'
        commonEventStore.EventAlertInformation(AlertType.Error, "注文登録中にエラーが発生しました", errorMessage)
      } else {
        commonEventStore.EventAlertInformation(AlertType.Error, "注文登録中にエラーが発生しました", '予期しないエラーが発生しました')
      }
    }finally {
      // 注文リストをクリア
      order_list.value = []
    } 
  }  
</script>