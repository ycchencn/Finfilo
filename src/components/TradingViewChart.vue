<template>
  <div ref="chartContainer" class="tradingview-chart"></div>
</template>

<script>
export default {
  name: 'TradingViewChart',
  props: {
    symbol: {
      type: String,
      default: 'AAPL'
    },
    interval: {
      type: String,
      default: 'D'
    }
  },
  mounted() {
    this.initChart();
  },
  methods: {
    initChart() {
      const widget = new window.TradingView.widget({
        "autosize": true,
        "symbol": this.symbol,
        "interval": this.interval,
        "timezone": "Etc/UTC",
        "theme": "light",
        "style": "1",
        "locale": "en",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "allow_symbol_change": true,
        "container_id": "chartContainer"
      });

      // 你可以在这里添加更多的配置选项
    }
  }
}
</script>

<style scoped>
.tradingview-chart {
  width: 100%;
  height: 600px;
}
</style>
