<script setup>

import { FilterMatchMode, FilterOperator } from '@primevue/core/api';
import { onBeforeMount, reactive, ref } from 'vue';
import Dialog from 'primevue/dialog';
import axios from 'axios';
import BullishBearishIndicator from '@/components/BullishBearishIndicator.vue'
import { fetchStockMarketData, fetchStockInfo, dictToMarkdownRecursive, formatDaysAgo } from '@/utils/function.js';

const news = ref(null);
const filters1 = ref(null);
const loading1 = ref(null);
const filters_topic = ref('*');

function initFilters1() {
    filters1.value = {
        global: { value: null, matchMode: FilterMatchMode.CONTAINS },
    };
}

// 封装获取数据的逻辑
const loadNewsData = () => {
    loading1.value = true; // 开启加载状态
    let _filters = filters_topic.value
    if (_filters === '*'){
        _filters = ''
    }
    axios.get('/api/v1/market/search_news', {
        params: {
            page: 1,
            page_size: 500,
            keyword: _filters // 使用当前的 filters_topic 值
        }
    }).then(response => {
        news.value = response.data.items;
        loading1.value = false; // 关闭加载状态
    }).catch(() => {
        loading1.value = false; // 出错也要关闭加载状态
    });
};

onBeforeMount(() => {
    loadNewsData();
    initFilters1();
});

const marketFilterOptions = [
    { label: '全部新闻', value: '*' },
    { label: '特朗普', value: '特朗普' },
    { label: '马斯克', value: '马斯克' },
    { label: '美联储', value: '美联储' },
    { label: '央行', value: '央行' },
    { label: '证监会', value: '证监会' },
    { label: '货币政策', value: '货币政策' },
    { label: '业绩披露', value: '业绩' },
    { label: '商业航天', value: '商业航天' },
    { label: '机器人', value: '机器人' },
    { label: 'CPO', value: 'CPO' },
    { label: 'PCB', value: 'PCB' },
    { label: '芯片', value: '芯片' },
    { label: '创新药', value: '创新药' },
    { label: '黄金', value: '黄金' },
];

</script>

<template>
    <div class="card">
        <div class="font-semibold text-xl mb-4">事件驱动</div>
        <DataTable
            tableStyle="font-size:12px"
            :value="news"
            :paginator="true"
            :rows="50"
            dataKey="id"
            :rowHover="true"
            filterDisplay="menu"
            :loading="loading1"
            :globalFilterFields="['stock_code']"
            :showGridlines="false"
        >
            <template #header>
                <div class="flex flex-col md:flex-row items-center justify-between gap-3 w-full">
                  <!-- 左侧：下拉框 -->
                  <div class="w-full md:w-auto">
                    <SelectButton
                      v-model="filters_topic"
                      :options="marketFilterOptions"
                      optionLabel="label"
                      optionValue="value"
                      @change="loadNewsData"
                      data-testid="market-filter"
                      size="small"
                    />
                  </div>
                </div>
            </template>
            <template #empty> No data found.</template>
            <template #loading> Loading customers data. Please wait.</template>
            <Column field="stock_name" filterField="stock_name" header="">
                <template #body="{ data }">
                  <div class="news-item">

                    <div class="news-time">{{ formatDaysAgo(data.news_time) }} <a v-if="data.url !== ''" :href="data.url" target="_blank"><i class="pi pi-link"></i></a></div>
                    <p class="news-digest font-semibold text-sm" style="font-size: 14px; padding: 5px 0;">{{ data.digest }}</p>

                    <!-- 关联股票 -->
                    <div v-if="data.relations_stocks && data.relations_stocks.length" class="relations-stocks text-sm">
                      <strong>关联股票：</strong>
                      <span
                        v-for="(stock, index) in data.relations_stocks"
                        :key="stock.code"
                        class="stock-tag"
                      >
                        <a class="text-blue-500" :href="'https://gushitong.baidu.com/stock/ab-' + stock.code" target="_blank">
                            {{ stock.code }} ({{ stock.name }})
                        </a>
                        <span v-if="index < data.relations_stocks.length - 1">、</span>
                      </span>
                    </div>

                    <!-- 标签 -->
                    <div v-if="data.tags && data.tags.length" class="tags text-sm">
                      <strong>标签：</strong>
                      <span
                        v-for="tag in data.tags"
                        :key="tag"
                        class="tag-badge text-sm"
                      >{{ tag }}</span>
                    </div>

                      <div class="tags text-sm" v-if="data.bullish_level != 0">
                          <BullishBearishIndicator :value="data.bullish_level" :max-segments="10" />
                      </div>

                  </div>
                </template>
            </Column>
        </DataTable>
    </div>

</template>

<style scoped>
.news-item {
    font-size: 0.95rem;
    line-height: 1.5;
}

.news-time {
    color: #666;
    font-weight: bold;
}

.news-digest {
    margin: 4px 0;
}

.relations-stocks,
.tags {
    margin-top: 6px;
    display: flex;
    align-items: center;
    flex-wrap: wrap;
}

.relations-stocks .stock-tag {
    white-space: nowrap;
}

.tags .tag-badge {
    display: inline-block;
    background-color: #e9ecef;
    border: 1px solid #ced4da;
    border-radius: 4px;
    padding: 2px 6px;
    margin-right: 4px;
    margin-top: 2px;
    font-size: 0.85rem;
    color: #495057;
}
</style>
