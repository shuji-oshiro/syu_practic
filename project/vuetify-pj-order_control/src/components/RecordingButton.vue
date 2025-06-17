<template>
  <v-btn @click="toggleRecording">
    <v-icon>
      {{ isRecording ? 'mdi-record-rec' : 'mdi-microphone' }}
    </v-icon>
    <span>
      {{ isRecording ? '停止' : '注文' }}
    </span>
  </v-btn>

  <!-- <button @click="toggleRecording">
    {{ isRecording ? '⏹️ 停止' : '🎙️ 録音' }}
  </button> -->
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
  recorder.onstop = () => {
    const blob = new Blob(chunks, { type: 'audio/webm' })
    const url = URL.createObjectURL(blob)
    emit('recorded', url)
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
