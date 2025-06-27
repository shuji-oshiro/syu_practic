<template>
  <v-btn @click="openFileDialog">
    <v-icon >mdi-import</v-icon>
    <span>更新</span>
  </v-btn>
</template>

<script setup lang="ts">
import axios from 'axios'
import { CommonEventStore } from '@/stores/eventStore'
const commonEventStore = CommonEventStore()

const openFileDialog = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.csv'
  input.addEventListener('change', async (event) => {
    const file = (event.target as HTMLInputElement).files?.[0]
    if (file) {
      const formData = new FormData()
      formData.append('file', file)
      await importMenus(formData)
    }
  })
  input.click()
}

// メニュー情報を更新するための関数
// CSVファイルを受け取り、DBに送信する
async function importMenus(formData: FormData) {
  // DBに送信するためのPOSTリクエスト
  try{
    const response = await axios.post('http://localhost:8000/menu', formData)
    // TODO:　メニュー画面更新処理は後日実装
  }catch (error) {
    if (axios.isAxiosError(error)) {
      // FastAPI 側の raise HTTPException(..., detail="...") を拾う
      const errorMessage = error.response?.data?.detail || 'サーバーからの応答がありません'
      commonEventStore.reportError("メニューの一括更新中にエラーが発生しました", errorMessage)
    } else {
      commonEventStore.reportError('メニュー更新中に予期しないエラーが発生しました')
    }
  }
}
</script>
