<!-- StockValuationChart.vue -->
<template>
    <div
        class="stock-valuation-card"
        :style="cardStyle"
    >
        <!-- 顶部标题区 -->
        <div v-if="showHeader" class="sv-header">
            <h2 :style="titleStyle">{{ title }}</h2>
            <p class="sv-rating" :style="ratingStyle">
                综合评级：<span :style="{color: ratingColor, fontWeight: 'bold'}">{{ ratingText }}</span>
            </p>
        </div>

        <!-- SVG核心图表 -->
        <svg
            width="100%"
            :height="chartHeight"
            :viewBox="`0 0 800 ${chartHeight - 40}`"
            style="display: block;"
        >
            <!-- 背景网格线 -->
            <line v-if="showGrid" x1="200" y1="20" x2="200" :y2="chartHeight - 60" stroke="#eee"
                  stroke-dasharray="4 4"/>
            <line v-if="showGrid" x1="400" y1="20" x2="400" :y2="chartHeight - 60" stroke="#eee"
                  stroke-dasharray="4 4"/>
            <line v-if="showGrid" x1="600" y1="20" x2="600" :y2="chartHeight - 60" stroke="#eee"
                  stroke-dasharray="4 4"/>
            <line v-if="showGrid" x1="0" y1="70" x2="800" y2="70" stroke="#eee" stroke-dasharray="4 4"/>
            <line v-if="showGrid" x1="0" y1="150" x2="800" y2="150" stroke="#eee" stroke-dasharray="4 4"/>
            <line v-if="showGrid" x1="0" y1="230" x2="800" y2="230" stroke="#eee" stroke-dasharray="4 4"/>
            <!-- 预测区间填充 -->
            <path
                :d="`M 400 ${priceToY(currentPrice)} L 800 ${priceToY(conservativeValue)} L 800 ${priceToY(neutralValue)} Z`"
                :fill="conservativeAreaColor"
            />
            <path
                :d="`M 400 ${priceToY(currentPrice)} L 800 ${priceToY(neutralValue)} L 800 ${priceToY(optimisticValue)} Z`"
                :fill="optimisticAreaColor"
            />
            <!-- 历史走势折线 -->
            <path
                :d="historyPath"
                :stroke="historyLineColor"
                stroke-width="2"
                fill="none"
            />
            <!-- 预测线 -->
            <line
                x1="400"
                :y1="priceToY(currentPrice)"
                x2="800"
                :y2="priceToY(conservativeValue)"
                :stroke="conservativeLineColor"
                stroke-width="2"
            />
            <line
                x1="400"
                :y1="priceToY(currentPrice)"
                x2="800"
                :y2="priceToY(neutralValue)"
                :stroke="neutralLineColor"
                stroke-width="2"
                stroke-dasharray="4 4"
            />
            <line
                x1="400"
                :y1="priceToY(currentPrice)"
                x2="800"
                :y2="priceToY(optimisticValue)"
                :stroke="optimisticLineColor"
                stroke-width="2"
            />
            <!-- 当前价格标记 -->
            <circle cx="400" :cy="priceToY(currentPrice)" r="6" :fill="historyLineColor"/>
            <text
                x="400"
                :y="priceToY(currentPrice) - 20"
                text-anchor="middle"
                font-size="16"
                font-weight="bold"
            >
                现价 {{ currentPrice }}
            </text>
            <!-- 右侧标签 -->
            <rect x="700" y="20" width="100" height="32" rx="4" :fill="optimisticLineColor"/>
            <text x="750" y="42" text-anchor="middle" fill="#fff" font-size="14">
                乐观 {{ optimisticValue }}
            </text>
            <rect x="700" y="64" width="100" height="32" rx="4" :fill="neutralLineColor"/>
            <text x="750" y="86" text-anchor="middle" fill="#fff" font-size="14">
                中性 {{ neutralValue }}
            </text>
            <rect x="700" y="108" width="100" height="32" rx="4" :fill="conservativeLineColor"/>
            <text x="750" y="130" text-anchor="middle" fill="#fff" font-size="14">
                保守 {{ conservativeValue }}
            </text>
        </svg>

        <!-- X轴说明 -->
        <div v-if="showXAxisLabel" class="sv-xlabel" :style="xLabelStyle">
            <span>过去1年走势</span>
            <span>未来1年预测</span>
        </div>

        <!-- 估值说明区 -->
        <div v-if="showAdvice" class="sv-advice" :style="adviceStyle">
            <h4 v-if="adviceTitle" style="margin: 0 0 10px 0; font-size: 16px;">{{ adviceTitle }}</h4>
            <p style="margin: 0; line-height: 1.6; color: #333;">{{ adviceText }}</p>
        </div>
    </div>
