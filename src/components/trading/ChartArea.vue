<script setup lang="ts">
import {ref, watch, onMounted, onUnmounted, nextTick} from 'vue'
import {createChartConfig} from '@/utils/constants.js'
import {fetchStockMarketData, fetchStockInfo} from '@/utils/function.js'
import {init} from 'klinecharts'

// 接收来自父组件的当前选中股票
const props = defineProps({
    symbol: {type: String, default: null},
    realtimeQuotes: {type: Object, default: () => ({})}   // 从父组件传入的实时行情
})

// 获取今日 0 点时间戳（毫秒）
function getTodayStartTimestamp(): number {
    const d = new Date()
    d.setHours(0, 0, 0, 0)
    return d.getTime()
}

// 根据实时报价更新或追加日线数据
function updateDailyDataWithRealtime(symbol: string) {
    const dailyBars = symbolDataCache[symbol]
    if (!dailyBars || dailyBars.length === 0) return
    const rt = props.realtimeQuotes
    if (!rt) return
    const todayStart = getTodayStartTimestamp()
    const lastBar = dailyBars[dailyBars.length - 1]
    const lastDate = new Date(lastBar.timestamp).setHours(0, 0, 0, 0)
    if (lastDate === todayStart) {
        // 更新当日 K 线
        lastBar.close = rt.lastPrice
        if (rt.high != null) lastBar.high = Math.max(lastBar.high ?? rt.lastPrice, rt.high)
        if (rt.low != null) lastBar.low = Math.min(lastBar.low ?? rt.lastPrice, rt.low)
        lastBar.volume = rt.volume ?? lastBar.volume
        lastBar.chg_pct = rt.chg_pct  // 如果源数据提供了涨跌幅
    } else if (lastDate < todayStart) {
        // 没有今日 K 线，新建一根
        const prevClose = lastBar.close
        const newBar = {
            timestamp: todayStart,
            open: rt.open ?? rt.lastPrice,
            high: rt.high ?? rt.lastPrice,
            low: rt.low ?? rt.lastPrice,
            close: rt.lastPrice,
            volume: rt.volume ?? 0,
            chg_pct: prevClose ? Number(((rt.lastPrice - prevClose) / prevClose * 100).toFixed(2)) : 0
        }
        dailyBars.push(newBar)
    }
}

// 重新聚合周/月数据
function updateAggregatedBars(symbol: string) {
    const dailyBars = symbolDataCache[symbol]
    if (!dailyBars) return
    PERIODS.forEach(cfg => {
        if (cfg.type === 'day') {
            dataCache[cfg.id] = dailyBars
        } else {
            dataCache[cfg.id] = aggregateBars(dailyBars, cfg.type as 'week' | 'month')
        }
    })
}

// 刷新所有图表
function refreshCharts() {
    PERIODS.forEach(cfg => {
        const chart = chartInstances.value[cfg.id]
        if (!chart) return
        const bars = dataCache[cfg.id]
        if (!bars || bars.length === 0) return
        chart.applyNewData([bars[bars.length - 1]], false)
    })
}

// 实时行情变化时更新图表
function applyRealtimeUpdate() {
    updateDailyDataWithRealtime(props.symbol)
    updateAggregatedBars(props.symbol)
    refreshCharts()
}

watch(() => props.realtimeQuotes, (newRt) => {
    // if (newRt) applyRealtimeUpdate()
})

const PERIODS = [
    {id: 'm', containerId: 'chart-month', type: 'month', span: 1},
    {id: 'w', containerId: 'chart-week', type: 'week', span: 1},
    {id: 'd', containerId: 'chart-day', type: 'day', span: 1}
] as const

const symbolDataCache: Record<string, any[]> = {}
const dataCache: Record<string, any[]> = {}
const chartInstances = ref<Record<string, any>>({})
let isRebuilding = false

const loading = ref(false) // 加载状态

interface OHLC {
    timestamp: number
    open: number
    high: number
    low: number
    close: number
    volume: number
    chg_pct?: number
}

