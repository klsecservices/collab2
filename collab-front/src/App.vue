<template>
  <div>
    <nav>
      <router-link to="/"><span class="material-icons">home</span></router-link>
      <button @click="$router.back()" style="background: none; border: none;"><span class="material-icons">arrow_back</span></button>
    </nav>
    <router-view />
    <NotificationContainer />
  </div>
</template>

<script setup>
import "@/assets/style.css"
import "@/assets/material-icons.css"
import NotificationContainer from "@/components/NotificationContainer.vue"
</script>
