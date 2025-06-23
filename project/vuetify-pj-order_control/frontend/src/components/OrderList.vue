<!-- components/OrderMenu.vue -->
<template>
  <v-sheet
    v-if="show"
    color="primary"
    class="pa-4 d-flex flex-column"
    dark
    style="position: absolute; top: 0; left: 0; right: 0; bottom: 56px; z-index: 10;"
  >
    <div class="text-h6 mb-4">ご注文履歴</div>

    <v-sheet color="grey darken-3" elevation="2" class="flex-grow-1 overflow-y-auto mb-4 rounded">
      <v-list density="compact">
        <v-list-item
          v-for="(order, index) in orders"
          :key="index"
          :title="order"
          prepend-icon="mdi-food"
        />
      </v-list>
    </v-sheet>

    <!-- <v-btn icon @click="show = false" class="ml-auto">
      <v-icon>mdi-close</v-icon>
    </v-btn> -->
  </v-sheet>
</template>

<script setup lang="ts">
import { ref } from 'vue'
defineProps<{ show: boolean }>()

// ダミー注文データ
const orders = ref<string[]>(Array.from({ length: 10 }, (_, i) => `注文 ${i + 1}`))
</script>
