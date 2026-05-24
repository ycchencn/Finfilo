function connectRealtime() {
    if (ws) ws.close()
    ws = new WebSocket('ws://localhost:8765')   // 你的转发服务端地址
    ws.onopen = () => {
        ws.send(JSON.stringify({role: 'viewer', symbol: '*'}))
        console.log('📡 终端已订阅全部行情')
    }
    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data)
            console.log(data)
            if (data.type === 'subscribed') return
            // 更新对应 symbol 的实时数据
            realtimeQuotes.value = {
                ...realtimeQuotes.value,
                [data.symbol]: data
            }
        } catch (e) {
            console.warn('WS 消息解析失败', e)
        }
    }
    ws.onerror = (e) => console.error('WS 错误', e)
    ws.onclose = () => {
        console.log('🔌 行情连接断开，5秒后重连...')
        setTimeout(connectRealtime, 5000)
    }
}