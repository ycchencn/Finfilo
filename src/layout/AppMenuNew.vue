<script setup>
import { ref } from 'vue';

import AppMenuItem from './AppMenuItem.vue';

const model = ref([
    {
        label: '市场监控',
        icon: 'pi pi-radar',
        items: [
            {
                label: '智能看板',
                icon: 'pi pi-table',
                items: [
                    { label: '市场温度', icon: 'pi pi-chart-scatter', url: '/grafana/dashboard' },
                    { label: '题材追踪', icon: 'pi pi-tags', to: '/market/theme_tracking' },
                    { label: 'ETF资金流', icon: 'pi pi-chart-line', to: '/market/etf_insight' }
                ]
            },
            {
                label: '事件驱动',
                icon: 'pi pi-bolt',
                items: [
                    { label: '新闻聚合', icon: 'pi pi-globe', to: '/market/news_flow' }
                ]
            }
        ]
    },
    {
        label: '量化工坊',
        icon: 'pi pi-microchip',
        items: [
            {
                label: '策略开发',
                icon: 'pi pi-code',
                items: [
                    { label: '策略回测', icon: 'pi pi-history', to: '/quant/backtest' }
                ]
            },
            {
                label: '组合管理',
                icon: 'pi pi-briefcase',
                items: [
                    { label: '股票池', icon: 'pi pi-database', to: '/quant/stock_pool' },
                    { label: '实盘监控', icon: 'pi pi-eye', to: '/quant/live_monitor' }
                ]
            }
        ]
    },
    {
        label: '数据中心',
        icon: 'pi pi-cloud',
        items: [
            { label: '另类数据', icon: 'pi pi-shield', to: '/data/alternative' },
            { label: 'API集市', icon: 'pi pi-code', url: '/api-market' },
            { label: '数据清洗', icon: 'pi pi-filter', to: '/data/cleaning' }
        ]
    },
    {
        label: '系统配置',
        icon: 'pi pi-cog',
        items: [
            {
                label: '账户管理',
                icon: 'pi pi-user',
                items: [
                    { label: '关注清单', icon: 'pi pi-bookmark', to: '/user/watchlist' },
                    { label: '权限设置', icon: 'pi pi-lock', to: '/user/permissions' }
                ]
            },
            {
                label: '系统维护',
                icon: 'pi pi-wrench',
                items: [
                    { label: '日志审计', icon: 'pi pi-file', to: '/system/logs' },
                    { label: '性能监控', icon: 'pi pi-stopwatch', to: '/system/monitor' }
                ]
            }
        ]
    }
]);
</script>

<template>
    <ul class="layout-menu">
        <template v-for="(item, i) in model" :key="item">
            <app-menu-item v-if="!item.separator" :item="item" :index="i"></app-menu-item>
            <li v-if="item.separator" class="menu-separator"></li>
        </template>
    </ul>
</template>

<style lang="scss" scoped></style>
