<!-- src/components/menu/OrijinalCard.vue -->
<template>
  <v-card
    elevated
    class="mx-auto"
    color="surface-variant"
    max-width="344px"
  >
    <!-- スロットでタイトル部分を外部から変更可能 -->
    <template #title>
      <slot name="menu-title">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>{{ menu.name }}</span>
          <span style="font-weight: bold;">¥{{ menu.price }}</span>
        </div>
      </slot>
    </template>

    <v-img
      height="300px"
      src="https://cdn.vuetifyjs.com/images/cards/sunshine.jpg"
      cover
    />

    <template #actions>
      <slot name="menu-action">
        <v-btn text="注文" @click="onClick" width="100%"></v-btn>
      </slot>
    </template>
  </v-card>
</template>

<script setup lang="ts">
defineProps<{
  menu: any
  onClick: () => void
}>()
</script>
