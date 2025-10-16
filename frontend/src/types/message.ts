export enum MessageRole {
  USER = 'user',
  ASSISTANT = 'assistant',
  SYSTEM = 'system'
}

export enum MessageContentType {
  TEXT = 'text',
  CODE = 'code',
  ERROR = 'error',
  JSON = 'json',
  MARKDOWN = 'markdown'
}

export interface Message {
  id: string
  session_id: string
  role: MessageRole
  content: string
  content_type: MessageContentType
  metadata: Record<string, any> | null
  timestamp: string
  sequence_number: number
  is_streamed: boolean
}

export interface CommandRequest {
  command: string
}
