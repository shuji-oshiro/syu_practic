<template>
  <v-bottom-navigation>
    <v-btn @click="on_history">
    <v-icon>mdi-history</v-icon>
    <span>注文履歴</span>
    </v-btn>
    <v-btn @click="on_menu">
    <v-icon>mdi-silverware</v-icon>
    <span>メニュー</span>
    </v-btn>
    <RecordingButton />
    <ImportCSVBtn />
  </v-bottom-navigation>
</template>
<script setup lang="ts">
  import { ja } from 'vuetify/locale';
  import { useEventStore } from '@/stores/eventStore'
  
  const store = useEventStore()
  // const emit = defineEmits<{
  //     (e: 'flg_navigation', flg_history: boolean, flg_menu:boolean, flg_recording:boolean): void
  //     (e: 'error', message: string): void
  // }>()

  const on_history = () => {
    store.triggerShowNavigationAction('history', 'AppBottomNavigation')
    //emit('flg_navigation', true, false, false)
  }
  const on_menu = () => {
    store.triggerShowNavigationAction('category', 'AppBottomNavigation')
    //emit('flg_navigation', false, true, false)
  }

</script>
