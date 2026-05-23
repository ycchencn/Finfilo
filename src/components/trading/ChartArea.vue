<script setup lang="ts">
import {ref, watch, onMounted, onUnmounted, nextTick} from 'vue'
import {createChartConfig} from '@/utils/constants.js'
import {fetchStockMarketData, fetchStockInfo} from '@/utils/function.js'
import {init} from 'klinecharts'

const props = defineProps<{ symbol: string }>()
const stock_info = ref({name: '', concepts: ''})

const PERIODS = [
    {id: 'day', containerId: 'chart-day', type: 'day', span: 1},
    {id: 'week', containerId: 'chart-week', type: 'week', span: 1},
    {id: 'month', containerId: 'chart-month', type: 'month', span: 1},
] as const

const chartInstances = ref<Record<string, any>>({})
const dataCache = ref<Record<string, any[]>>({})
let isRebuilding = false

// 独立初始化单周期图表
const initPeriodChart = async (cfg: typeof PERIODS[number]) => {
    // ✅ 数据获取恢复：若无缓存则拉取
    if (!dataCache.value[cfg.id]) {
        dataCache.value[cfg.id] = await fetchStockMarketData(props.symbol)
    }

    await nextTick()
    const el = document.getElementById(cfg.containerId)
    if (!el) return

    let chart = chartInstances.value[cfg.id]

    // 如果实例存在且未销毁，且容器匹配，则仅更新参数（避免重复 init）
    if (chart && !chart.destroyed && chart.getContainerElement() === el) {
        chart.setSymbol({ticker: props.symbol})
        chart.setPeriod({span: cfg.span, type: cfg.type})
        chart.setDataLoader({
            getBars: async ({callback}) => {
                callback(dataCache.value[cfg.id] || [])
            }
        })
        return
    }

    // 销毁旧实例（容器不匹配或已标记为无效）
    if (chart) {
        try {
            chart.destroy()
        } catch {

        }
        chartInstances.value[cfg.id] = null
    }

    // 创建新实例
    chart = init(cfg.containerId)
    chart.setStyles(createChartConfig('redUp', 'dark'))
    chartInstances.value[cfg.id] = chart

    chart.setSymbol({ticker: props.symbol})
    chart.setPeriod({span: cfg.span, type: cfg.type})
    chart.setDataLoader({
        getBars: async ({callback}) => {
            callback(dataCache.value[cfg.id] || [])
        }
    })
}

// 批量重建三张图（仅用于 symbol 切换或初次挂载）
const rebuildCharts = async () => {
    if (isRebuilding) return
    isRebuilding = true

    // 彻底清空旧实例和数据
    Object.values(chartInstances.value).forEach(c => c?.destroy())
    chartInstances.value = {}
    dataCache.value = {}

    await Promise.all(PERIODS.map(cfg => initPeriodChart(cfg)))

    // stock_info.value = await fetchStockInfo(props.symbol)

    isRebuilding = false
}

// 无 immediate，避免 onMounted 与 watch 同时触发
watch(() => props.symbol, async () => {
    await rebuildCharts()
})

onMounted(async () => {
    await rebuildCharts()
})

onUnmounted(() => {
    Object.values(chartInstances.value).forEach(c => c?.destroy())
    chartInstances.value = {}
})
</script>

<template>
    <div class="vertical-charts">
        <div v-for="p in PERIODS" :key="p.id" class="chart-item">
            <div :id="p.containerId" class="chart-obj"></div>
        </div>
    </div>
</template>

<style scoped lang="scss">
.vertical-charts {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 12px;
    background: #1a1a1a;
}

.chart-obj{
    height: 30vh;
    background: #222
}
</style>