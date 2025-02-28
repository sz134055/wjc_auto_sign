<template>
    <div class="cap-box">
        <div class="cap-input-box">
            <input 
                v-for="(_, index) in 6" 
                :key="index"
                ref="inputRefs"
                type="text" 
                class="cap-input-item"
                v-model="codes[index]"
                :style="activeStyle(index)"
                @input="handleInput($event, index)"
                @keydown.delete="handleDelete(index)"
                maxlength="1"
                @paste="handlePaste"
                :disabled="isDisabled"
            >
        </div>
        <div class="tips-box">
            <div class="tips-bar" v-show="isCapPass != null">
                <span class="tips-bar-item tips-bar-item-success" v-if="isCapPass">PASS</span>
                <span class="tips-bar-item tips-bar-item-error" v-else>ERROR</span>
            </div>
            <span>{{ tip }}</span>
        </div>
    </div>
    
</template>

<script setup>
import { ref, watch, nextTick,defineEmits,onMounted } from 'vue'
import userStore from '../store'
import axios from 'axios'
const emit = defineEmits(['complete'])
const codes = ref(Array(6).fill(''))
const inputRefs = ref([])
const activeIndex = ref(0)
const tip = ref('一封包含验证码的邮件已发送至你的邮箱，请填写验证码')
const isCapPass = ref(null)
const isDisabled = ref(false)
const user = userStore()

const handlePaste = (e) => {
    const pasteData = e.clipboardData.getData('text').replace(/\D/g, '')
    codes.value = pasteData.split('').slice(0, 6)
    activeIndex.value = Math.min(pasteData.length, 5)
    nextTick(() => inputRefs.value[activeIndex.value]?.focus())
}
const checkCap =async (cap) => {
    try{
        const response = await axios.post('/emailCheck', {
        account: user.account,
        emailVCode: cap
        }, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
        })

        if(response.data.code ==='ok'){
            isCapPass.value = true
            tip.value = '验证码通过，即将跳转'
            isDisabled.value = true  // 冻结输入
            // 触发父组件事件
            emit('complete')
        }else {
            isCapPass.value = false
            tip.value = '请检查验证码'
            codes.value = Array(6).fill('')
            activeIndex.value = 0
            nextTick(() => {
                inputRefs.value[0].focus()
            })
        }
    }catch (error) {
        console.error('注册请求失败:', error)
        ElMessage.error(error.response?.data?.msg || '网络请求异常')
        isCapPass.value = false
        codes.value = Array(6).fill('')
        activeIndex.value = 0
        nextTick(() => {
            inputRefs.value[0].focus()
        })
    } 
}
// 自动聚焦下一个输入框
const focusNext = (index) => {
    activeIndex.value = Math.min(index + 1, 5)
    nextTick(() => {
        if (activeIndex.value < 6) {
            inputRefs.value[activeIndex.value].focus()
        }
    })
}

// 处理输入
const handleInput = (e, index) => {
    // 过滤非数字输入
    codes.value[index] = e.target.value.replace(/\D/g, '')
    
    // 自动跳转
    if (codes.value[index] && index < 5) {
        focusNext(index)
    }
}

// 处理删除键
const handleDelete = (index) => {
    if (!codes.value[index] && index > 0) {
        activeIndex.value = index - 1
        nextTick(() => {
            inputRefs.value[activeIndex.value].focus()
        })
    }
}

// 输入高亮样式
const activeStyle = (index) => ({
    borderColor: activeIndex.value === index ? '#66FCF1' : '#45A29E'
})

// 监听完整输入
watch(
  () => [...codes.value], // 创建新数组触发响应
  (newVal) => {
    if (newVal.every(code => code !== '')) {
      checkCap(newVal.join(''))
    }
  }
)

onMounted(() => {
    inputRefs.value[0].focus()
})
</script>

<style scoped>
.cap-box{
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 20px;
}
.cap-input-box {
    display: flex;
    gap: 8px;
}

.cap-input-item {
    width: 1em;
    padding: 0.5em;
    font-size: 1.1em;
    border: 2px solid; /* 加粗边框 */
    border-radius: 10px;
    background-color: #C5C6C7;
    text-align: center;
    transition: border-color 0.3s ease;
    outline: none;
}

.cap-input-item:focus {
    background-color: #ffffff;
}
.tips-box{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 10px;

    width: 100%;
}
.tips-bar{
    width: 100%;
}
.tips-bar-item{
    display: inline-block;
    width: 100%;
    text-align: center;
    color: #ffffff;
    font-size: 1.5em;
    letter-spacing: 20px;
    padding: 0.8em 0;
    animation: blink 0.4s ease 1;
}
.tips-bar-item-success {
  background: linear-gradient(45deg, #65ff6a, #86fc00);
}

.tips-bar-item-error {
  background: linear-gradient(45deg, #f74141, #f80132);
}
/* 添加动画关键帧 */
@keyframes blink {
  0% { opacity: 0.3; }
  50% { opacity: 1; }
  100% { opacity: 0.3; }
}
.cap-input-item:disabled {
  background-color: #e0e0e0;
  cursor: not-allowed;
  opacity: 0.7;
}
</style>