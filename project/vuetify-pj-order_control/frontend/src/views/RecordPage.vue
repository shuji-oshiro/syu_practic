<template>
  <v-app class="rounded-md">
    <v-main class="d-flex flex-column justify-center align-center" style="min-height: 70vh;">
      <!-- <PlaybackAudio :audioUrl="audioUrl" /> -->
      <!-- <p v-if="audioUrl">音声URL: {{ audioUrl }}</p> -->
      <p>音声認識: {{ reco_text }}</p>
      <p>マッチングメニュー: {{ match_text }}</p>
      <p>サイズ: {{ audioSize }} KB</p>
      <v-alert v-if="errorMessage" type="error" class="ma-4">
        {{ errorMessage }}
      </v-alert>
    </v-main>
    <v-slide-y-transition>
      <OrderList :show="showList"/>
    </v-slide-y-transition>
    <v-bottom-navigation>
      <RecordingButton 
      @recorded="handleRecorded"
      @error="errorMessage = $event"
      />
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

  const reco_text = ref<string | null>(null)
  const match_text = ref<string | null>(null)
  const audioSize = ref<string | null>(null)
  const errorMessage = ref<string | null>(null)

  const handleRecorded = (reco: string, match:string, blob: Blob) => {
    if(showList){
      showList.value = false
    }
    reco_text.value = reco
    match_text.value= match
    audioSize.value = (blob.size / 1024).toFixed(2)
    errorMessage.value = null
  }
  </script>

<style scoped>
.section {
  margin-bottom: 2rem;
}
</style>
  