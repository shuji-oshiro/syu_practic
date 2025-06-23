<template>
  <v-btn @click="toggleRecording">
    <v-icon>
      {{ isRecording ? 'mdi-record-rec' : 'mdi-microphone' }}
    </v-icon>
    <span>
      {{ isRecording ? '停止' : '注文' }}
    </span>
  </v-btn>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const emit = defineEmits<{
  (e: 'recorded', reco_text: string, match_text:string, blob:Blob): void
  (e: 'error', message: string): void  // ← エラー用emit追加
}>()

const isRecording = ref(false)
let recorder: MediaRecorder | null = null
let chunks: Blob[] = []

const startRecording = async () => {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
  recorder = new MediaRecorder(stream)
  chunks = []

  recorder.ondataavailable = (e) => chunks.push(e.data)

  recorder.onstop = async () => {
    const blob = new Blob(chunks, { type: 'audio/webm' })
    chunks = []

    // サーバーへ送信
    const formData = new FormData()
    formData.append('file', blob, 'recording.webm')

    try {
      const response = await fetch('http://localhost:8000/voice', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json();
        emit('error', errorData.detail || 'サーバーエラー')
        return;
      }

      const data = await response.json()

      const reco_text = data.reco_text
      const match_text = data.match_text
      emit('recorded', reco_text, match_text, blob)

    } catch (err) {
      emit('error', '通信エラーが発生しました')
    }
  }

  recorder.start()
  isRecording.value = true
}

const stopRecording = () => {
  if (recorder?.state === 'recording') {
    recorder.stop()
    isRecording.value = false
  }
}

const toggleRecording = () => {
  isRecording.value ? stopRecording() : startRecording()
}
</script>
