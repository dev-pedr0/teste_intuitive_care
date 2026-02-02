<script setup lang="ts">
import AppFooter from './components/AppFooter.vue';
import AppHeader from './components/AppHeader.vue';

</script>

<template>
  <div class="container">
    <AppHeader />
    <router-view />
    <AppFooter />
  </div>
</template>

<style scoped></style>
