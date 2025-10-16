export enum SessionStatus {
  CREATED = 'CREATED',
  CONNECTING = 'CONNECTING',
  ACTIVE = 'ACTIVE',
  DISCONNECTED = 'DISCONNECTED',
  RECONNECTING = 'RECONNECTING',
  IDLE = 'IDLE',
  ENDED = 'ENDED'
}

export interface Session {
  id: string
  user_id: string
  title: string | null
  status: SessionStatus
  created_at: string
  last_activity: string
  ended_at: string | null
}

export interface SessionCreate {
  title?: string
  working_directory?: string
}
