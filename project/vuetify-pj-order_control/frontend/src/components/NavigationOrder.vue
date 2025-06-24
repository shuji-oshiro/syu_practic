<template>
  <v-navigation-drawer v-model="flg_order"
      temporary
  >
    <v-list-item
        title="注文確認"
    ></v-list-item>
    <v-list density="compact">
      <v-list-item
        v-for="menu in menus"
        :key="menu.id"
        class="menu-item"
        lines="three"
      >
        <v-card
          elevated
          class="mx-auto"
          color="surface-variant"
          max-width="200px"
          :title="menu.name"
          :subtitle="menu.description"
        >
          <template #title>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>{{ menu.name }}</span>
              <span style="font-weight: bold;">¥{{ menu.price }}</span>
            </div>
          </template>
          <v-img
            height="100px"
            src="https://cdn.vuetifyjs.com/images/cards/sunshine.jpg"
            cover
          ></v-img>
        </v-card>
      </v-list-item>
    </v-list>
    <div v-if="menus && menus.length === 1" class="d-flex align-center mt-2" style="gap: 8px; width: 100%;">
        <v-text-field
          v-model.number="quantity"
          placeholder="数量を入力"
          type="number"
          min="1"
          max="10"
          class="flex-grow-1"
          style="flex: 0 0 100%; max-width: none; text-align: right;"
          hide-details
          :step="1"
          :rules="[
              v => (v >= 1 && v <= 10) || '1～10の数値を入力してください'
          ]"
        />
    </div>
    <div>
      <v-btn color="primary" :width="'100%'" @click="on_order_commit">
          注文
      </v-btn>
    </div>
    <order-history />
  </v-navigation-drawer>
</template>

<script setup lang="ts">
    import axios from 'axios'
    import { ref ,onMounted, watch} from 'vue'
    import { useEventStore } from '@/stores/eventStore'
    
    const store = useEventStore()
    const flg_order = ref<boolean>(false)
    const menus = ref<any[]>([])
    const menuid = ref<number>(0)
    const quantity = ref(0)
    watch(
        () => store.menuAction,
        (newVal, oldVal) => {
            on_order(newVal.menu)
        },
        { deep: true }
    )

    // 注文画面を開くための関数
    // メニューが配列で渡されることを想定
    function on_order(newMenu: any) {
      quantity.value = 1 // 数量を初期化
      flg_order.value = true // 注文画面を開く
      // 配列で受け取るように修正
      menus.value = Array.isArray(newMenu) ? newMenu : [newMenu]
      menuid.value = menus.value[0].id
    }

    // 注文確定ボタンのクリックイベント
    async function on_order_commit() {

      try{
        if (quantity.value < 1 || quantity.value > 10) {
            alert('数量は1～10の範囲で入力してください。')
            return
        }
        const response = await axios.post('http://localhost:8000/order', [{
            "seat_id": 1,
            "menu_id": menuid.value,
            "order_cnt": quantity.value
        }])

        if (response.status === 200) {
            alert('注文が完了しました。')
            flg_order.value = false // 注文画面を閉じる
            store.triggerUpdateOrderAction() 
            //store.clearMenuAction() // Pinia の状態をクリア
        } else {
            alert('注文に失敗しました。')
        }

      } catch (error) {
          alert('注文に失敗しました。')
          return
      }
    }

    const orders = ref<any[]>([]) // 注文リスト
    onMounted(async () => {
      try {
        // シート単位の現在の注文状況を取得
        const response = await axios.get('http://localhost:8000/order/1')
        if (response.status === 200) {
          orders.value = response.data || []
        } else {
          throw new Error('注文の取得に失敗しました')
        }
      } catch (error) {
        // errorMessage.value = error instanceof Error ? error.message : '不明なエラーが発生しました'
      }
    })

    
  </script>