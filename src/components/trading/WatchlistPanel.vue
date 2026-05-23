<script setup>
import {onBeforeMount, ref} from 'vue'
import axios from "axios";
import {fearGreedToText, getMarketByCode} from "@/utils/function";
const activeTab = ref('全部')
const tabs = ['全部', '持仓', '自选', '监控']
const stock_list = ref([])

function loadStockList(){
    // 获取个股数据
    axios.get(`/api/v1/stocks_monitored?page_size=300&page=1&market=cn&v=1.2`).then(response => {
        stock_list.value = response.data.map(item => {
            const ohlc = item.ohlc_last; // 可能为 null 或 undefined
            return {
                ...item,
                fear_greed: item.greed_data?.fear_greed ?? null,
                fear_greed_text: fearGreedToText(item.greed_data?.fear_greed ?? null),
                chg_pct: ohlc?.chg_pct ?? null,
                close: ohlc?.close ?? null,
                open: ohlc?.open ?? null,
                high: ohlc?.high ?? null,
                low: ohlc?.low ?? null,
                market: getMarketByCode(item.symbol) ?? null
            };
        });
    }).catch(error => {
        console.error('加载股票列表失败:', error);
    });
}

onBeforeMount(() => {
    // 获取个股数据
    loadStockList()
});

</script>

<template>
  <!--
    ⬇️⬇️⬇️ 高度锁定核心代码：
    w-80:       宽度固定
    h-full:     高度继承父级（即 h-screen）
    border-r:   右分割线
  -->
  <aside class="w-80 h-full border-r border-gray-800 bg-neutral-900 flex flex-col shrink-0" style="height: 96vh; margin-top: 1px;">

    <!-- 1. 头部区域：shrink-0 确保不会被压缩 -->
    <div class="px-3 pt-3 pb-2 border-b border-gray-800 shrink-0">
      <!-- Tab切换 -->
      <div class="flex gap-1 text-xs mb-2 text-gray-400">
        <button v-for="t in tabs" :key="t" :class="{'!text-white': activeTab === t}" @click="activeTab = t">{{ t }}</button>
      </div>
      <!-- 搜索框 -->
      <input type="text" placeholder="输入代码..." class="w-full bg-gray-800 text-sm px-2 py-1 rounded outline-none focus:border-blue-500 border border-transparent transition-colors" />
    </div>

    <!-- 2. 列表区域：flex-1 撑满剩余空间，overflow-y-auto 允许滚动 -->
    <div class="flex-1 overflow-y-auto min-w-0 custom-scrollbar">
      <div v-for="(stock, index) in stock_list" :key="stock.code" class="px-4 py-3 hover:bg-gray-800 cursor-pointer border-b border-gray-800/40 group transition-colors">
        <div class="flex justify-between items-start">
          <div>
            <div class="font-semibold text-sm">{{ stock.name }} <span class="text-[10px] text-gray-500 ml-1">{{ stock.symbol }}</span></div>
            <!-- 迷你走势图占位 -->
            <div class="mt-1 h-3 w-16 opacity-30 bg-gradient-to-r from-gray-700 to-gray-600 rounded-sm"></div>
          </div>
          <div class="text-right">
            <div class="text-sm font-mono">{{ stock.close.toFixed(2) }}</div>
            <div :class="stock.chg_pct >= 0 ? 'text-red-500' : 'text-green-500'" class="text-xs font-medium mt-0.5">
              {{ stock.chg_pct >= 0 ? '+' : '' }}{{ stock.chg_pct.toFixed(2) }}%
            </div>
          </div>
        </div>
      </div>
    </div>
  </aside>
</template>

<style scoped>
/* 自定义暗色滚动条 */
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background-color: #4b5563; border-radius: 3px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background-color: #6b7280; }
</style>