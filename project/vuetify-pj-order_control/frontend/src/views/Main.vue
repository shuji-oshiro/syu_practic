<template>
  <!-- <RecordingDialg v-model="showDialog"/> -->
  <v-card>
    <v-layout>
      <NavigationOrder />
      <NavigationHistory />
      <NavigationMenu />
      <v-main style="height: 100vh;">  
        <Window />
        <BottomNavigation />
      </v-main>
    </v-layout>
  </v-card>
</template>
<script setup lang="ts">
  import { ref } from 'vue'

</script>