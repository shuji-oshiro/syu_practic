<template>
  <v-card>
    <v-layout>
      <AppNavigationCategory v-model="isNavigationCategory"/>
      <AppNavigationOrder v-model="isNavigationOrder"/>
      <AppNavigationHistory v-model="isNavigationHistory"/>
      <v-main style="height: 100vh;" >  
        <v-alert
          v-if="showAlert"
          closable
          :title="title"
          :text="message"
          :type="alertType"
          variant="tonal"
          @click:close="showAlert = false"
        ></v-alert>
        <MenuWindow @click="selectMenu" />
        <AppBottomNavigation @click="showNavigation" />
      </v-main>
    </v-layout>
  </v-card>
</template>
<script setup lang="ts">
  import { ref, watch} from 'vue'
  import { CommonEventStore } from '@/stores/eventStore'
  import { NavigationType } from '@/types/enums'
  import type { MenuOut } from '@/types/menuTypes'

  const emit = defineEmits<{
    (e: 'click', value: MenuOut): void
  }>()

  const isNavigationCategory = ref<boolean>(false)
  const isNavigationOrder = ref<boolean>(false)
  const isNavigationHistory = ref<boolean>(false)

  const store = CommonEventStore()
  const showAlert = ref(false)
  const message = ref('')
  const title = ref<string>('')
  const alertType = ref<'success' | 'info' | 'warning' | 'error'>('success')
  const icon = ref<'mdi-alert-circle' | 'mdi-information' | 'mdi-check-circle'>()
  // ナビゲーションバーよりカテゴリが選択された時、またはメニューがインポートされた時の処理を監視
  watch(
    () => [store.lastError.timestamp, store.lastInfo.timestamp, store.lastWarning.timestamp],
    () => {
      showAlert.value = true  
      if (store.lastError.message) {
        title.value = store.lastError.message
        message.value = store.lastError.detail
        icon.value = 'mdi-alert-circle'
        alertType.value = 'error' // エラータイプ
      } else if (store.lastWarning.message) {
        title.value = store.lastWarning.message
        message.value = store.lastWarning.detail
        icon.value = 'mdi-alert-circle'
        alertType.value = 'warning' // 警告タイプ
      } else if (store.lastInfo.message) {
        title.value = store.lastInfo.message
        message.value = store.lastInfo.detail
        icon.value = 'mdi-information'
        alertType.value = 'info' // 情報タイプ
      }
    }
  )

  function selectMenu(menu: MenuOut, navigation: NavigationType) {
    // 親コンポーネントに選択されたメニューを通知する
    emit('click', menu)
    //TODO: menu をAppNavigationOrderに渡す方法があるのか？
    // ナビゲーションバーの状態を更新
    showNavigation(navigation)
  }


  // ナビゲーションバーよりカテゴリが選択された時、またはメニューがインポートされた時の処理を監視
  function showNavigation(target: NavigationType) {

    isNavigationCategory.value = false
    isNavigationOrder.value = false
    isNavigationHistory.value = false

    if (target === NavigationType.Category) {
      isNavigationCategory.value = true
    } else if (target === NavigationType.Order) {
      isNavigationOrder.value = true
    } else if (target === NavigationType.History) {
      isNavigationHistory.value = true
    }
  }
</script>