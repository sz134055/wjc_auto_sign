<template>
  <div class="main-page">
    <div class="reg-box" v-if="!isEmailPass">
        <el-icon class="global-icon reg-icon"><More /></el-icon>
        <span class="global-title-large">Almost...</span>
        <CapInput @complete="capComplete"/>
    </div>
    <div class="reg-box" v-else>
        <el-icon class="global-icon reg-icon success-color"><CircleCheck /></el-icon>
        <span class="global-title-large">Done !</span>
        <span>恭喜你已完成邮箱验证，现在可添加签到地址</span>
        <span>将会在5秒后自动前往</span>
        <div class="spec-btn-box global-btn" @click="specBtnClick">
            <el-icon><AddLocation /></el-icon>
            <span>前往添加向导</span>
        </div>
    </div>
  </div>
</template>

<script setup>
import { onBeforeMount, ref } from 'vue'
import { CircleCheck,More,Loading,CircleClose,AddLocation } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import CapInput from '../components/CapInput.vue'

const isEmailPass = ref(false)
const router = useRouter()


const specBtnClick = function(){
    router.push('/guide')
}

const capComplete = function(res){
    setTimeout(()=>{
        isEmailPass.value = true
    },1500)
}

onBeforeMount(()=>{
})
</script>

<style scoped>
.main-page{
    width: 100%;
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
}
.reg-icon{
    font-size: 100px;
    font-weight: 700;
}
.reg-box{
    padding: 0 30px;
    height: max-content;
    display: flex;
    flex-direction: column;
    gap: 10px;
    align-items: center;
    justify-content: center;
    text-align: center;
}

.error-color{
    color:red;
}
.success-color{
    color:green;
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
</style>