<!-- components/OrderMenu.vue -->
<template>
  <v-sheet
    v-if="show"
    color="primary"
    class="pa-4 d-flex flex-column"
    dark
    style="position: absolute; top: 0; left: 0; right: 0; bottom: 56px; z-index: 10;"
  >
    <div class="text-h6 mb-4">メニュー</div>

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
import { ref, onMounted  } from 'vue'
defineProps<{ show: boolean }>()

// ダミーメニューデータ
const menus = ref<string[]>(Array.from({ length: 10 }, (_, i) => `メニュー ${i + 1}`))

// メッセージ表示用
const message = ref<string>('')

// エラーメッセージ用
const errorMessage = ref<string | null>(null)

onMounted(async () => {
  try {
    const response = await fetch('http://localhost:8000/menu', {
      method: 'GET'
    })

    if (!response.ok) {
      // ステータスコードに応じてエラー処理
      const errorData = await response.json()
      if (response.status === 404) {
        errorMessage.value = errorData.detail  // "Menu not found"
      } else if (response.status === 400) {
        errorMessage.value = "不正なメニューIDです"
      } else {
        errorMessage.value = "予期しないエラーが発生しました"
      }
      return
    }

    const data = await response.json()
    console.log(data)
    message.value = data.message  // ← "This is a test endpoint for voice API." が入る
  } catch (error) {
    console.error('Fetch error:', error)
    errorMessage.value = 'サーバーへの接続に失敗しました'
  }
})


</script>
