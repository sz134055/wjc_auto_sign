<template>
  <div class="main-page">
    <div class="nav-bar">
      <span class="global-title-large">PROFILE</span>
    </div>
    <div class="main-content">
        <div class="title-bar">
        <el-icon class="global-icon icon-large">
          <WindPower />
        </el-icon>
        <span class="global-title-large">CONSTRUTING</span>
        <span>即将实现：</span>
        <ul>
          <li>显示你已提交的签到信息</li>
          <li>显示签到记录</li>
        </ul>
      </div>
      <div class="func-box">
        <div class="spec-btn-box global-btn" @click="goToGuide">
          <el-icon>
            <AddLocation />
          </el-icon>
          <span>前往添加向导</span>
        </div>
      </div>
    </div>
  </div>
  <FooterBar />
</template>

<script setup>
import { useRouter } from 'vue-router';
import { onMounted } from 'vue';
import FooterBar from '../components/FooterBar.vue';
import { AddLocation, WindPower } from '@element-plus/icons-vue';

const router = useRouter();

const goToGuide = () => {
  router.push('/guide');
}

onMounted(() => {
})
</script>

<style scoped>
.main-page {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.nav-bar{
  width: 100%;
  background-color: #C5C6C7;
  display: flex;
  justify-content: center;
}
.spec-btn-box{
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 5px;
    border-radius: 50px;
    font-size: 1.4em;
    margin-top: 20px;
}
.icon-large{
  font-size: 100px;
}
.title-bar{
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.main-content{
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
</style>