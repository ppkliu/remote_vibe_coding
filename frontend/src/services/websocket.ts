export class WebSocketClient {
  private ws: WebSocket | null = null
  private messageHandlers: Array<(message: any) => void> = []
  private closeHandlers: Array<() => void> = []
  private url: string
  private token: string
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelays = [1000, 2000, 4000, 8000, 30000] // Exponential backoff
  private reconnectTimeout: NodeJS.Timeout | null = null
  private shouldReconnect = true

  constructor(sessionId: string, token: string) {
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'
    this.url = `${wsUrl}/${sessionId}?token=${token}`
    this.token = token
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url)

        this.ws.onopen = () => {
          console.log('[WebSocket] Connected')
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data)
            this.messageHandlers.forEach(handler => handler(message))
          } catch (e) {
            console.error('[WebSocket] Failed to parse message:', e)
          }
        }

        this.ws.onerror = (error) => {
          console.error('[WebSocket] Error:', error)
          reject(error)
        }

        this.ws.onclose = () => {
          console.log('[WebSocket] Disconnected')
          this.handleDisconnect()
        }
      } catch (error) {
        reject(error)
      }
    })
  }

  private handleDisconnect() {
    this.closeHandlers.forEach(handler => handler())

    if (this.shouldReconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
      const delay = this.reconnectDelays[Math.min(this.reconnectAttempts, this.reconnectDelays.length - 1)]
      console.log(`[WebSocket] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts + 1}/${this.maxReconnectAttempts})`)

      this.reconnectTimeout = setTimeout(() => {
        this.reconnectAttempts++
        this.connect().catch(err => {
          console.error('[WebSocket] Reconnect failed:', err)
        })
      }, delay)
    } else if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[WebSocket] Max reconnection attempts reached')
    }
  }

  onMessage(handler: (message: any) => void) {
    this.messageHandlers.push(handler)
  }

  onClose(handler: () => void) {
    this.closeHandlers.push(handler)
  }

  resetReconnectAttempts() {
    this.reconnectAttempts = 0
  }

  getReconnectAttempts(): number {
    return this.reconnectAttempts
  }

  send(data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    } else {
      throw new Error('WebSocket not connected')
    }
  }

  sendCommand(command: string) {
    this.send({ type: 'command', command })
  }

  disconnect() {
    this.shouldReconnect = false
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout)
      this.reconnectTimeout = null
    }
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  manualReconnect() {
    this.reconnectAttempts = 0
    this.shouldReconnect = true
    return this.connect()
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN
  }
}
