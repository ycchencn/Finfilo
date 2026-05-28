<template>
    <div class="flex h-full w-full bg-gray-50">

        <!-- 左侧智能体列表区域 -->
        <div class="w-72 bg-white border-r border-gray-200 flex flex-col overflow-hidden">

            <!-- 智能体列表 -->
            <div class="flex-1 overflow-y-auto p-2">
              <div
                v-for="agent in agents"
                :key="agent.id"
                :class="[
                  'agent-item p-3 rounded-lg cursor-pointer mb-2 transition-colors',
                  currentAgentId === agent.id
                    ? 'bg-primary-50 border border-primary-200'
                    : 'hover:bg-gray-100 border border-transparent'
                ]"
                @click="selectAgent(agent.id)"
              >
                <!-- 智能体基本信息 + 编辑按钮在同一行 -->
                <div class="flex items-center gap-3">
                  <div
                    class="w-10 h-10 rounded-full bg-primary text-white flex items-center justify-center text-lg font-bold"
                  >
                    {{ agent.avatar }}
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="font-medium text-gray-800 truncate">{{ agent.name }}</p>
                    <p class="text-xs text-gray-400 truncate">{{ agent.model }}</p>
                  </div>
                  <!-- 编辑按钮紧贴右侧 -->
                  <Button
                    icon="pi pi-pencil"
                    severity="secondary"
                    text
                    rounded
                    size="small"
                    @click.stop="editAgent(agent.id)"
                    aria-label="编辑提示词"
                  />
                </div>
                <!-- 删除原来的单独一行编辑按钮 -->
              </div>
            </div>

            <!-- 添加智能体按钮 -->
            <div class="p-3 border-t border-gray-200">
                <Button label="新建智能体" icon="pi pi-plus" class="w-full" severity="contrast" @click="addAgent"/>
            </div>
        </div>

        <!-- 右侧对话区域 -->
        <div class="flex-1 flex flex-col" style="height: 85vh">
            <!-- 当前智能体信息头部 -->
            <div class="p-4 bg-white border-b border-gray-200 flex items-center gap-3">
                <div
                    class="w-10 h-10 rounded-full bg-primary text-white flex items-center justify-center text-lg font-bold">
                    {{ currentAgent.avatar }}
                </div>
                <div>
                    <p class="font-semibold text-gray-800">{{ currentAgent.name }}</p>
                    <p class="text-xs text-gray-500">{{ currentAgent.model }}</p>
                </div>
            </div>

            <!-- 消息列表（复用原聊天组件的消息区域，但数据源改为currentAgent.messages） -->
            <div class="flex-1 overflow-auto p-4 bg-gray-50" ref="messageContainer">
                <div class="mb-4" v-for="msg in currentAgent.messages" :key="msg.id">
                    <!-- 用户消息 -->
                    <div class="flex justify-end mb-2" v-if="msg.role === 'user'">
                        <div class="bg-primary text-white rounded-lg px-4 py-2 max-w-[95%]">
                            <p>{{ msg.content }}</p>
                        </div>
                    </div>
                    <!-- AI消息 -->
                    <div class="flex justify-start mb-2" v-else>
                        <div class="px-2 py-2 w-[95%]">
                            <MarkdownRenderer fontSize="11px" :markdown="msg.content || ''"/>
                            <Skeleton v-if="msg.isLoading" style="width: 12px" class="inline-block"/>
                        </div>
                    </div>
                </div>
                <div ref="scrollAnchor"></div>
            </div>

            <!-- 输入区域（复用原组件） -->
            <div class="p-4 bg-white border-t border-gray-200">
                <div class="flex gap-2">
                    <InputText
                        v-model="inputMessage"
                        placeholder="输入消息，回车发送..."
                        @keyup.enter="sendMessage"
                        class="flex-1"
                        :disabled="isLoading"
                    />
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

        <!-- 编辑提示词的对话框 -->
        <Dialog
            v-model:visible="showEditDialog"
            header="编辑智能体提示词"
            :modal="true"
            :style="{ width: '60vw' }"
            :breakpoints="{ '960px': '75vw', '640px': '90vw' }"
        >
            <div class="flex flex-col gap-3">
                <div>
                    <label class="font-medium text-sm">智能体名称</label>
                    <InputText v-model="editingAgent.name" class="w-full mt-1"/>
                </div>
                <div>
                    <label class="font-medium text-sm">模型ID</label>
                    <InputText v-model="editingAgent.model" class="w-full mt-1"/>
                </div>
                <div>
                    <label class="font-medium text-sm">提示词（System Prompt）</label>
                    <Textarea
                        v-model="editingAgent.systemPrompt"
                        rows="16"
                        class="w-full mt-1"
                        placeholder="请输入系统提示词..."
                    />
                </div>
                <div>
                    <label class="font-medium text-sm">头像（emoji）</label>
                    <InputText v-model="editingAgent.avatar" class="w-full mt-1" placeholder="如 🤖"/>
                </div>
            </div>
            <template #footer>
                <Button label="取消" icon="pi pi-times" @click="cancelEdit" severity="secondary"/>
                <Button label="保存" icon="pi pi-check" @click="saveAgent"/>
            </template>
        </Dialog>
    </div>
