<!-- MapContainer.vue -->
<template>
    <LoadingPage v-show="isLoading" />
    <div id="map-container" v-show="!isLoading" :class="{ 'pointer-events-none': !isLocated }">
        <div v-if="!isLocated" class="map-overlay"></div>
    </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref, defineEmits, watch } from 'vue'
import AMapLoader from '@amap/amap-jsapi-loader'
import LoadingPage from './LoadingPage.vue'

const isLoading = ref(true)
const emit = defineEmits(['coordinates-update'])
const map = ref(null)
const currentLng = ref(null)
const currentLat = ref(null)
const currentName = ref(null)
const activeMarker = ref(null)
// 添加地理编码器引用
const geocoder = ref(null)
// 增加定位完成状态
const isLocated = ref(false)


const getAMapInfo = () => ({
    key: "980b929874b97995c3f388dd513df211",
    code: "8cd4e18a2645a9f6dc890f7f7eeae83e",
    longitude: 118.265303,
    latitude: 31.359218
})

// 添加地址解析方法
const getLocationName = async (lnglat) => {
    return new Promise((resolve, _) => {
        geocoder.value.getAddress(lnglat, (status, result) => {
            if (status === 'complete' && result.regeocode) {
                resolve(result.regeocode.formattedAddress)
            } else {
                resolve('未知位置')
            }
        })
    })
}



// 暴露坐标获取方法
const getCurrentCoordinates = () => ({
    lng: currentLng.value,
    lat: currentLat.value,
    name: currentName.value
})

// 更新坐标并触发事件
const updateCoordinates = async (lng, lat, name = "") => {
    const formattedLng = Number(lng.toFixed(6))
    const formattedLat = Number(lat.toFixed(6))

    currentLng.value = formattedLng
    currentLat.value = formattedLat

    // 确保名称获取的异常处理
    try {
        const locationName = name || await getLocationName([formattedLng, formattedLat])
        emit('coordinates-update', {
            lng: formattedLng,
            lat: formattedLat,
            name: locationName
        })
    } catch (e) {
        console.error('地址解析失败:', e)
        emit('coordinates-update', {
            lng: formattedLng,
            lat: formattedLat,
            name: '位置解析失败'
        })
    }
}

// 更新地图标记
const updateMarker = (position, title = '签到位置') => {
    if (activeMarker.value) {
        activeMarker.value.setMap(null)
    }
    activeMarker.value = new AMap.Marker({
        position: position,
        title: title,
        icon: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_b.png'
    })
    activeMarker.value.setMap(map.value)
}

// 初始化地图事件
const initMapEvents = (AMap) => {
    // 地图点击事件
    map.value.on('click', (e) => {
        const pos = [e.lnglat.getLng(), e.lnglat.getLat()]
        updateCoordinates(...pos)
        updateMarker(pos)
    })

    // 设备定位处理
    const geolocation = new AMap.Geolocation({
        enableHighAccuracy: true,
        timeout: 10000
    })

    geolocation.getCurrentPosition(
        (status, result) => {
            const success = status === 'complete'
            const pos = success ?
                [result.position.getLng(), result.position.getLat()] :
                [getAMapInfo().longitude, getAMapInfo().latitude]

            updateCoordinates(...pos)
            updateMarker(pos, success ? '当前位置' : '默认位置')
            map.value.setCenter(pos)

            // 定位完成后关闭加载状态
            isLoading.value = false
            isLocated.value = true
        },
        (error) => {
            console.error('定位失败:', error)
            // 失败时使用默认位置
            const pos = [getAMapInfo().longitude, getAMapInfo().latitude]
            updateCoordinates(...pos)
            updateMarker(pos, '默认位置')
            map.value.setCenter(pos)

            // 依然关闭加载状态
            isLoading.value = false
            isLocated.value = true
        }
    )
}

// 监听坐标变化（来自父组件）
watch([currentLng, currentLat], ([newLng, newLat]) => {
    if (newLng && newLat && map.value) {
        const newPos = [Number(newLng), Number(newLat)]
        if (!isNaN(newPos[0]) && !isNaN(newPos[1])) {
            updateMarker(newPos, '指定位置')
            map.value.setCenter(newPos)
        }
    }
})

onMounted(() => {
    const AMapInfo = getAMapInfo()
    window._AMapSecurityConfig = { securityJsCode: AMapInfo.code }

    AMapLoader.load({
        key: AMapInfo.key,
        version: "2.0",
        plugins: ["AMap.Scale", "AMap.Geolocation", "AMap.Geocoder"]
    }).then((AMap) => {
        // 先创建地图实例
        map.value = new AMap.Map('map-container', {
            viewMode: "3D",
            zoom: 15,
            center: [AMapInfo.longitude, AMapInfo.latitude]
        })

        // 再初始化其他组件
        geocoder.value = new AMap.Geocoder()
        initMapEvents(AMap)

        // 添加地图加载完成事件
        map.value.on('complete', () => {
            console.log('地图加载完成')
        })
    }).catch(error => {
        console.error('地图初始化失败:', error)
    }).finally(() => {
        isLoading.value = false
    })
})

onUnmounted(() => {
    if (map.value) {
        map.value.destroy()
        map.value = null
    }
})

defineExpose({
    getCurrentCoordinates,
    updateCoordinates
})
</script>

<style scoped>
#map-container {
    padding: 0px;
    margin: 0px;
    width: 100%;
    min-height: 400px;
    position: relative;
}

.amap-marker {
    animation: marker-appear 0.3s ease;
}

@keyframes marker-appear {
    from {
        transform: scale(0);
    }

    to {
        transform: scale(1);
    }
}

.map-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(255, 255, 255, 0.8);
    z-index: 999;
}

.pointer-events-none {
    pointer-events: none;
}
</style>