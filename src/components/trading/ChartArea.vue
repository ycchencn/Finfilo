<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import Select from 'primevue/select'
import Divider from 'primevue/divider'

const props = defineProps<{ symbol: string }>()
const period = ref('日线')
const periods = ['分时', '日线', '周线', '月线', '1小时', '15分钟', '5分钟']
const indicator = ref('MACD')

let chartInstance: any = null

// 🟢 图表初始化钩子（后期替换为 lightweight-charts / TradingView）
watch(() => props.symbol, async (newSym) => {
  console.log(`[Chart] Switching to ${newSym}`)
  // await fetchKline(newSym)
  // initChart(instance)
}, { immediate: true })

onMounted(() => {
  // 实际项目中在此调用第三方图表库初始化
  // chartInstance = createChart(document.getElementById('chart-mount'), {...})
})

defineExpose({ destroyChart: () => { chartInstance?.remove(); chartInstance = null } })
</script>

<template>
  <section class="flex-1 flex flex-col h-full relative bg-black">
    <div class="h-11 px-3 border-b border-gray-800 flex items-center justify-between text-xs shrink-0">
      <div class="flex items-center gap-2">
        <Select v-model="period" :options="periods" optionLabel="label" class="w-20" size="small" fluid />
        <Divider type="vertical" class="h-5 mx-1 bg-gray-700" />
        <span class="text-gray-400 tracking-wide">MA EMA BBI DC MACD KDJ RSI ATR</span>
      </div>
      <div class="flex gap-1">
        <Button size="small" icon="pi pi-plus-circle" text round class="!p-1" />
        <Button size="small" icon="pi pi-minus-circle" text round class="!p-1" />
        <Button size="small" icon="pi pi-arrows-alt" text round class="!p-1" />
        <Button size="small" icon="pi pi-download" text round class="!p-1" />
      </div>
    </div>

    <!-- 🟢 挂载点 -->
    <div id="chart-mount" class="flex-1 w-full h-full relative bg-neutral-950">
      <div v-if="!chartInstance" class="absolute inset-0 flex flex-col items-center justify-center text-gray-600 pointer-events-none">
        <svg class="w-10 h-10 mb-2 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
        <span class="text-sm">K 线渲染容器<br><code>#chart-mount</code></span>
      </div>
    </div>
  </section>
</template>