</template>

<script setup>
import {ref, computed, watch, onMounted, onUnmounted, nextTick} from 'vue'
import MarkdownRenderer from '@/components/MarkdownRenderer.vue'
import {useToast} from 'primevue/usetoast'

const toast = useToast()

// 智能体数据（可扩展为从后端获取）
const agents = ref([
    {
        id: 1,
        name: '量化助手',
        avatar: '📊',
        model: 'deepseek-v4-flash',
        systemPrompt: '你是一个量化交易金融机构的专家，请以JSON格式输出。',
        messages: [
            {id: 1, role: 'assistant', content: '你好！我是量化助手，有什么可以帮你的？'}
        ]
    },
    {
        id: 2,
        name: '代码助手',
        avatar: '💻',
        model: 'qwen3.6-plus',
        systemPrompt: '你是一个编程专家，擅长多种语言。',
        messages: [
            {id: 1, role: 'assistant', content: 'Hello! I am your coding assistant.'}
        ]
    },
    {
        id: 3,
        name: 'DeepSeek操盘手',
        avatar: '🤖',
        model: 'deepseek-v4-flash',
        systemPrompt: '你是一个通用AI助手，回答一切问题。',
        messages: [
            {id: 1, role: 'assistant', content: '嗨！我是通用助手，有什么问题吗？'}
        ]
    }
])

// 当前选中的智能体ID
const currentAgentId = ref(1)

// 计算当前智能体对象
const currentAgent = computed(() => {
    return agents.value.find(a => a.id === currentAgentId.value) || agents.value[0]
})

// 输入框与加载状态
const inputMessage = ref('')
const isLoading = ref(false)
const scrollAnchor = ref(null)
const messageContainer = ref(null)
const abortController = ref(new AbortController())

// 编辑相关
const showEditDialog = ref(false)
const editingAgent = ref({}) // 编辑中的智能体副本

// 生成唯一ID（用于智能体和消息）
const generateId = () => `id_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`

// 切换智能体
function selectAgent(agentId) {
    if (currentAgentId.value === agentId) return
    currentAgentId.value = agentId
    scrollToBottom()
}

// 开始编辑智能体（弹出对话框，拷贝当前数据）
function editAgent(agentId) {
    const agent = agents.value.find(a => a.id === agentId)
    if (agent) {
        editingAgent.value = JSON.parse(JSON.stringify(agent)) // 深拷贝
        showEditDialog.value = true
    }
}

// 取消编辑
function cancelEdit() {
    showEditDialog.value = false
    editingAgent.value = {}
}

// 保存编辑
function saveAgent() {
    const index = agents.value.findIndex(a => a.id === editingAgent.value.id)
    if (index !== -1) {
        agents.value[index] = {...editingAgent.value}
        toast.add({severity: 'success', summary: '成功', detail: '智能体已更新', life: 2000})
    }
    // 如果当前正在对话的智能体被编辑，则更新当前对话的system prompt已实时生效（因为后面发送请求时使用currentAgent.systemPrompt）
    showEditDialog.value = false
    editingAgent.value = {}
}

