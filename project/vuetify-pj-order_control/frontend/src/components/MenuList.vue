<!-- components/OrderMenu.vue -->
<template>
  <v-sheet
    v-if="show"
    color="primary"
    class="pa-4 d-flex flex-column"
    dark
    style="position: absolute; top: 0; left: 0; right: 0; bottom: 56px; z-index: 10;"
  >
    <div class="text-h6 mb-4">
      メニュー
      <ImportCSVBtn @csvdata="importCSV" @error="handleError" />
    </div>

    <v-sheet color="grey darken-3" elevation="2" class="flex-grow-1 overflow-y-auto mb-4 rounded">
        <v-list density="compact">
            <v-list-item
            v-for="(menu, index) in menus"
            :key="index"
            :title="menu"
            prepend-icon="mdi-food"
            />
        </v-list>
        <v-alert v-if="errorMessage" type="error" class="ma-4">
            {{ errorMessage }}
        </v-alert>
        <v-alert v-if="message" type="info" class="ma-4">
        {{ message }}
        </v-alert>
    </v-sheet>
  </v-sheet>
</template>

<script setup lang="ts">
import axios from 'axios'
import { ref } from 'vue'
import ImportCSVBtn from '@/components/ImportCSVBtn.vue'
defineProps<{ show: boolean }>()

// メッセージ表示用
const message = ref<string>('')
// エラーメッセージ用
const errorMessage = ref<string | null>(null)
// メニューリスト
const menus = ref<string[]>([])

// CSVデータをインポートする関数
const importCSV = async (formData: FormData) => {
  // DBに送信するためのPOSTリクエスト
  const response = await axios.post('http://localhost:8000/menu', formData)
  if (response.status !== 200) {
    throw new Error('メニューの更新に失敗しました')
  }
  menus.value = response.data.menus || []
  message.value = 'メニューが更新されました'  // メニュー更新後のメッセージ
  errorMessage.value = null  // エラーメッセージをクリア
}
// エラー処理
const handleError = (message: string) => {
  errorMessage.value = message
}

// onMounted(async () => {
//   try {
//     const response = await fetch('http://localhost:8000/menu', {
//       method: 'GET'
//     })

//     if (!response.ok) {
//       // ステータスコードに応じてエラー処理
//       const errorData = await response.json()
//       if (response.status === 404) {
//         errorMessage.value = errorData.detail  // "Menu not found"
//       } else if (response.status === 400) {
//         errorMessage.value = "不正なメニューIDです"
//       } else {
//         errorMessage.value = "予期しないエラーが発生しました"
//       }
//       return
//     }

//     const data = await response.json()
//     console.log(data)
//   } catch (error) {
//     console.error('Fetch error:', error)
//     errorMessage.value = 'サーバーへの接続に失敗しました'
//   }
// })


</script>
