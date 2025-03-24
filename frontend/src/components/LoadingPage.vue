<template>
  <div class="loading-box">
    <el-icon class="global-icon loading-icon animate-rotate"><Loading /></el-icon>
    <span class="animate-pulse">Loading...</span>
  </div>
  
</template>

<script setup>
import { Loading } from '@element-plus/icons-vue';
</script>

<style scoped>
.loading-box{
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap:20px;
}
.loading-icon{
  font-size: 100px;
  font-weight: 700;
}
.animate-rotate {
  animation: rotate 2s linear infinite;
}
@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>