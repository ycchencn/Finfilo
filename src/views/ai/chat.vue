<script setup>
import {ref, onMounted, watch, nextTick, onUnmounted} from 'vue'
// 响应式数据
const messages = ref([]) // 消息列表
const inputMessage = ref('') // 输入框内容
const isLoading = ref(false) // 加载状态
const sessionId = ref('') // 会话ID
const scrollAnchor = ref(null) // 滚动锚点
// 添加请求控制器：用于取消未完成的流式请求（防止内存泄漏）
const abortController = ref(new AbortController())
import MarkdownRenderer from '@/components/MarkdownRenderer.vue';

// 生成唯一会话ID
const generateSessionId = () => {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

// 修复滚动到底部函数（原来为空，导致消息不滚动）
const scrollToBottom = () => {
    nextTick(() => {
        scrollAnchor.value?.scrollIntoView({behavior: 'smooth'})
    })
}

// 发送消息并处理流式响应（替换axios为fetch，解决浏览器流式兼容性问题）
const sendMessage = async () => {
    if (!inputMessage.value.trim() || isLoading.value) return

    // 1. 添加用户消息到列表
    const userMsg = {
        id: Date.now(),
        role: 'user',
        content: inputMessage.value.trim()
    }
    messages.value.push(userMsg)
    inputMessage.value = ''
    scrollToBottom()

    // 2. 添加AI加载中的占位消息
    const aiMsgId = Date.now() + 1
    const loadingMsg = {
        id: aiMsgId,
        role: 'assistant',
        content: '',
        isLoading: true
    }
    messages.value.push(loadingMsg)
    scrollToBottom()
    isLoading.value = true

    // 取消之前未完成的请求（防止多个流式响应冲突）
    abortController.value.abort()
    abortController.value = new AbortController()

    try {
        // 3. 使用fetch发送流式请求（浏览器原生支持，解决axios兼容性问题）
        const response = await fetch('/chat/stream', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: userMsg.content,
                session_id: sessionId.value,
                model: 'deepseek-v4-flash'
            }),
            signal: abortController.value.signal // 绑定取消信号
        })

        if (!response.ok) {
            throw new Error(`请求失败: ${response.status} ${response.statusText}`)
        }

        // 4. 流式处理响应数据
        const reader = response.body.getReader()
        const decoder = new TextDecoder('utf-8') // 处理中文编码
        let aiMsgIndex = messages.value.findIndex(m => m.id === aiMsgId)

        while (true) {
            const {done, value} = await reader.read()
            if (done) break
            // 解码流式数据并更新AI消息
            const chunk = decoder.decode(value, {stream: true})
            messages.value[aiMsgIndex].content += chunk
            // scrollToBottom()
        }

        // 5. 响应结束后移除加载状态
        messages.value[aiMsgIndex].isLoading = false

    } catch (error) {
        // 忽略主动取消的请求（比如用户快速发送新消息）
        if (error.name !== 'AbortError') {
            const aiMsgIndex = messages.value.findIndex(m => m.id === aiMsgId)
            messages.value[aiMsgIndex].content = `出错了：${error.message || '网络异常'}`
            messages.value[aiMsgIndex].isLoading = false
            console.error('发送失败:', error)
        }
    } finally {
        isLoading.value = false
    }
}

// 组件初始化
onMounted(() => {
    sessionId.value = generateSessionId()
    // 欢迎消息
    messages.value.push({
        id: 1,
        role: 'assistant',
        content: '你好！我是你的AI助手，有什么问题可以问我～'
    })
    // 默认发送你好
    inputMessage.value = '你好'
    sendMessage()
})

// 监听消息变化，自动滚动到底部
watch(messages, scrollToBottom, {deep: true})

// 组件销毁时取消未完成的请求（防止内存泄漏）
onUnmounted(() => {
    abortController.value.abort()
})
</script>

<template>
    <div class="chat-container flex flex-col">

        <!-- 消息列表区域 -->
        <div class="flex-1 overflow-auto p-4 bg-gray-50">
            <!-- 自定义消息气泡 -->
            <div class="mb-4" v-for="msg in messages" :key="msg.id">
                <!-- 用户消息 -->
                <div class="flex justify-end mb-2" v-if="msg.role === 'user'">
                    <div class="bg-primary text-white rounded-lg rounded-br-none px-4 py-2 max-w-[80%]">
                        <p>{{ msg.content }}</p>
                    </div>
                </div>
                <!-- AI消息 -->
                <div class="flex justify-start mb-2" v-else>
                    <div class="bg-white border border-gray-200 rounded-lg rounded-bl-none px-2 py-2 max-w-[80%]">
                        <MarkdownRenderer fontSize="11px" :markdown="msg.content || ''"/>
                        <Skeleton v-if="msg.isLoading" style="width: 12px"></Skeleton>
                    </div>
                </div>
            </div>
            <!-- 自动滚动到底部 -->
            <div ref="scrollAnchor"></div>
        </div>

        <!-- 输入区域 -->
        <div class="p-4 bg-white border-t border-gray-200">
            <div class="flex gap-2">
                <!-- PrimeVue输入框 -->
                <InputText
                    v-model="inputMessage"
                    placeholder="输入消息，回车发送..."
                    @keyup.enter="sendMessage"
                    class="flex-1"
                    :disabled="isLoading"
                />
                <!-- 发送按钮 -->
                <Button
                    label="发送"
                    icon="pi pi-send"
                    @click="sendMessage"
                    :disabled="!inputMessage.trim() || isLoading"
                    severity="primary"
                />
            </div>
        </div>
    </div>
</template>

<style scoped>
.chat-container {
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    height: 80vh;
}

/* 自定义滚动条样式 */
::-webkit-scrollbar {
    width: 6px;
}

::-webkit-scrollbar-track {
    background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
    background: #555;
}
</style>