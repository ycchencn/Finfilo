<template>
    <div class="progress-bar" :style="{ width: '100%', height: barHeight + 'px' }">
        <div class="progress-bar-fill"
             :style="{ width: value + '%', height: '100%', background: fillBackground }"></div>
        <span class="progress-bar-value">{{ value }} ℃</span>
    </div>
</template>

<script>
export default {
    props: {
        value: {
            type: Number,
            required: true,
            validator: (value) => value >= 0 && value <= 100
        },
        barHeight: {
            type: Number,
            default: 25
        }
    },
    computed: {
        fillBackground() {
            if (this.value > 40) {
                return 'linear-gradient(to left, rgba(255, 107, 107, 0.8), rgba(255, 71, 87, 0.8))';
            } else {
                return 'linear-gradient(to left, rgba(106, 176, 76, 0.8), rgba(46, 204, 113, 0.8))';
            }
        }
    }
};
</script>

<style scoped>
.progress-bar {
    position: relative;
    background-color: #f3f3f3;
    overflow: hidden;
}

.progress-bar-fill {
    position: absolute;
    top: 0;
    left: 0;
    background-color: #4caf50;
    transition: width 0.3s ease;
    border-radius: 3px;
}

.progress-bar-value {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: #333;
    font-weight: normal;
    z-index: 1; /* 确保文字在进度条之上 */
    font-size: 12px;
    cursor: default;
}
</style>
