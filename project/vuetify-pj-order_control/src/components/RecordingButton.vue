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
  (e: 'recorded', url: string): void
}>()

const isRecording = ref(false)
let recorder: MediaRecorder | null = null
let chunks: Blob[] = []

const startRecording = async () => {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
  recorder = new MediaRecorder(stream)
  chunks = []

  recorder.ondataavailable = (e) => chunks.push(e.data)

// 🔧 async に変更
  recorder.onstop = async () => {
    const blob = new Blob(chunks, { type: 'audio/webm' })
    chunks = []

    // 🔧 サーバーへ送信
    const formData = new FormData()
    formData.append('file', blob, 'recording.webm')

    try {
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        console.error('Upload failed:', response.statusText)
        return
      }

      const data = await response.json()
      const mp3Url = `http://localhost:8000${data.url}`

      // 🔧 mp3のURLをemit
      emit('recorded', mp3Url)

    } catch (err) {
      console.error('Fetch error:', err)
    }
  }
  
  // recorder.onstop = () => {
  //   const blob = new Blob(chunks, { type: 'audio/webm' })
    
  //   const url = URL.createObjectURL(blob)
  //   emit('recorded', url)
  // }

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
