<template>
    <div class="main-page">
        <div class="title-box">
            <el-icon class="global-icon guide-icon"><LocationInformation /></el-icon>
            <span class="global-title-large">设置签到位置</span>
        </div>
        <div class="coordinates-box">
            <div class="setter-input">
                <div class="setter-input-item">
                    <span>位置</span>
                    <input 
                        class="global-input" 
                        type="text"
                        step="any"
                        placeholder="位置名"
                        v-model="currentName"
                    >
                </div>
                <div class="setter-input-item">
                    <span>经度</span>
                    <input 
                        class="global-input" 
                        type="number"
                        step="any"
                        placeholder="经度"
                        v-model.number="currentLng"
                    >
                </div>
                <div class="setter-input-item">
                    <span>纬度</span>
                    <input 
                        class="global-input" 
                        type="number"
                        step="any"
                        placeholder="纬度"
                        v-model.number="currentLat"
                    >
                </div>
            </div>
            <div class="btn-box">
                <button class="global-btn" @click="goToSchool">定位到学校</button>
                <button class="global-btn" @click="confirmCoordinates">确认位置</button>
            </div>
            <span>如需重新定位到你当前位置请刷新页面</span>
        </div>

        <MapContainer 
            class="map-box" 
            ref="mapRef" 
            @coordinates-update="handleCoordinatesUpdate"
        />
       <FooterBar />
    </div>
</template>

<script setup>
import { LocationInformation } from '@element-plus/icons-vue'
import MapContainer from '../components/MapContainer.vue';
import FooterBar from '../components/FooterBar.vue';
import { ref, watch } from 'vue'
import axios from 'axios';
import userStore from '../store';
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'


// 坐标数据
const currentLng = ref(null)
const currentLat = ref(null)
const currentName = ref(null)
const mapRef = ref()
const user = userStore()
const router = useRouter()

const goToSchool = () => {
  mapRef.value?.updateCoordinates(118.265303, 31.359218)
}

// 处理坐标更新事件
const handleCoordinatesUpdate = ({ lng, lat, name }) => {
  currentLng.value = lng
  currentLat.value = lat
  currentName.value = name
}

// 坐标验证方法
const validateCoordinate = (value) => {
  return typeof value === 'number' && 
         value >= -180 && value <= 180 &&
         !isNaN(value)
}

// 输入框变化监听
watch([currentLng, currentLat], ([newLng, newLat]) => {
  if (validateCoordinate(newLng) && validateCoordinate(newLat)) {
    mapRef.value?.updateCoordinates(newLng, newLat)
  }
})

// 确认坐标提交
const confirmCoordinates = async() => {
  const { lng, lat,name } = mapRef.value.getCurrentCoordinates()
  
  if (!validateCoordinate(lng) || !validateCoordinate(lat)) {
    alert('请先在地图上选择有效位置')
    return
  }
  
  try {
    const response = await axios.post(
        '/submit',
        {
            account:user.getAccount,
            coordinate: `${lng},${lat}`,
            position: name
        },{
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        }
    )

    if (response.data.code === 'ok') {
        ElMessage.success('设置位置成功！')
        setTimeout(()=>{
            router.push('/profile')
        },2000)
        
    } else {
        ElMessage.error(response.data.msg || '设置位置失败')
    }
  }catch (error) {
    console.error('设置位置请求失败:', error)
    ElMessage.error(error.response?.data?.msg || '网络请求异常')
  }
}
</script>

<style scoped>
.main-page {
    width: 100%;
    height: 100vh;
    padding-top: 50px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 20px;
}

.map-box {
    min-height: 400px;
    width: 90%;
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}

.title-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    text-align: center;
}
.guide-icon {
    font-size: 100px;
    color: #409EFF;
    transition: color 0.3s ease;
}

.setter-input {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: center;
    flex-wrap: wrap;
    gap: 10px;
}
.coordinates-box {
    display: flex;
    flex-direction: row;
    width: 100%;
    gap:10px;
    flex-wrap: wrap;
    justify-content: center;
    align-items: center;
}

.setter-input-item {
    display: flex;
    align-items: center;
    gap: 10px;
    flex: 1;
}

.setter-input-item span {
    min-width: 50px;
    text-align: right;
    font-weight: 500;
}
.setter-input-item input{
    min-width: 130px;
}
.btn-box{
    display: flex;
    width: 100%;
    justify-content: center;
    align-items: center;
    gap: 20px;
}

</style>