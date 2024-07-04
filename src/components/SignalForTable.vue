<template>
    <div class="signal-container-for-table" :class="color ? 'greenBackground' : 'redBackground'">
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  
  const props = defineProps({
    color: {
      type: Boolean,
      required: true
    }
  })
  
  // No changes needed in the script setup section for this functionality
  </script>
  
  <style scoped>
  .signal-container-for-table{
    border: 1px solid black;
    width:15px;
    height:10px;
  }
  .greenBackground{
    background-color: green;
  }
  .redBackground{
    background-color: red;
  }
  </style>
  