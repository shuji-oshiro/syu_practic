<script setup lang="ts">
    //
  import { ref } from 'vue'
  
  // ダミー注文データ（仮）
  const orders = Array.from({ length: 10 }, (_, i) => `注文 ${i + 1}`)
   
  const showToolbar = ref(true)

  // トグル関数
  const toggleToolbar = () => {
    showToolbar.value = !showToolbar.value
  }

  const downloadAudio = (blob: Blob) => {
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'recorded-audio.webm'  // ファイル名
    a.click()
    URL.revokeObjectURL(url)  // メモリ開放
  }

    
  // audioタグの参照
  const audioPlayer = ref<HTMLAudioElement | null>(null)
  
  // MediaRecorderと録音関連変数
  let recorder: MediaRecorder | null = null
  let mimeType = ''
  let chunks: Blob[] = []
  
  const errorMessage = ref('') 
  const isRecording = ref(false)
  const audioKey = ref(0)

  const initMicrophone = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })

      // MediaRecorderサポートチェック
      if (typeof MediaRecorder === 'undefined') {
        throw new Error('このブラウザは MediaRecorder をサポートしていません。')
      }

      recorder = new MediaRecorder(stream)

      recorder.ondataavailable = (e) => {
        mimeType = e.data.type
        chunks.push(e.data)
      }

      recorder.onstop = () => {
        const blob = new Blob(chunks, { type: mimeType })
        chunks = []
        downloadAudio(blob)
        const audioURL = URL.createObjectURL(blob)

        if (audioPlayer.value) {
          audioPlayer.value.pause()
          audioPlayer.value.src = ''
          audioPlayer.value.load() // ← 明示的に初期化
          audioPlayer.value.src = audioURL
          audioPlayer.value.load() // ← 再読み込み（重要）
        } else {
          console.warn('audioPlayer is not ready')
        }
      }
      errorMessage.value = '' // 成功したのでエラーをクリア
    } catch (err: any) {
      errorMessage.value = `マイクの使用に失敗しました: ${err.message || err.name}`
      console.error('getUserMedia error:', err)
    }
  }


  const startRecording = async () => {
  if (!recorder) await initMicrophone()
  if (recorder && recorder.state === 'inactive') {
    isRecording.value = true
    recorder.start()
  }
}

const stopRecording = () => {
  if (recorder && recorder.state === 'recording') {
    isRecording.value = false
    recorder.stop()
  }
}

</script>

<template>

  <v-app class="rounded rounded-md">

    <!-- メイン中央配置 -->
    <v-main
  class="d-flex flex-column justify-center align-center"
  style="min-height: 70vh;"
>
  <!-- カード -->
  <v-card class="mb-4">
    <v-card-title class="text-h6">メインコンテンツ</v-card-title>
    <v-card-text>横メニューは上部に表示／非表示できます</v-card-text>
  </v-card>

<!-- 音声プレイヤー -->
<article class="clip mb-4">
  <audio :key="audioKey" ref="audioPlayer" controls />
</article>

    <!-- エラー表示 -->
    <v-alert
      v-if="errorMessage"
      type="error"
      class="ma-4"
      border="start"
      colored-border
    >
      {{ errorMessage }}
    </v-alert>
  </v-main>


    
    <!-- 横メニュー（フルスクリーン風にスライド） -->
    <v-slide-y-transition>
    <v-sheet
      v-if="showToolbar"
      color="primary"
      style="position: absolute; top: 0; left: 0; right: 0; bottom: 56px; z-index: 10;"
      class="pa-4 d-flex flex-column"
      dark
    >
      <!-- ラベル -->
      <div class="text-h6 mb-4">ご注文メニュー</div>

      <!-- スクロール可能なリスト -->
      <v-sheet
        color="grey darken-3"
        elevation="2"
        class="flex-grow-1 overflow-y-auto mb-4 rounded"
      >
        <v-list density="compact">
          <v-list-item
            v-for="(order, index) in orders"
            :key="index"
            :title="order"
            prepend-icon="mdi-food"
          />
        </v-list>
      </v-sheet>

      <!-- 閉じるボタン -->
      <v-btn icon @click="showToolbar = false" class="ml-auto">
        <v-icon>mdi-close</v-icon>
      </v-btn>
    </v-sheet>
  </v-slide-y-transition>


  <!-- 下段ナビゲーション -->
  <v-bottom-navigation>      
      <v-btn v-if="!isRecording" @click="startRecording">
        <v-icon>mdi-record-rec</v-icon>
        <span>注文</span>
      </v-btn>
      <v-btn v-else @click="stopRecording">
        <v-icon>mdi-microphone</v-icon>
        <span>停止</span>
      </v-btn>      

      <v-btn value="stop" @click="toggleToolbar">
        <v-icon>mdi-history</v-icon>
        <span>注文履歴</span>
      </v-btn>
    </v-bottom-navigation>
  </v-app>
</template>

<style scoped></style>

