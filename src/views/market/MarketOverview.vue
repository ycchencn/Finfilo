<script setup lang="ts">
import {ref, onMounted, computed} from 'vue'
import Chart from 'primevue/chart'
import Card from 'primevue/card'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'

// ========================
// 类型定义
// ========================
interface IndexItem {
    name: string
    code: string
    price: number
    change: number
    changePercent: number
}

interface SectorItem {
    name: string
    changePercent: number
    leadingStock: string
}

interface StockItem {
    name: string
    code: string
    price: number
    changePercent: number
}

// ========================
// Mock 数据 - 指数（扩展为6个）
// ========================
const indices = ref<IndexItem[]>([
    {name: '上证指数', code: '000001', price: 3364.85, change: -11.32, changePercent: -0.34},
    {name: '深证成指', code: '399001', price: 10796.58, change: +28.47, changePercent: +0.26},
    {name: '创业板指', code: '399006', price: 2158.63, change: +5.12, changePercent: +0.24},
    {name: '科创50', code: '000688', price: 1089.76, change: +12.34, changePercent: +1.15},
    {name: '科创200', code: '000692', price: 1487.32, change: +7.89, changePercent: +0.53},
    {name: '创业板成长', code: '399296', price: 4521.18, change: -23.45, changePercent: -0.52}
])

// 板块数据
const sectors = ref<SectorItem[]>([
    {name: '半导体', changePercent: 3.21, leadingStock: '中芯国际'},
    {name: '新能源', changePercent: 2.87, leadingStock: '宁德时代'},
    {name: '计算机', changePercent: 2.15, leadingStock: '浪潮信息'},
    {name: '食品饮料', changePercent: -1.23, leadingStock: '贵州茅台'},
    {name: '银行', changePercent: -0.87, leadingStock: '招商银行'},
    {name: '房地产', changePercent: -2.33, leadingStock: '万科A'}
])

const topStocks = ref<StockItem[]>([
    {name: '中芯国际', code: '688981', price: 58.32, changePercent: 5.68},
    {name: '宁德时代', code: '300750', price: 213.45, changePercent: 4.21},
    {name: '贵州茅台', code: '600519', price: 1680.0, changePercent: -2.11},
    {name: '药明康德', code: '603259', price: 47.56, changePercent: 7.32},
    {name: '隆基绿能', code: '601012', price: 21.3, changePercent: 3.45}
])

// ========================
// 分时图（上证指数）数据
// ========================
const minuteChartData = ref({
    labels: ['9:30', '10:00', '10:30', '11:00', '11:30', '13:30', '14:00', '14:30', '15:00'],
    datasets: [
        {
            label: '上证指数',
            data: [3365, 3363, 3367, 3362, 3360, 3364, 3366, 3365, 3364],
            borderColor: '#ef4444',
            backgroundColor: 'rgba(239,68,68,0.1)',
            fill: true,
            tension: 0.4,
            pointRadius: 0
        }
    ]
})

const minuteChartOptions = ref({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {display: false},
        tooltip: {mode: 'index', intersect: false}
    },
    scales: {
        x: {grid: {display: false}},
        y: {grid: {color: '#e5e7eb'}}
    }
})

// ========================
// 涨跌停家数柱状图数据
// ========================
const limitUpDownData = ref({
    labels: ['12/02', '12/02', '12/02', '12/02', '12/02', '12/02', '12/02', '12/03', '12/04', '12/05', '12/06', '12/09', '12/10'],
    datasets: [
        {
            label: '涨停家数',
            data: [68, 72, 68, 72, 68, 72, 68, 72, 81, 56, 94, 102, 88],
            backgroundColor: '#ef4444',
        },
        {
            label: '跌停家数',
            data: [12, 8, 12, 8, 12, 8, 12, 8, 90, 9, 6, 10, 11],
            backgroundColor: '#10b981',
            borderRadius: 4
        }
    ]
})

