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
      <OrderList :show="is_orderList"/>
    </v-slide-y-transition>
    <v-slide-y-transition>
      <MenuList :show="is_MenuList"/>
    </v-slide-y-transition>
    <v-bottom-navigation>
      <RecordingButton 
      @recorded="on_Recorded"
      @error="errorMessage = $event"
      />
      <v-btn @click="setView_orderList">
        <v-icon>mdi-history</v-icon>
        <span>注文履歴</span>
      </v-btn>
      <v-btn @click="setView_MenuList">
        <v-icon>mdi-silverware</v-icon>
        <span>メニュー</span>
      </v-btn>
    </v-bottom-navigation>
  </v-app>
</template>
  
  <script setup lang="ts">
  import { ref } from 'vue'
  import RecordingButton from '@/components/RecordingButton.vue'
  import PlaybackAudio from '@/components/PlaybackAudio.vue'
  import OrderList from '@/components/OrderList.vue'
  import MenuList from '@/components/MenuList.vue'

  const is_orderList = ref<boolean>(true)
  const setView_orderList = () => {
    is_orderList.value = !is_orderList.value
  }

  const is_MenuList = ref<boolean>(false)
  const setView_MenuList = () => {
    is_MenuList.value = !is_MenuList.value
  }


  const reco_text = ref<string | null>(null)
  const match_text = ref<string | null>(null)
  const audioSize = ref<string | null>(null)
  const errorMessage = ref<string | null>(null)

  const on_Recorded = (reco: string, match:string, blob: Blob) => {
    is_orderList.value = false
    is_MenuList.value = false

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
  