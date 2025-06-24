<template>
  <!-- <RecordingDialg v-model="showDialog"/> -->
  <v-card>
    <v-layout>
      <NavigationOrder />
      <NavigationHistory v-model="ishistory" />
      <NavigationMenu v-model="ismenu" />
      <v-main style="height: 100vh;">  
        <Window />
        <BottomNavigation
          @flg_navigation="on_navigation"
        />
      </v-main>
    </v-layout>
  </v-card>
</template>
<script setup lang="ts">

  import { ref } from 'vue'

  const ishistory = ref<boolean>(false)
  const ismenu = ref<boolean>(false)

  // 注文履歴を表示する処理
  const on_navigation = (history: boolean, menu: boolean) => {
    ishistory.value = history
    ismenu.value = menu
  }


</script>