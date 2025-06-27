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
  import { NavigationType } from '@/types/enums'
  import type { MenuOut } from '@/types/menuTypes'
  import { CommonEventStore, UseEventStore } from '@/stores/eventStore'
  const useEventStore = UseEventStore()
  const commonEventStore = CommonEventStore()

  const isNavigationCategory = ref<boolean>(false)
  const isNavigationOrder = ref<boolean>(false)
  const isNavigationHistory = ref<boolean>(false)

  const showAlert = ref(false)
  const title = ref<string>('')
  const message = ref('')
  const icon = ref<'mdi-alert-circle' | 'mdi-information' | 'mdi-check-circle'>()
  const alertType = ref<'success' | 'info' | 'warning' | 'error'>('success')
  // ナビゲーションバーよりカテゴリが選択された時、またはメニューがインポートされた時の処理を監視
  watch(
    () => [commonEventStore.lastError.timestamp, commonEventStore.lastInfo.timestamp, commonEventStore.lastWarning.timestamp],
    () => {
      showAlert.value = true
      title.value = commonEventStore.lastError.message
      message.value = commonEventStore.lastError.detail

      if (commonEventStore.lastError.message) {
        icon.value = 'mdi-alert-circle'
        alertType.value = 'error' // エラータイプ
      } else if (commonEventStore.lastWarning.message) {
        icon.value = 'mdi-alert-circle'
        alertType.value = 'warning' // 警告タイプ
      } else if (commonEventStore.lastInfo.message) {
        icon.value = 'mdi-information'
        alertType.value = 'info' // 情報タイプ
      }
    }
  )

  function selectMenu(menu: MenuOut, navigation: NavigationType) {
    // メニューが選択されたことを通知
    useEventStore.triggerMenuSelectAction(menu)
    // ナビゲーションの状態を更新
    showNavigation(NavigationType.Order)
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