</template>

<script setup>
import {computed} from 'vue'

const props = defineProps({
    /**
     * 估值核心数据，必填
     * @type {Object}
     * @property {string} 当前股价 - 股票当前价格
     * @property {string} 估值判断 - 估值建议文本
     * @property {Object} 每股内在价值 - 三个情景的估值
     * @property {string} 每股内在价值.保守情景 - 保守目标价
     * @property {string} 每股内在价值.中性情景 - 中性目标价
     * @property {string} 每股内在价值.乐观情景 - 乐观目标价
     */
    data: {
        type: Object,
        required: true,
        validator: (val) => {
            return val?.当前股价 && val?.估值判断 && val?.每股内在价值
        }
    },
    /** 组件标题 */
    title: {
        type: String,
        default: '个股估值预测'
    },
    /** 评级文字 */
    ratingText: {
        type: String,
        default: '买入'
    },
    /** 评级文字颜色 */
    ratingColor: {
        type: String,
        default: '#f43f5e'
    },
    /** 价格区间最小值，用于坐标映射 */
    minPrice: {
        type: Number,
        default: 20
    },
    /** 价格区间最大值，用于坐标映射 */
    maxPrice: {
        type: Number,
        default: 90
    },
    /** 图表高度 */
    chartHeight: {
        type: Number,
        default: 200
    },
    /** 历史走势数据，数组格式，不传则自动生成模拟数据 */
    historyData: {
        type: Array,
        default: () => []
    },
    /** 是否显示顶部头部 */
    showHeader: {
        type: Boolean,
        default: false
    },
    /** 是否显示网格线 */
    showGrid: {
        type: Boolean,
        default: true
    },
    /** 是否显示X轴说明 */
    showXAxisLabel: {
        type: Boolean,
        default: false
    },
    /** 是否显示估值建议 */
    showAdvice: {
        type: Boolean,
        default: false
    },
    /** 估值建议标题 */
    adviceTitle: {
        type: String,
        default: '估值判断'
    },
    /** 自定义卡片样式 */
    cardStyle: {
        type: Object,
        default: () => ({
            maxWidth: '900px',
            margin: '20px auto',
            padding: '20px',
            background: '#fff',
            borderRadius: '0px',
            boxShadow: ''
        })
    },
    /** 配色自定义 */
    historyLineColor: {type: String, default: '#3b82f6'},
    conservativeLineColor: {type: String, default: '#22c55e'},
    neutralLineColor: {type: String, default: '#6b7280'},
    optimisticLineColor: {type: String, default: '#ef4444'},
    conservativeAreaColor: {type: String, default: 'rgba(34, 197, 94, 0.15)'},
    optimisticAreaColor: {type: String, default: 'rgba(239, 68, 68, 0.15)'}
})

// 数据提取&容错
const currentPrice = computed(() => Number(props.data.当前股价 || 0))
const conservativeValue = computed(() => Number(props.data.每股内在价值?.保守情景 || 0))
const neutralValue = computed(() => Number(props.data.每股内在价值?.中性情景 || 0))
const optimisticValue = computed(() => Number(props.data.每股内在价值?.乐观情景 || 0))
const adviceText = computed(() => props.data.估值判断 || '暂无估值建议')

/**
 * 价格转SVG Y坐标
 * @param {number} price 股票价格
 * @returns {number} Y坐标值
 */
const priceToY = (price) => {
    const validHeight = props.chartHeight - 80
    return (props.chartHeight - 40) - ((price - props.minPrice) * validHeight / (props.maxPrice - props.minPrice))
}

/**
 * 生成历史走势路径
 */
const historyPath = computed(() => {
    // 如果用户传入了真实历史数据，优先使用
    if (props.historyData.length) {
        let path = `M 0 ${priceToY(props.historyData[0])}`
        const step = 400 / (props.historyData.length - 1)
        props.historyData.forEach((price, index) => {
            if (index === 0) return
            path += ` L ${index * step} ${priceToY(price)}`
        })
        path += ` L 400 ${priceToY(currentPrice.value)}`
        return path
    }
    // 没有传入则生成模拟数据
    let path = 'M 0 120'
    let lastY = 120
    for (let i = 1; i < 10; i++) {
        lastY += (Math.random() - 0.5) * 40
        lastY = Math.max(30, Math.min(lastY, props.chartHeight - 50))
        path += ` L ${i * 40} ${lastY}`
    }
    path += ` L 400 ${priceToY(currentPrice.value)}`
    return path
})
</script>