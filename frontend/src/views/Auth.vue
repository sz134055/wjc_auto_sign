<template>
  <div class="main-page">
    <LoadingPage v-show="isLoading" />
    <div class="auth-box" v-show="isReg">
        <div class="global-title-large">注册</div>
        <div class="form-input-item">
            <el-icon class="global-icon"><Message /></el-icon>
            <input class="global-input" type="email" placeholder="输入一个有效的邮箱" v-model="email"/>
        </div>
        <div class="form-input-item">
            <el-icon class="global-icon"><User /></el-icon>
            <input class="global-input" type="text" placeholder="输入校芜优账号" v-model="account"/>
        </div>
        <div class="form-input-item">
            <el-icon class="global-icon"><Lock /></el-icon>
            <input class="global-input" type="password" placeholder="校芜优密码" v-model="pswd"/>
        </div>
        <button class="global-btn" @click="handleRegister">注册</button>
        <a @click="isReg = !isReg">我已有账号</a>
    </div>
    <div class="auth-box" v-show="!isReg">
        <div class="global-title-large">登录</div>
        <div class="form-input-item">
            <el-icon class="global-icon"><Message /></el-icon>
            <input class="global-input" type="text" placeholder="邮箱或校芜优账号" v-model="email"/>
        </div>
        <div class="form-input-item">
            <el-icon class="global-icon"><Lock /></el-icon>
            <input class="global-input" type="password" placeholder="校芜优密码" v-model="pswd"/>
        </div>
        <button class="global-btn" @click="handleLogin">登录</button>
        <a @click="isReg = !isReg">我还没有账号</a>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import LoadingPage from '../components/LoadingPage.vue';
import {User,Message,Lock} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import userStore from '../store'
const isReg = ref(true)
const isLoading = ref(false)
const email = ref()
const pswd = ref()
const account = ref()
const user = userStore()
const handleRegister = async () => {
  // 验证输入
  if (!email.value || !account.value || !pswd.value) {
    ElMessage.error('请填写完整信息')
    return
  }

  try {
    isLoading.value = true
    const response = await axios.post('/checkAccount', {
      email: email.value,
      account: account.value,
      pswd: pswd.value
    }, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    if (response.data.code === 'ok') {
      ElMessage.success('注册成功')
      user.setEmail(email.value)
      user.setAccount(account.value)
      router.push('/result')
    } else {
      ElMessage.error(response.data.msg || '注册失败')
    }
  } catch (error) {
    console.error('注册请求失败:', error)
    ElMessage.error(error.response?.data?.msg || '网络请求异常')
  } finally {
    isLoading.value = false
  }
}

const handleLogin = async () => {
  if (!account.value || !pswd.value) {
    ElMessage.error('请填写完整信息')
    return
  }
  try {
    isLoading.value = true
    const response = await axios.post('/login', {
      account: account.value,
      pswd: pswd.value
    }, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    if (response.data.code === 'ok') {
      ElMessage.success('登录成功')
      user.setEmail(email.value)
      user.setAccount(account.value)
      user.setLoginTime()
      router.push('/profile')
    } else {
      ElMessage.error(response.data.msg || '登录失败')
    }
  } catch (error) {
    console.error('登录请求失败:', error)
    ElMessage.error(error.response?.data?.msg || '网络请求异常')
  } finally {
    isLoading.value = false
  }
}

</script>

<style scoped>
.main-page{
    width: 100%;
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    text-align: center;
}
.auth-box{
    width: 300px;
    min-height: 300px;
    height: fit-content;
    padding: 20px;
    margin-top: 10vh;

    border-radius: 10px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);

    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 20px;

}
.form-input-item{
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    gap:5px;
}
.form-input-item input{
    width: 100%;
}
.flex-1{
    flex: 1;
}
.auth-box button{
    width: 100%;
}
</style>