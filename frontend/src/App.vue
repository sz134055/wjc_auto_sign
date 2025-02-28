<script setup>
</script>

<template>
  <router-view />
</template>

<style>
html,body{
  margin: 0;
  padding: 0;
  background-color: rgb(11, 12, 16);
  color: #C5C6C7;
}
.global-btn{
  padding: 10px 20px;
  color: #C5C6C7;
  background-color: rgba(11, 12, 16, 0.2);
  border: 1px solid #45A29E;
  border-radius: 5px;
  letter-spacing: 3px;
  transition: all 0.6s ease-in-out; /* 添加过渡属性 */
}

.global-btn:hover{
  background-color: rgba(11, 12, 16, 0.4);
  border-color: #66FCF1;          /* 改变边框颜色 */
  box-shadow: 0 0 10px #66FCF1;   /* 添加发光效果 */
}
.global-title-large {
  font-size: 4em;
  font-weight: 900;
  color: #66FCF1;
}
.global-icon {
  color: #66FCF1;
}
.global-input{
  padding: 10px 10px;
  width: 100%;
  color: #C5C6C7;
  background-color: rgba(11, 12, 16, 0.2);
  border: 1px solid #45A29E;
  border-radius: 10px;
  transition: all 0.6s ease-in-out; /* 添加过渡属性 */
}
.global-btn:hover{
  background-color: rgba(11, 12, 16, 0.4);
  border-color: #66FCF1;          /* 改变边框颜色 */
  box-shadow: 0 0 10px #66FCF1;   /* 添加发光效果 */
}
.global-btn:active {
  transform: scale(0.98);
  transition: all 0.2s ease;
}
.global-btn:focus:not(:active) {
  box-shadow: none;
  border-color: #45A29E;
}
</style>
