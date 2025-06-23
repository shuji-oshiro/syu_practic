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
          v-for="menu in menus"
          :key="menu.id"
          class="menu-item"
          prepend-icon="mdi-food"
          lines="3"
        >
        <!-- メニューのアイコンを表示 -->
         <!-- name,price,decriptionの横に数値を入力できるテキストボックスを表示 -->
        <template #prepend>
          <v-avatar>
            <v-icon v-if="!menu.image" size="32">mdi-food</v-icon>
            <!-- <v-img :src="menu.image" /> -->
          </v-avatar>
        </template>
        <v-list-item-title>
          {{ menu.name }}
        </v-list-item-title>
        <v-list-item-subtitle class="subtitle-wrap">
          ¥{{ menu.price }}<br />
          {{ menu.description }}
        </v-list-item-subtitle>
        <v-list-item-action>
          <v-text-field
            v-model="menu.quantity"
            type="number"
            min="0"
            label="数量"
            class="mt-2"
          />
        </v-list-item-action>
      </v-list-item>
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
import { ref, onMounted } from 'vue'
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
}

// エラー処理
const handleError = (message: string) => {
  errorMessage.value = message
}

onMounted(async () => {
  try {
    // 初期メニューの取得
    const response = await axios.get('http://localhost:8000/menu')
    if (response.status === 200) {
      menus.value = response.data || []
    } else {
      throw new Error('メニューの取得に失敗しました')
    }
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '不明なエラーが発生しました'
  }
})

</script>
