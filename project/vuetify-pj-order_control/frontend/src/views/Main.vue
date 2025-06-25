<template>
  <!-- <RecordingDialg v-model="showDialog"/> -->
  <v-card>
    <v-layout>
      <AppNavigation />
      <v-main style="height: 100vh;" >  
        <MenuWindow />
        <AppBottomNavigation />
      </v-main>
    </v-layout>
  </v-card>
</template>
<script setup lang="ts">
  import { ref } from 'vue'

</script>