const limitUpDownOptions = ref({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {position: 'top' as const},
        tooltip: {mode: 'index'}
    },
    scales: {
        x: {grid: {display: false}},
        y: {beginAtZero: true, grid: {color: '#e5e7eb'}}
    }
})

// ========================
// 两市成交额图（柱状图/面积图）
// ========================
const turnoverData = ref({
    labels: ['12/02', '12/03', '12/04', '12/05', '12/06', '12/09', '12/10'],
    datasets: [
        {
            label: '成交额（亿元）',
            data: [18542, 19021, 17896, 21034, 19875, 20321, 21560],
            backgroundColor: 'rgba(59,130,246,0.6)',
            borderColor: '#3b82f6',
            borderWidth: 1,
            borderRadius: 4
        }
    ]
})

const turnoverOptions = ref({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {display: false},
        tooltip: {mode: 'index'}
    },
    scales: {
        x: {grid: {display: false}},
        y: {beginAtZero: false, grid: {color: '#e5e7eb'}}
    }
})

// ========================
// 沪深涨跌分布（柱状图） - 修改为专业柱状图
// ========================
const distributionData = ref({
    labels: ['<-5%', '-5%~-3%', '-3%~-1%', '-1%~0%', '0%~1%', '1%~3%', '3%~5%', '>5%'],
    datasets: [
        {
            label: '家数',
            data: [80, 200, 500, 1000, 1200, 600, 300, 120],
            // 下跌区间（前4个）用绿色系，上涨区间（后4个）用红色系
            backgroundColor: [
                '#14532d', // <-5%
                '#166534', // -5%~-3%
                '#22c55e', // -3%~-1%
                '#4ade80', // -1%~0%
                '#fca5a5', // 0%~1%
                '#ef4444', // 1%~3%
                '#dc2626', // 3%~5%
                '#b91c1c'  // >5%
            ],
            borderRadius: 4,
            borderSkipped: false
        }
    ]
})

const distributionOptions = ref({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            display: false // 单条数据，不显示图例更简洁
        },
        tooltip: {
            callbacks: {
                label: (context: any) => {
                    const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0)
                    const value = context.parsed.y
                    const percent = ((value / total) * 100).toFixed(1)
                    return `${context.label}: ${value} 家 (${percent}%)`
                }
            }
        }
    },
    scales: {
        x: {
            grid: {display: false},
            ticks: {
                font: {size: 11},
                maxRotation: 45
            }
        },
        y: {
            beginAtZero: true,
            grid: {color: '#e5e7eb'},
            title: {
                display: true,
                text: '家数'
            }
        }
    }
})

// ========================
// 辅助函数
// ========================
const getChangeColor = (val: number) => val >= 0 ? '#ef4444' : '#10b981'
const formatSign = (val: number) => val > 0 ? `+${val.toFixed(2)}` : val.toFixed(2)
</script>

