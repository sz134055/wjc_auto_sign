<template>
  <a 
    :href="repoUrl" 
    target="_blank" 
    class="repo-btn"
  >
    <div class="logo-circle">
      <img 
        v-if="logo" 
        :src="logo" 
        class="logo-img" 
        alt="Repository Logo"
      >
    </div>
    <div class="text-container">
      <span class="main-text">Github</span>
      <span class="sub-text">View Source</span>
    </div>
  </a>
</template>

<script setup>
import { defineProps } from 'vue'

defineProps({
  repoUrl: {
    type: String,
    default: '#'
  },
  description: {
    type: String,
    default: '项目仓库'
  },
  logo: {
    type: String,
    default: ''
  }
})
</script>

<style scoped>
.repo-btn {
  display: inline-flex;
  align-items: center;
  padding-right: 15px;
  border: 2px solid #66FCF1;
  border-radius: 50px;
  background: transparent;
  text-decoration: none;
  transition: box-shadow 0.3s ease;
}

.repo-btn:hover {
  box-shadow: 0 0 15px #66FCF1;
}

.logo-circle {
  width: 58px;
  height: 58px;
  border: 2px solid #66FCF1;
  border-radius: 50%;
  overflow: hidden; /* 隐藏超出圆框的部分 */
}

.logo-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.text-container {
  padding-left: 8px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.main-text {
  color: #C5C6C7;
  font-size: 14px;
  font-weight: 500;
}

.sub-text {
  color: #66FCF1;
  font-size: 12px;
  opacity: 0.8;
}
</style>