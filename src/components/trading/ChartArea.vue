<script setup lang="ts">
import {ref, watch, onMounted, onUnmounted, nextTick} from 'vue'
import {createChartConfig} from '@/utils/constants.js'
import {fetchStockMarketData, fetchStockInfo} from '@/utils/function.js'
import {init} from 'klinecharts'

const props = defineProps<{ symbol: string }>()
// const stock_info = ref({name: '', concepts: ''})

const PERIODS = [
    {id: 'm', containerId: 'chart-month', type: 'month', span: 1},
    {id: 'w', containerId: 'chart-week', type: 'week', span: 1},
    {id: 'd', containerId: 'chart-day', type: 'day', span: 1}
] as const

const symbolDataCache: Record<string, any[]> = {}
const dataCache: Record<string, any[]> = {}
const chartInstances = ref<Record<string, any>>({})
// ✅ 改为模块级 Map（放在 <script setup> 上方）
let isRebuilding = false

interface OHLC {
    timestamp: number
    open: number
    high: number
    low: number
    close: number
    volume: number
    chg_pct?: number
}

/**
 * 按周/月聚合日线数据（自然周/自然月）
 * @param dailyBars 升序日线数据
 * @param mode 'week' | 'month'
 */
function aggregateBars(dailyBars: OHLC[], mode: 'week' | 'month'): OHLC[] {
    const result: OHLC[] = []
    let idx = 0
    let prevClose: number | null = null  // 前一根聚合K线的收盘价

    while (idx < dailyBars.length) {
        const group: OHLC[] = []
        const date = new Date(dailyBars[idx].timestamp)

        if (mode === 'week') {
            // 确定本周结束时间（下周一的00:00:00）
            const startDate = new Date(dailyBars[idx].timestamp)
            startDate.setHours(0, 0, 0, 0)
            const endOfWeek = new Date(startDate)
            endOfWeek.setDate(startDate.getDate() + (7 - startDate.getDay()))

            // 收集本周内所有日线数据
            while (idx < dailyBars.length && new Date(dailyBars[idx].timestamp) < endOfWeek) {
                group.push(dailyBars[idx])
                idx++
            }
            if (group.length === 0) continue

        } else if (mode === 'month') {
            const year = date.getFullYear()
            const month = date.getMonth()
            // 收集同一月份的所有日线数据
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

        // 聚合OHLCV
        const open = group[0].open
        const close = group[group.length - 1].close
        const high = Math.max(...group.map(b => b.high))
        const low = Math.min(...group.map(b => b.low))
        const volume = group.reduce((sum, b) => sum + b.volume, 0)

        // 计算涨跌幅（相对前一根K线收盘价）
        let chg_pct = 0
        if (prevClose !== null && prevClose !== 0) {
            chg_pct = Number(((close - prevClose) / prevClose * 100).toFixed(2))
        }

        // 构建聚合后的K线对象
        const bar: OHLC = {
            timestamp: group[0].timestamp,
            open,
            high,
            low,
            close,
            volume,
            chg_pct
        }

        result.push(bar)
        prevClose = close  // 更新前一根收盘价
    }

    return result
}

// 独立初始化单周期图表
const initPeriodChart = async (cfg: typeof PERIODS[number]) => {

    // 始终先获取日线数据（可以复用 symbol 缓存）
    if (!symbolDataCache[props.symbol] || symbolDataCache[props.symbol].length === 0) {
        symbolDataCache[props.symbol] = await fetchStockMarketData(props.symbol)
    }

    // let bars = await fetchStockMarketData(props.symbol, null, null, 'd')
    if (cfg.type === 'week') {
        dataCache[cfg.id] = aggregateBars(symbolDataCache[props.symbol], 'week')
    } else if (cfg.type === 'month') {
        dataCache[cfg.id] = aggregateBars(symbolDataCache[props.symbol], 'month')
    } else if (cfg.type === 'day') {
        dataCache[cfg.id] = symbolDataCache[props.symbol];
    }

    await nextTick()
    const el = document.getElementById(cfg.containerId)
    if (!el) return

    let chart = chartInstances.value[cfg.id]

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
            callback(dataCache[cfg.id] || [])
        }
    })
    chart.createIndicator('MA', {pane: {id: 'candle_pane'}, isStack: true})
    chart.createIndicator('MACD', true, {id: 'candle_pane_1'});
}

// 批量重建三张图（仅用于 symbol 切换或初次挂载）
const rebuildCharts = async () => {
    if (isRebuilding) return
    isRebuilding = true

    // 彻底清空旧实例和数据
    Object.values(chartInstances.value).forEach(c => c?.destroy())
    chartInstances.value = {}

    await Promise.all(PERIODS.map(cfg => initPeriodChart(cfg)))

    isRebuilding = false
}

// 专门在 symbol 变化时清除对应缓存
watch(() => props.symbol, async (newSym, oldSym) => {
    symbolDataCache[props.symbol] = await fetchStockMarketData(props.symbol)
    if (newSym !== oldSym) {
        // 清除旧标的缓存（避免内存无限增长）
        delete symbolDataCache[oldSym]
        await rebuildCharts()
    }
})

onMounted(async () => {
    symbolDataCache[props.symbol] = await fetchStockMarketData(props.symbol)
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
    gap: 0;
    //background: #1a1a1a;
}

.chart-obj {
    height: 31.5vh;
    //background: #222;
    margin: 5px 5px 0;;
}
</style>