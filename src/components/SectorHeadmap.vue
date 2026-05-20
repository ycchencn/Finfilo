<template>
    <div class="heatmap-container">
        <div class="header">
            <h2 class="title">A股板块热力图</h2>
            <div class="controls">
                <el-select v-model="sectorType" placeholder="选择板块类型" class="select">
                    <el-option label="申万二级" value="SW2"/>
                    <el-option label="申万一级" value="SW1"/>
                    <el-option label="行业板块" value="行业板块"/>
                    <el-option label="概念板块" value="概念板块"/>
                </el-select>
                <el-select v-model="weightBy" placeholder="加权方式" class="select">
                    <el-option label="等权" value="eq"/>
                    <el-option label="市值加权" value="cap"/>
                </el-select>
                <el-button type="primary" @click="fetchData(true)" :loading="loading">刷新数据</el-button>
                <span class="update-time">更新时间：{{ updateTime }}</span>
            </div>
        </div>
        <div ref="chartRef" class="chart"></div>
    </div>
</template>

<script setup>
import {ref, onMounted, onUnmounted} from 'vue'
import * as echarts from 'echarts'
import axios from 'axios'

const chartRef = ref(null)
let chartInstance = null
const loading = ref(false)
const sectorType = ref('SW2')
const weightBy = ref('eq')
const updateTime = ref('')

// A股红涨绿跌配色
const colorScale = [
    {value: -10, color: '#00b300'},
    {value: -0.1, color: '#66ff66'},
    {value: 0, color: '#2a2a2a'},
    {value: 0.1, color: '#ff6666'},
    {value: 10, color: '#ff1a1a'}
]

// 渲染图表
const renderChart = (data) => {
    if (!chartInstance) return
    const chartData = data.map(item => ({
        name: item.sector_name,
        value: item.total_trade_amount,
        itemStyle: {
            color: getColor(item.change_pct)
        },
        // 携带所有hover字段
        customData: item
    }))

    const option = {
        tooltip: {
            trigger: 'item',
            formatter: (params) => {
                const d = params.data.customData
                return `
          <div style="padding: 8px; color: #fff;">
            <b>🏷️ 板块：${d.sector_name}</b><br/>
            📈 涨跌幅：${d.change_pct}%<br/>
            💴 成交金额：${d.total_trade_amount}亿<br/>
            ⬆️ 上涨家数：${d.up_count}家<br/>
            ⬇️ 下跌家数：${d.down_count}家<br/>
            📊 涨跌比：${d.up_down_ratio}<br/>
            🔄 平均换手率：${d.avg_turnover}%<br/>
            🚀 领涨股：${d.top_stock}（${d.top_stock_pct}%）<br/>
            💣 领跌股：${d.bottom_stock}（${d.bottom_stock_pct}%）
          </div>
        `
            },
            backgroundColor: 'rgba(0,0,0,0.8)',
            borderColor: 'transparent'
        },
        series: [{
            type: 'treemap',
            data: chartData,
            roam: false,
            label: {
                show: true,
                color: '#fff',
                fontSize: 13,
                fontFamily: '微软雅黑',
                formatter: '{b}\n{c}亿\n{@[customData.change_pct]}%'
            },
            itemStyle: {
                borderColor: '#121212',
                borderWidth: 2,
                gapWidth: 2
            },
            breadcrumb: {
                show: false
            }
        }]
    }
    chartInstance.setOption(option)
}

// 根据涨跌幅计算颜色
const getColor = (pct) => {
    if (pct <= -10) return '#00b300'
    if (pct < 0) return `rgb(0, ${Math.floor(179 + (77 * (10 + pct) / 10))}, 0)`
    if (pct === 0) return '#2a2a2a'
    if (pct <= 10) return `rgb(${Math.floor(255 - (153 * (10 - pct) / 10))}, 0, 0)`
    return '#ff1a1a'
}

// 获取数据
const fetchData = async (refresh = false) => {
    loading.value = true
    try {
        const res = await axios.get('http://localhost:8000/api/sector_heatmap', {
            params: {
                sector_type: sectorType.value,
                weight_by: weightBy.value,
                refresh
            }
        })
        if (res.data.code === 200) {
            renderChart(res.data.data)
            updateTime.value = res.data.update_time
        } else {
            alert(res.data.msg)
        }
    } catch (e) {
        alert('接口请求失败，请检查后端服务是否启动')
    } finally {
        loading.value = false
    }
}

onMounted(() => {
    chartInstance = echarts.init(chartRef.value)
    fetchData()
    // 自适应窗口
    window.addEventListener('resize', () => chartInstance.resize())
})

onUnmounted(() => {
    window.removeEventListener('resize', () => chartInstance.resize())
    chartInstance?.dispose()
})
</script>

<style scoped>
.heatmap-container {
    width: 100%;
    height: 100vh;
    background-color: #121212;
    padding: 20px;
    box-sizing: border-box;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.title {
    color: #fff;
    margin: 0;
}

.controls {
    display: flex;
    gap: 12px;
    align-items: center;
}

.select {
    width: 150px;
}

.update-time {
    color: #aaa;
    font-size: 14px;
}

.chart {
    width: 100%;
    height: calc(100% - 80px);
}
</style>