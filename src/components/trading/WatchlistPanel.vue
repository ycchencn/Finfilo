<script setup>
import {computed, onBeforeMount, ref} from 'vue'
import axios from "axios"

// 接收来自父组件的当前选中股票
const props = defineProps({
    selectedSymbol: {type: String, default: null},
    realtimeQuotes: {type: Object, default: () => ({})}   // 从父组件传入的实时行情
})

const page_size = 150
const activeTab = ref('全部')
const tabs = ['全部', '持仓', '自选', '监控']
const stock_list = ref([])

// 排序状态：'none' | 'asc' | 'desc'
const sortOrder = ref('desc')

function loadStockList() {
    axios.get(`/api/v1/stocks_monitored?page_size=${page_size}&page=1&market=cn&v=1.2`)
        .then(response => {
            stock_list.value = response.data.map(item => {
                const ohlc = item.ohlc_last
                return {
                    ...item,
                    chg_pct: ohlc?.chg_pct ?? null,
                    close: ohlc?.close ?? null,
                    open: ohlc?.open ?? null,
                    high: ohlc?.high ?? null,
                    low: ohlc?.low ?? null
                }
            })
        })
        .catch(error => {
            console.error('加载股票列表失败:', error)
        })
}

// 根据 sortOrder 排序后的列表
const sortedStocks = computed(() => {
    const merged = stock_list.value.map(stock => {
        const rt = props.realtimeQuotes[stock.symbol]
        if (!rt) return stock
        let chg_pct = rt.chg_pct ?? null
        if (chg_pct === null && stock.lastClose != null && stock.lastClose !== 0) {
            chg_pct = Number(((rt.lastPrice - stock.lastClose) / stock.lastClose * 100).toFixed(2))
        }
        return {
            ...stock,
            close: rt.lastPrice ?? stock.close,
            chg_pct: chg_pct ?? stock.chg_pct,
            high: rt.high ?? stock.high,
            low: rt.low ?? stock.low,
            open: rt.open ?? stock.open,
        }
    })
    if (sortOrder.value === 'none') return merged
    return [...merged].sort((a, b) => {
        const aVal = a.chg_pct ?? 0
        const bVal = b.chg_pct ?? 0
        return sortOrder.value === 'desc' ? bVal - aVal : aVal - bVal
    })
})

// 切换排序模式：none -> desc -> asc -> none ...
function toggleSort() {
    if (sortOrder.value === 'none') {
        sortOrder.value = 'desc'
    } else if (sortOrder.value === 'desc') {
        sortOrder.value = 'asc'
    } else {
        sortOrder.value = 'none'
    }
}

// 事件传递
const emit = defineEmits(['update:symbol'])
const selectStock = (code) => {
    emit('update:symbol', code)
}

onBeforeMount(() => {
    loadStockList()
})
</script>

<template>
    <aside class="w-80 h-full border-r border-gray-800 bg-neutral-900 flex flex-col shrink-0"
           style="height: 96vh; margin-top: 1px;">

        <!-- 头部区域 -->
        <div class="px-3 pt-3 pb-2 border-b border-gray-800 shrink-0">
            <!-- Tab切换 -->
            <div class="flex gap-1 text-xs mb-2 text-gray-400">
                <button v-for="t in tabs" :key="t" :class="{'!text-white': activeTab === t}" @click="activeTab = t">
                    {{ t }}
                </button>
            </div>

            <!-- 涨幅排序按钮 -->
            <button
                @click="toggleSort"
                class="flex items-center gap-1 text-xs text-gray-400 hover:text-white transition-colors cursor-pointer select-none"
            >
                <span :class="{ 'text-blue-400': sortOrder !== 'none' }">涨幅</span>
                <span v-if="sortOrder === 'asc'" class="text-blue-400">↑</span>
                <span v-else-if="sortOrder === 'desc'" class="text-blue-400">↓</span>
                <span v-else class="text-gray-600">↕</span>
            </button>
        </div>

        <!-- 列表区域 -->
        <div class="flex-1 overflow-y-auto min-w-0 custom-scrollbar">
            <div
                v-for="stock in sortedStocks"
                :key="stock.symbol"
                :class="{ 'bg-gray-800': selectedSymbol === stock.symbol }"
                @click="selectStock(stock.symbol)"
                class="px-4 py-3 hover:bg-gray-800 cursor-pointer border-b border-gray-800/40 group transition-colors"
            >
                <div class="flex justify-between items-start">
                    <div>
                        <div class="font-semibold text-sm">{{ stock.name }}</div>
                        <div><span class="text-[10px] text-gray-500">{{ stock.symbol }}</span></div>
                    </div>
                    <div class="text-right">
                        <div class="text-sm font-mono">{{ stock.close?.toFixed(2) ?? '-' }}</div>
                        <div
                            :class="(stock.chg_pct ?? 0) >= 0 ? 'text-red-500' : 'text-green-500'"
                            class="text-xs font-medium mt-0.5"
                        >
                            {{ (stock.chg_pct ?? 0) >= 0 ? '+' : '' }}{{ stock.chg_pct?.toFixed(2) ?? '0.00' }}%
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </aside>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
    width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
    background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
    background-color: #4b5563;
    border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background-color: #6b7280;
}
</style>