<template>
    <div class="dashboard-container">
        <!-- 顶部标题栏 -->
        <div class="header">
            <h1 class="title">沪深大盘监控</h1>
            <span class="update-time">最后更新: {{ new Date().toLocaleTimeString() }}</span>
        </div>

        <!-- 指数卡片行 (6个，自动折行) -->
        <div class="indices-row">
            <Card v-for="item in indices" :key="item.code" class="index-card">
                <template #content>
                    <div class="card-content">
                        <div class="index-name">{{ item.name }}</div>
                        <div class="index-code">{{ item.code }}</div>
                        <div class="index-price">{{ item.price.toFixed(2) }}</div>
                        <div class="index-change" :style="{ color: getChangeColor(item.change) }">
                            <span>{{ formatSign(item.change) }}</span>
                            <span class="change-percent">{{ formatSign(item.changePercent) }}%</span>
                        </div>
                    </div>
                </template>
            </Card>
        </div>

        <!-- 图表行1：分时走势 + 涨跌停家数 -->
        <div class="grid-row">
            <Card class="chart-card">
                <template #title> 上证指数 分时走势</template>
                <template #content>
                    <div class="chart-wrapper">
                        <Chart type="line" :data="minuteChartData" :options="minuteChartOptions"/>
                    </div>
                </template>
            </Card>
            <Card class="distribution-card">
                <template #title> 沪深涨跌分布</template>
                <template #content>
                    <div class="chart-wrapper">
                        <Chart type="bar" :data="distributionData" :options="distributionOptions"/>
                    </div>
                </template>
            </Card>
        </div>

        <!-- 图表行2：板块涨跌幅 + 两市成交额 -->
        <div class="grid-row">

            <Card class="chart-card">
                <template #title> 两市成交额</template>
                <template #content>
                    <div class="chart-wrapper">
                        <Chart type="bar" :data="turnoverData" :options="turnoverOptions"/>
                    </div>
                </template>
            </Card>

            <Card class="chart-card sector-card-custom">
                <template #title> 板块涨跌幅</template>
                <template #content>
                    <DataTable :value="sectors" stripedRows size="small" class="sector-table">
                        <Column field="name" header="板块"/>
                        <Column field="changePercent" header="涨跌幅">
                            <template #body="slotProps">
                                <span :style="{ color: getChangeColor(slotProps.data.changePercent) }">
                                  {{ formatSign(slotProps.data.changePercent) }}%
                                </span>
                            </template>
                        </Column>
                        <Column field="leadingStock" header="领涨股"/>
                    </DataTable>
                </template>
            </Card>
        </div>

    </div>
</template>

<style scoped lang="scss">
// 全局容器
.dashboard-container {
    padding: 1.5rem;
    background: #f5f7fb;
    min-height: 100vh;
    font-family: 'Microsoft YaHei', sans-serif;
}

// 头部
.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;

    .title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1e293b;
        margin: 0;
    }

    .update-time {
        color: #64748b;
        font-size: 0.9rem;
    }
}

// 指数卡片行（使用flex-wrap让六个卡片自动折行）
.indices-row {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    margin-bottom: 1.5rem;

    .index-card {
        flex: 1 1 calc(16.66% - 1rem); // 6个一行，留出间距
        min-width: 160px;
        transition: all 0.2s ease;

        &:hover {
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }
    }
}

.card-content {
    display: flex;
    flex-direction: column;
    align-items: center;

    .index-name {
        font-size: 1rem;
        color: #475569;
        font-weight: 600;
        white-space: nowrap;
    }

    .index-code {
        font-size: 0.75rem;
        color: #94a3b8;
        margin-top: 0.2rem;
    }

    .index-price {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0f172a;
        margin: 0.5rem 0;
        line-height: 1;
    }

    .index-change {
        display: flex;
        gap: 0.5rem;
        font-size: 0.95rem;

        .change-percent {
            color: inherit;
        }
    }
}

// 图表行（两栏布局）
.grid-row {
    display: flex;
    gap: 1.5rem;
    margin-bottom: 1.5rem;
    align-items: stretch; /* 确保左右卡片等高 */

    .chart-card {
        flex: 1;
    }

    .stocks-card {
        flex: 1;
    }

    .distribution-card {
        flex: 1;
    }
}

// 图表容器
.chart-wrapper {
    position: relative;
}

// 涨跌分布卡片 - 柱状图样式（无需额外改动，继承父类即可）
.distribution-card {
    background: #fff;
    margin-bottom: 1.5rem;
}

// 板块表格
.sector-table {
    ::v-deep(.p-datatable-wrapper) {
        max-height: 280px;
        overflow-y: auto;
    }

    td, th {
        padding: 0.4rem 0.5rem;
        font-size: 0.9rem;
    }
}

// 个股表格卡片
.stocks-card {
    .stocks-table {
        td, th {
            padding: 0.4rem 0.5rem;
            font-size: 0.9rem;
        }
    }
}

@media (max-width: 1200px) {
    .grid-row {
        flex-direction: column;

        & > :first-child {
            order: -1;
        }

        /* 可选：让图表始终置顶 */
    }
}

@media (max-width: 768px) {
    .indices-row .index-card {
        flex: 1 1 calc(50% - 1rem);
    }
}
</style>