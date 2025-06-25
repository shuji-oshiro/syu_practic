<template>
  <div style="max-height: 90vh; overflow-y: auto; overflow-x: hidden;">
    <v-row dense>
      <v-col
        v-for="(variant, i) in variants"
        :key="i"
        cols="12"
        md="4"
        >  
      <v-card
          :variant="variant"
          class="mx-auto"
          color="surface-variant"
          max-width="344px"
          subtitle="Greyhound divisely hello coldly wonderfully"
          title="Headline">
      <v-img
          height="300px"
          src="https://cdn.vuetifyjs.com/images/cards/sunshine.jpg"
          cover
      ></v-img>
          <template v-slot:actions >
            <v-btn text="注文"></v-btn>
          </template>
      </v-card>
      <div class="text-center text-caption">{{ variant }}</div>
      </v-col>
    </v-row>
  </div>
</template>
<script setup>
  const variants = ['elevated', 'flat', 'tonal', 'outlined', 'text', 'plain']
</script>