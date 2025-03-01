<template>
  <div class="main-page">
    <div class="fade-overlay"></div>
    <div class="title-box">
      <div class="title-content">
        <div class="title-large-box">
          <span class="global-title-large">Auto</span>
          <span class="global-title-large">Check-In</span>
        </div>
        <span>高效、全自动的UWH在线签到打卡服务</span>
        <button class="global-btn" @click="authBtn">注册或登录</button>
        <!-- <span>当前运行状态：正常</span> -->
      </div>
      <span class="scroll-tip">向下滑动查看更多说明</span>
    </div>
    <div class="introduction-box">
      <span class="global-title-large">说明</span>
      <div class="introductions">
        <div class="introduction-card">
          <span>这是一个基于逆向官方API实现的签到脚本</span>
          <ul>
            <li>优化流程自动执行签到操作</li>
            <li>绕过冗余步骤提升执行效率</li>
            <li>特殊网络情况下仍保持较高成功率</li>
          </ul>
        </div>
        <div class="introduction-card">
          <span>你需要</span>
          <ul>
            <li>使用有效邮箱和校芜优账号进行注册</li>
            <li>设置签到位置信息</li>
            <li>定期查收签到状态邮件</li>
          </ul>
        </div>
        <div class="introduction-card">
          <span>额外说明</span>
          <ul>
            <li>将会明文存储你的密码,不要使用常用密码</li>
            <li>时刻关注你的签到状态</li>
            <li>推荐自搭建脚本使用保障账户安全</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
  <FooterBar />
</template>

<script setup>
import { useRouter } from 'vue-router';
import FooterBar from '../components/FooterBar.vue';

const router = useRouter();
const authBtn = () => {
  router.push('/auth');
}
</script>

<style scoped>
.main-page {
  width: 100%;
  height: fit-content;


  display: flex;
  flex-direction: column;
  justify-content: center;
}

.title-box {
  position: relative; /* 为绝对定位子元素提供基准 */
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #1F2833;
}

.title-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.scroll-tip {
  position: absolute;
  bottom: 20px;
  animation: float 2s ease-in-out infinite;
  opacity: 0.8;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.title-large-box {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
  gap:10px;
}

.introduction-box {
  display: flex;
  flex-direction: column;
  justify-content:flex-start;
  align-items: center;
  padding-top: 50px;
  padding-bottom: 50px;
  gap: 30px;
}

.introductions {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.introduction-card {
  display: flex;
  flex-direction: column;
  justify-content: center;
  max-width: 400px;
}
.introduction-card span{
  padding-left: 20px;
}

.fade-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #1F2833; /* 与背景色一致 */
  animation: fadeInFromDark 1s ease-in forwards;
  z-index: 999;
}

@keyframes fadeInFromDark {
  from {
    opacity: 1;
  }
  to {
    opacity: 0;
    visibility: hidden;
  }
}
</style>