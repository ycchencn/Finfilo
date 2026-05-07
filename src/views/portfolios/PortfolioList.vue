<script setup>
import ConfirmDialog from 'primevue/confirmdialog';
import { onBeforeMount, ref } from 'vue';
import axios from 'axios';
import { formatCurrency } from '@/utils/function';

const portfolios = ref([]); // 初始化为空数组，避免 v-for 报错
const loading1 = ref(false);

// 辅助函数：安全计算累计收益率
const calculateCumulativeReturn = (item) => {

    // 1. 防御性编程：检查对象层级是否存在
    const summary = item.summary || {};
    const totalAssets = Number(summary.total_assets);
    const initCash = Number(item.init_cash);

    // 2. 边界值判断：如果总资产或初始资金无效（如 null, undefined, NaN），返回 0 或 '-'
    if (!totalAssets || !initCash) {
        item.summary.total_assets = item.summary.init_cash
        return 0;
    }

    // 3. 计算公式：(总资产 - 本金) / 本金 * 100
    const ratio = (totalAssets - initCash) / initCash;

    // 4. 格式化：保留两位小数 + %
    return ratio * 100;
};

onBeforeMount(() => {
    loading1.value = true;
    axios.get('/api/v1/investment_portfolios')
        .then(response => {
            // --- 核心修改开始 ---
            // 在赋值前对数据进行映射和处理
            const rawData = response.data || [];
            portfolios.value = rawData.map(item => {
                // 这里你可以直接修改原对象，或者创建一个新对象
                // 我们将计算好的结果挂载到 item 上，方便模板直接使用
                item.summary.position_ratio = item.summary.position_ratio * 100;
                item.calculated_return_rate = calculateCumulativeReturn(item);
                return item;
            });
            // --- 核心修改结束 ---
        })
        .catch(err => {
            console.error("数据加载失败", err);
        })
        .finally(() => {
            loading1.value = false;
        });
});

// 1. 阶段映射配置
const PHASE_CONFIG = {
    0: { label: '技术面', type: 'unknown', severity: 'secondary' },
    1: { label: 'AI主观', type: 'accumulate', severity: 'info' },
};

const formatType = (phaseInt) => {
    return PHASE_CONFIG[phaseInt]?.label || PHASE_CONFIG[0].label;
};

</script>

<template>
    <ConfirmDialog></ConfirmDialog>
    <div class="card">
        <DataTable
            tableStyle="font-size:12px"
            :value="portfolios"
            :rows="25"
            dataKey="id"
            :showGridlines="false"
            :rowHover="true"
            filterDisplay="menu"
            :loading="loading1"
            :globalFilterFields="['name']"
            :size="'large'"
            showGridlines
        >
            <template #header>
                <div class="flex flex-col md:flex-row items-center justify-between gap-3 w-full">
                    <!-- 左侧：下拉框 -->
                    <div class="w-full md:w-auto">
                        <span class="font-semibold">AI 量化策略</span>
                    </div>
                    <!-- 右侧：按钮 + 搜索框 -->
                    <div class="flex flex-wrap items-center gap-2 w-full md:w-auto justify-end md:justify-start">
                        <Button
                            type="button"
                            icon="pi pi-plus"
                            size="small"
                            label="添加策略"
                            class="whitespace-nowrap"
                        />
                    </div>
                </div>
            </template>
            <template #empty> No data found.</template>
            <template #loading> Loading customers data. Please wait.</template>

            <Column field="name" filterField="name" header="策略名">
                <template #body="{ data }">
                    {{ data.name }}
                </template>
            </Column>

            <Column field="name" filterField="name" header="策略类型">
                <template #body="{ data }">
                    {{ formatType(data.strategy_type) }}
                </template>
            </Column>

            <Column field="name" filterField="name" header="仓位" style="min-width: 8rem">
                <template #body="{ data }">
                    <ProgressBar :value="data.summary?.position_ratio.toFixed(2)"></ProgressBar>
                </template>
            </Column>

            <Column field="name" filterField="name" header="今日收益">
                <template #body="{ data }">
                    <span class="font-mono"
                      :class="{
                      'text-red-600': data.summary.daily_pnl_change > 0,
                      'text-green-600': data.summary.daily_pnl_change < 0,
                    }">
                        {{ formatCurrency(data.summary.daily_pnl_change, true) }}
                        ({{ (data.summary.daily_pnl_change / data.summary.total_assets * 100).toFixed(2) }}%)
                    </span>
                </template>
            </Column>

            <!-- 修改后的累计收益列 -->
            <Column field="calculated_return_rate" header="累计收益">
                <template #body="{ data }">
                    <!-- 直接使用预处理好的字段，简单且无运行时错误风险 -->
                    <span class="font-mono" :class="{
                        'text-red-600': parseFloat(data.calculated_return_rate) > 0,
                        'text-green-600': parseFloat(data.calculated_return_rate) < 0,
                    }">
                        {{ formatCurrency(data.summary.total_assets - data.init_cash, true) }}
                        ({{ data.calculated_return_rate.toFixed(2) }}%)
                    </span>
                </template>
            </Column>

            <Column field="name" filterField="name" header="浮动盈亏" class="font-mono">
                <template #body="{ data }">
                    <span
                      :class="{
                      'text-red-600': data.summary.total_unrealized_pnl > 0,
                      'text-green-600': data.summary.total_unrealized_pnl < 0,
                    }">{{ formatCurrency(data.summary.total_unrealized_pnl, true) }}
                    </span>
                </template>
            </Column>

            <Column field="name" filterField="name" header="持仓个股">
                <template #body="{ data }">
                    {{ data.assets.length }}
                </template>
            </Column>

            <Column field="name" filterField="name" header="操作">
                <template #body="{ data }">
                    <router-link
                        class="text-blue-500"
                        :to="{ name: 'portfolio_view', params: { portfolio_id: data.portfolio_id } }">查看
                    </router-link>
                </template>
            </Column>
        </DataTable>
    </div>

</template>

<style scoped lang="scss">
:deep(.p-datatable-frozen-tbody) {
    font-weight: bold;
}

:deep(.p-datatable-scrollable .p-frozen-column) {
    font-weight: bold;
}
</style>
