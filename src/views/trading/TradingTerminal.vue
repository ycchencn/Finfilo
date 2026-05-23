<script setup>
import {ref, onMounted, onUnmounted} from 'vue'
import WatchlistPanel from '@/components/trading/WatchlistPanel.vue'
import ChartArea from '@/components/trading/ChartArea.vue'
import StatusBar from '@/components/trading/StatusBar.vue'
import router from "@/router";

const selectedSymbol = ref(null)
const currentSymbol = ref(selectedSymbol.value)
const refreshing = ref(false)

function handleSymbolChange(symbol) {
    console.log(symbol)
    selectedSymbol.value = symbol
    currentSymbol.value = symbol
    simulateDataRefresh()
}

function simulateDataRefresh() {
    refreshing.value = true
    setTimeout(() => {
        refreshing.value = false
        // 此处可触发 WebSocket 重连或 API 请求
    }, 600)
}

// 量化终端快捷键：Ctrl+R 刷新 / Esc 退出
function handleKeyDown(e) {
    if (e.key === 'Escape') {
        history.back() // 或触发全局 store 关闭全屏模式
    }
    if (e.ctrlKey && e.key.toLowerCase() === 'r') {
        e.preventDefault()
        simulateDataRefresh()
    }
}

const toggleHome = () => {
    router.push({path: '/market/cn_market_overview'});
};

onMounted(() => {
    window.addEventListener('keydown', handleKeyDown)
})
onUnmounted(() => {
    window.removeEventListener('keydown', handleKeyDown)
    // ⚠️ 必须在此处销毁图表实例 & 清理 WebSocket，防止内存泄漏
})
</script>

<template>

    <section class="flex flex-col h-full w-full bg-neutral-950 text-white overflow-hidden select-none h-100vh">
        <!-- 顶部工具栏 -->
        <header
            class="h-10 px-4 border-b border-gray-800 flex items-center justify-between shrink-0 bg-neutral-900/60 backdrop-blur-sm">
            <div class="flex items-center gap-3 text-sm font-medium">
                <span class="text-blue-400">⚡ QuantTrade</span>
                <span class="text-gray-600">|</span>
                <span class="text-gray-300">{{ currentSymbol }}</span>
                <span
                    class="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px] border border-emerald-500/20 flex items-center gap-1">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span> LIVE
        </span>
            </div>
            <div class="flex items-center gap-2">
                <Button size="small" variant="text" icon="pi pi-sync" @click="simulateDataRefresh" :loading="refreshing"/>
                <Button size="small" variant="text" icon="pi pi-cog"/>
                <Button size="small" variant="text" icon="pi pi-home" @click="toggleHome()"/>
            </div>
        </header>
        <!-- 主网格区域：h-full 占满剩余高度 -->
        <main class="flex-1 flex flex-col md:flex-row overflow-hidden">
            <WatchlistPanel @update:symbol="handleSymbolChange" :selected-symbol="selectedSymbol" />
            <ChartArea :symbol="selectedSymbol" v-if="selectedSymbol"/>
        </main>
        <!-- 底部状态栏 -->
        <StatusBar/>
    </section>
</template>

<style scoped>
/* 终端专属滚动条样式 */
::v-deep(*::-webkit-scrollbar) {
    width: 5px;
    height: 5px;
}

::v-deep(*::-webkit-scrollbar-track) {
    background: transparent;
}

::v-deep(*::-webkit-scrollbar-thumb) {
    background: #4b5563;
    border-radius: 3px;
}

::v-deep(*::-webkit-scrollbar-thumb:hover) {
    background: #6b7280;
}
</style>