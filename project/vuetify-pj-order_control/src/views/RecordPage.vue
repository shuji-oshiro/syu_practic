<template>
  <v-app class="rounded-md">
    <v-main class="d-flex flex-column justify-center align-center" style="min-height: 70vh;">
      <PlaybackAudio :audioUrl="audioUrl" />
    </v-main>
    <v-slide-y-transition>
      <OrderList :show="showList"/>
    </v-slide-y-transition>
    <v-bottom-navigation>
      <RecordingButton @recorded="handleRecorded"/>
      <v-btn @click="handle_Call_list">
        <v-icon>mdi-history</v-icon>
        <span>注文履歴</span>
      </v-btn>
    </v-bottom-navigation>
  </v-app>
</template>
  
  <script setup lang="ts">
  import { ref } from 'vue'
  import RecordingButton from '@/components/RecordingButton.vue'
  import PlaybackAudio from '@/components/PlaybackAudio.vue'
  import OrderList from '@/components/OrderList.vue'

  const showList = ref<boolean>(true)
  const handle_Call_list = () => {
    showList.value = !showList.value
  }

  const audioUrl = ref<string | null>(null)
  const handleRecorded = (url: string) => {
    if(showList){
      showList.value = false
    }
    audioUrl.value = url
  }
  </script>

<style scoped>
.section {
  margin-bottom: 2rem;
}
</style>
  