export class WebSocketClient {
  private ws: WebSocket | null = null
  private messageHandlers: Array<(message: any) => void> = []
  private url: string
  private token: string

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
        }
      } catch (error) {
        reject(error)
      }
    })
  }

  onMessage(handler: (message: any) => void) {
    this.messageHandlers.push(handler)
  }

  sendCommand(command: string) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: 'command', command }))
    } else {
      throw new Error('WebSocket not connected')
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN
  }
}
