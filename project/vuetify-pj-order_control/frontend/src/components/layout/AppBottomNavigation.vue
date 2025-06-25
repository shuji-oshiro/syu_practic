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
  
  //注文履歴ボタン押下時
  const on_history = () => {
    store.triggerShowNavigationAction('history', 'AppBottomNavigation')
    //emit('flg_navigation', true, false, false)
  }
  //メニューボタン押下時
  const on_menu = () => {
    store.triggerShowNavigationAction('category', 'AppBottomNavigation')
    //emit('flg_navigation', false, true, false)
  }

</script>
