<!-- src/components/VoiceRecorder.vue -->
<template>
  <div>
    <button @click="recording ? stopRecording() : startRecording()">
      {{ recording ? '停止' : '録音開始' }}
    </button>
    <button @click="sendAudio" :disabled="!audioBlob">音声送信</button>
    <p v-if="transcript">📝 {{ transcript }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'

const recording = ref(false)
const mediaRecorder = ref<MediaRecorder | null>(null)
const audioBlob = ref<Blob | null>(null)
const transcript = ref('')

const startRecording = async () => {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
  const recorder = new MediaRecorder(stream)
  const chunks: Blob[] = []

  recorder.ondataavailable = e => chunks.push(e.data)
  recorder.onstop = () => {
    audioBlob.value = new Blob(chunks, { type: 'audio/webm' })
  }

  recorder.start()
  mediaRecorder.value = recorder
  recording.value = true
}

const stopRecording = () => {
  mediaRecorder.value?.stop()
  recording.value = false
}

const sendAudio = async () => {
  if (!audioBlob.value) return

  const formData = new FormData()
  formData.append('file', audioBlob.value, 'voice.webm')

  const res = await axios.post('http://localhost:8000/voice', formData)
  transcript.value = res.data.text
}
</script>
