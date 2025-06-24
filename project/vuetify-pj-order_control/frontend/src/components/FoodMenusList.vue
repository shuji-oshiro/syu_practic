<template>
  <div style="max-height: 90vh; overflow-y: auto; overflow-x: hidden;">
    <v-row dense>
      <v-col
        v-for="(menu, i) in menus"
        :key="menu.id"
        cols="12"
        md="4"
      >  
        <v-card
          elevated
          class="mx-auto"
          color="surface-variant"
          max-width="344px"
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
            height="300px"
            src="https://cdn.vuetifyjs.com/images/cards/sunshine.jpg"
            cover
          ></v-img>
          <template v-slot:actions >
            <v-btn text="注文" @click="selectMenu(menu)" width="100%"></v-btn>
          </template>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
  import axios from 'axios'
  import { ref, onMounted, watch } from 'vue'
  import { useEventStore } from '@/stores/eventStore'
  
  const store = useEventStore()
  const menus = ref<any[]>([]) // メニューリスト
  // Vuetify ダミーデータ
  //const variants = ['elevated', 'flat', 'tonal', 'outlined', 'text', 'plain'] as const  
  
  async function importMenus(formData: FormData) {
    // DBに送信するためのPOSTリクエスト
    const response = await axios.post('http://localhost:8000/menu', formData)
    if (response.status !== 200) {
      throw new Error('メニューの更新に失敗しました')
    }
    menus.value = response.data.menus || []
    alert('メニューが更新されました')  // メニュー更新後のアラート    
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
      alert('メニューの取得に失敗しました')
    }
  })
  
  function selectMenu(menu: any) {
    store.triggerMenuAction(menu) // ← Pinia に記録！
  }

  // メニュー情報を更新するCSVファイルが読み込まれた時の処理
  watch(
    () => store.importMenusAction,
    (newVal, oldVal) => {
        if (newVal && newVal.formData) {
          importMenus(newVal.formData)
        }
    },
    { deep: true }
  ) 
    
</script>