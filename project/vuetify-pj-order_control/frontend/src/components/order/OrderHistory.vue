<template>
  <v-list-item
    title="注文履歴"
  ></v-list-item>        
  <v-list density="compact" nav>
    <v-list-item prepend-icon="mdi-view-dashboard" title="座席番号"></v-list-item>
    <v-list-item prepend-icon="mdi-forum" title="ご注文金額"></v-list-item>
  </v-list>
  <v-data-table-virtual
    :headers="headers"
    :items="orders"
    height="80vh"
    item-value="name"
    fixed-header
  ></v-data-table-virtual>
</template>

<script setup >
  import axios from 'axios'
  import { ref ,onMounted, watch} from 'vue'
  import { useEventStore } from '@/stores/eventStore'
  const orders = ref([]) // 注文リスト
  const store = useEventStore()

  const headers = [
    { title: '商品名', align: 'start', key: 'menu.name' },
    { title: '単価', align: 'end', key: 'menu.price'},
    { title: '注文数', align: 'end', key: 'order_cnt' },
    { title: '合計金額', align: 'end', key: 'total_price', value: item => (item.menu.price * item.order_cnt) }
  ]

  async function getOrderInfo(order) {
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
  }

  // 初期化時に注文情報を取得
  onMounted(async () => {
    getOrderInfo()
  })

  // 注文情報が更新されたときに再取得
  watch(
    () => store.updateOrderAction.timestamp,
    () => {
      if (store.updateOrderAction.timestamp) {
        getOrderInfo()
      }
    },
    { deep: true }
  ) 

  function formatPrice (value) {
    return `$${value.toFixed(0).replace(/\d(?=(\d{3})+$)/g, '$&,')}`
  }
</script>