// 添加新智能体
function addAgent() {
    const newAgent = {
        id: generateId(),
        name: '新智能体',
        avatar: '🧠',
        model: 'deepseek-v4-flash',
        systemPrompt: '你是一个乐于助人的助手。',
        messages: [
            {id: generateId(), role: 'assistant', content: '你好！我是新智能体，请问有什么需要帮助的吗？'}
        ]
    }
    agents.value.push(newAgent)
    // 自动选中新智能体
    currentAgentId.value = newAgent.id
    toast.add({severity: 'info', summary: '新建成功', detail: `智能体"${newAgent.name}"已创建`, life: 2000})
}

// 发送消息（复用原逻辑，但使用currentAgent的model和systemPrompt）
const sendMessage = async () => {
    if (!inputMessage.value.trim() || isLoading.value) return

    const userMsg = {
        id: generateId(),
        role: 'user',
        content: inputMessage.value.trim()
    }
    currentAgent.value.messages.push(userMsg)
    inputMessage.value = ''
    scrollToBottom()

    const aiMsgId = generateId()
    const loadingMsg = {
        id: aiMsgId,
        role: 'assistant',
        content: '',
        isLoading: true
    }
    currentAgent.value.messages.push(loadingMsg)
    scrollToBottom()
    isLoading.value = true

    // 取消之前未完成的请求
    abortController.value.abort()
    abortController.value = new AbortController()

    try {
        // 构造消息数组：先加入system prompt（如果有）
        const requestMessages = []
        if (currentAgent.value.systemPrompt) {
            requestMessages.push({role: 'system', content: currentAgent.value.systemPrompt})
        }
        // 加入当前智能体的对话历史（除最后一个loading message）
        requestMessages.push(
            ...currentAgent.value.messages
                .filter(m => m.id !== aiMsgId)
                .map(m => ({role: m.role, content: m.content}))
        )

        const response = await fetch('/chat/stream', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                message: userMsg.content,
                session_id: sessionId.value,
                model: currentAgent.value.model,
                messages: requestMessages  // 可选：将完整历史发送给后端
            }),
            signal: abortController.value.signal
        })

        if (!response.ok) throw new Error(`请求失败: ${response.status}`)

        const reader = response.body.getReader()
        const decoder = new TextDecoder('utf-8')
        let aiMsgIndex = currentAgent.value.messages.findIndex(m => m.id === aiMsgId)

        while (true) {
            const {done, value} = await reader.read()
            if (done) break
            const chunk = decoder.decode(value, {stream: true})
            currentAgent.value.messages[aiMsgIndex].content += chunk
            // 可选：实时滚动
            // scrollToBottom()
        }

        currentAgent.value.messages[aiMsgIndex].isLoading = false
    } catch (error) {
        if (error.name !== 'AbortError') {
            const aiMsgIndex = currentAgent.value.messages.findIndex(m => m.id === aiMsgId)
            currentAgent.value.messages[aiMsgIndex].content = `出错了：${error.message || '网络异常'}`
            currentAgent.value.messages[aiMsgIndex].isLoading = false
            console.error('发送失败:', error)
        }
    } finally {
        isLoading.value = false
    }
}

// 生成会话ID（每个智能体独立session？这里简单复用全局session，或者根据agent.id动态生成）
const sessionId = ref('')
const generateSessionId = () => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`

const scrollToBottom = () => {
    nextTick(() => {
        scrollAnchor.value?.scrollIntoView({behavior: 'smooth'})
    })
}

// 监听消息变化自动滚动
watch(
    () => currentAgent.value.messages,
    () => scrollToBottom(),
    {deep: true}
)

onMounted(() => {
    sessionId.value = generateSessionId()
    scrollToBottom()
})

onUnmounted(() => {
    abortController.value.abort()
})
</script>

<style scoped>
/* 自定义滚动条 */
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

/* 左侧智能体列表样式 */
.agent-item {
    transition: all 0.2s;
}

.agent-item:hover {
    background-color: #f3f4f6;
}
</style>