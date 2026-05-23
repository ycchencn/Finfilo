<script setup lang="ts">
import { useLayout } from '@/layout/composables/layout';
import { computed, ref, watch } from 'vue';
import { useRoute } from 'vue-router'; // ⬇️ 新增引入
import AppFooter from './AppFooter.vue';
import AppSidebar from './AppSidebar.vue';
import AppTopbar from './AppTopbar.vue';

const { layoutConfig, layoutState, isSidebarActive } = useLayout();
const route = useRoute(); // ⬇️ 获取当前路由实例

// ⬇️⬇️️ 判断是否启用紧凑型布局（隐藏导航） ⬇️⬇️⬇️
const isCompactLayout = computed(() => {
  return route.meta?.layoutCompact === true;
});

const containerClass = computed(() => {
    return {
        'layout-overlay': !isCompactLayout.value && layoutConfig.menuMode === 'overlay',
        'layout-static': !isCompactLayout.value && layoutConfig.menuMode === 'static',
        'layout-static-inactive': !isCompactLayout.value && layoutState.staticMenuDesktopInactive && layoutConfig.menuMode === 'static',
        'layout-overlay-active': !isCompactLayout.value && layoutState.overlayMenuActive,
        'layout-mobile-active': !isCompactLayout.value && layoutState.staticMenuMobileActive,
        'layout-fullscreen': isCompactLayout.value // ⬅️ 全屏工作区专属类
    };
});

// ...（外部点击绑定方法保持不变）...
</script>

<template>
    <div class="layout-wrapper min-h-screen" :class="containerClass">

        <!-- ⬇️️⬇️ 核心修改：根据 meta 动态渲染导航栏 ⬇️⬇️⬇️ -->
        <template v-if="!isCompactLayout">
            <app-topbar></app-topbar>
            <app-sidebar></app-sidebar>
            <div class="layout-mask animate-fadein"></div>
        </template>

        <div class="layout-main-container"
             :class="{ 'p-0 layout-trading': isCompactLayout, 'overflow-hidden': isCompactLayout }">
            <div class="layout-main">
                <!-- 交易界面或原业务页均渲染于此 -->
                <router-view></router-view>
            </div>
            <!-- 底部状态栏同样按需隐藏 -->
            <app-footer v-if="!isCompactLayout"></app-footer>
        </div>
    </div>

    <Toast />
</template>

<style scoped>
/* 防止紧凑模式下内容区滚动条与外层冲突 */
.layout-fullscreen .layout-main-container::-webkit-scrollbar { display: none; }
</style>