function aggregateBars(dailyBars: OHLC[], mode: 'week' | 'month'): OHLC[] {
    const result: OHLC[] = []
    let idx = 0
    let prevClose: number | null = null

    while (idx < dailyBars.length) {
        const group: OHLC[] = []
        const date = new Date(dailyBars[idx].timestamp)

        if (mode === 'week') {
            const startDate = new Date(dailyBars[idx].timestamp)
            startDate.setHours(0, 0, 0, 0)
            const endOfWeek = new Date(startDate)
            endOfWeek.setDate(startDate.getDate() + (7 - startDate.getDay()))

            while (idx < dailyBars.length && new Date(dailyBars[idx].timestamp) < endOfWeek) {
                group.push(dailyBars[idx])
                idx++
            }
            if (group.length === 0) continue
        } else if (mode === 'month') {
            const year = date.getFullYear()
            const month = date.getMonth()
            while (idx < dailyBars.length) {
                const bar = dailyBars[idx]
                const barDate = new Date(bar.timestamp)
                if (barDate.getFullYear() === year && barDate.getMonth() === month) {
                    group.push(bar)
                    idx++
                } else {
                    break
                }
            }
            if (group.length === 0) continue
        }

        const open = group[0].open
        const close = group[group.length - 1].close
        const high = Math.max(...group.map(b => b.high))
        const low = Math.min(...group.map(b => b.low))
        const volume = group.reduce((sum, b) => sum + b.volume, 0)

        let chg_pct = 0
        if (prevClose !== null && prevClose !== 0) {
            chg_pct = Number(((close - prevClose) / prevClose * 100).toFixed(2))
        }

        result.push({timestamp: group[0].timestamp, open, high, low, close, volume, chg_pct})
        prevClose = close
    }

    return result
}

const initPeriodChart = async (cfg: typeof PERIODS[number]) => {
    if (!symbolDataCache[props.symbol] || symbolDataCache[props.symbol].length === 0) {
        symbolDataCache[props.symbol] = await fetchStockMarketData(props.symbol)
    }

    if (cfg.type === 'week') {
        dataCache[cfg.id] = aggregateBars(symbolDataCache[props.symbol], 'week')
    } else if (cfg.type === 'month') {
        dataCache[cfg.id] = aggregateBars(symbolDataCache[props.symbol], 'month')
    } else {
        dataCache[cfg.id] = symbolDataCache[props.symbol]
    }

    await nextTick()
    const el = document.getElementById(cfg.containerId)
    if (!el) return

    let chart = chartInstances.value[cfg.id]
    if (chart) {
        try {
            chart.destroy()
        } catch {
        }
        chartInstances.value[cfg.id] = null
    }

    chart = init(cfg.containerId)
    chart.setStyles(createChartConfig('redUp', 'dark'))
    chartInstances.value[cfg.id] = chart

    chart.setSymbol({ticker: props.symbol})
    chart.setPeriod({span: cfg.span, type: cfg.type})
    chart.setDataLoader({
        getBars: async ({callback}) => {
            callback(dataCache[cfg.id] || [])
        }
    })
    chart.createIndicator('MA', {pane: {id: 'candle_pane'}, isStack: true})
    chart.createIndicator('MACD', true, {id: 'candle_pane_1'})
}

const rebuildCharts = async () => {
    if (isRebuilding) return
    isRebuilding = true

    Object.values(chartInstances.value).forEach(c => c?.destroy())
    chartInstances.value = {}

    try {
        await Promise.all(PERIODS.map(cfg => initPeriodChart(cfg)))
    } finally {
        isRebuilding = false
    }
}

watch(() => props.symbol, async (newSym, oldSym) => {
    loading.value = true
    symbolDataCache[props.symbol] = await fetchStockMarketData(props.symbol)
    if (newSym !== oldSym) {
        delete symbolDataCache[oldSym]
        await rebuildCharts()
    }
    loading.value = false
})

onMounted(async () => {
    loading.value = true
    try {
        symbolDataCache[props.symbol] = await fetchStockMarketData(props.symbol)
        await rebuildCharts()
    } finally {
        loading.value = false
    }
})

onUnmounted(() => {
    Object.values(chartInstances.value).forEach(c => c?.destroy())
    chartInstances.value = {}
})
</script>

<template>
    <div class="relative vertical-charts">
        <!-- 加载遮盖层 -->
        <div v-if="loading"
             class="absolute inset-0 z-50 flex items-center justify-center bg-neutral-950/70 backdrop-blur-sm">
            <div class="flex flex-col items-center gap-3">
                <svg class="animate-spin h-8 w-8 text-blue-400" xmlns="http://www.w3.org/2000/svg" fill="none"
                     viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor"
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span class="text-sm text-gray-300">加载数据中...</span>
            </div>
        </div>

        <!-- 图表区域 -->
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
    gap: 0;
    position: relative; // 确保遮盖层定位基准
}

.chart-obj {
    height: 31.5vh;
    margin: 5px 5px 0;
}
</style>