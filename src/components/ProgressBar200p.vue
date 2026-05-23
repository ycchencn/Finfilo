<template>
    <div class="progress-bar" :style="{ width: '100px', height: barHeight + 'px' }">
        <div class="progress-bar-fill" :style="fillStyle"></div>
        <span class="progress-bar-value">{{ value }} %</span>
    </div>
</template>

<script>
export default {
    props: {
        value: {
            type: Number,
            required: true,
            validator: (value) => value >= -100 && value <= 100
        },
        barHeight: {
            type: Number,
            default: 25
        },
        times: {
            type: Number,
            default: 1
        }
    },
    computed: {
        fillBackground() {
            if (this.value > 0) {
                return 'linear-gradient(to left, rgba(255, 107, 107, 0.8), rgba(255, 71, 87, 0.8))';
            } else {
                return 'linear-gradient(to right, rgba(106, 176, 76, 0.8), rgba(46, 204, 113, 0.8))';
            }
        },
        fillStyle() {
            const absValue = Math.abs(this.value) * this.times;
            if (this.value > 0) {
                return {
                    width: `${absValue / 2}%`,
                    height: '100%',
                    background: this.fillBackground,
                    left: '50%',
                    right: 'auto'
                };
            } else if (this.value < 0) {
                return {
                    width: `${absValue / 2}%`,
                    height: '100%',
                    background: this.fillBackground,
                    left: `calc(50% - ${absValue / 2}%)`,
                    right: 'auto'
                };
            } else {
                return {
                    width: '0%',
                    height: '100%',
                    background: this.fillBackground,
                    left: '50%',
                    right: 'auto'
                };
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
    transition: width 0.3s ease, left 0.3s ease;
    border-radius: 3px;
}

.progress-bar-value {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: #555;
    font-weight: normal;
    z-index: 1; /* 确保文字在进度条之上 */
    font-size: 12px;
    cursor: default;
}
</style>
