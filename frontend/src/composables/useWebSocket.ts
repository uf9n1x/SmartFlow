import { ref, onUnmounted } from 'vue'

/**
 * WebSocket 连接管理 composable
 * 提供自动重连、消息收发、连接状态管理
 * @param url - WebSocket 相对路径（如 /api/v1/ws/dashboard）
 */
export function useWebSocket(url: string) {
  /** WebSocket 连接状态 */
  const connected = ref(false)
  /** 接收到的最新数据 */
  const data = ref<any>(null)
  /** WebSocket 实例 */
  let ws: WebSocket | null = null
  /** 重连定时器 */
  let reconnectTimer: number | null = null

  /**
   * 建立 WebSocket 连接
   * 自动处理 onopen / onmessage / onclose / onerror
   * 断开后 3 秒自动重连
   */
  function connect() {
    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${location.host}${url}`
    ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      connected.value = true
    }

    ws.onmessage = (event) => {
      try {
        data.value = JSON.parse(event.data)
      } catch {
        data.value = event.data
      }
    }

    ws.onclose = () => {
      connected.value = false
      // 3 秒后自动重连
      reconnectTimer = window.setTimeout(() => connect(), 3000)
    }

    ws.onerror = () => {
      ws?.close()
    }
  }

  /**
   * 发送消息（JSON 序列化后发送）
   */
  function send(msg: any) {
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(msg))
    }
  }

  /**
   * 断开连接并清除重连定时器
   */
  function disconnect() {
    if (reconnectTimer) clearTimeout(reconnectTimer)
    ws?.close()
  }

  // 组件卸载时自动断开连接
  onUnmounted(() => disconnect())

  return { connected, data, connect, send, disconnect }
}
