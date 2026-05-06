export interface SSEEvent {
  type: string
  data: any
}

export interface SSEConnection {
  close: () => void
}

const SSE_EVENT_TYPES = [
  'node_started',
  'node_completed',
  'node_failed',
  'llm_connecting',
  'llm_connected',
  'llm_failed',
  'workflow_completed',
]

export function connectSSE(
  url: string,
  onEvent: (event: SSEEvent) => void,
  onError?: (error: Event) => void,
): SSEConnection {
  const source = new EventSource(url)

  for (const type of SSE_EVENT_TYPES) {
    source.addEventListener(type, (e: MessageEvent) => {
      try {
        const data = JSON.parse(e.data)
        onEvent({ type, data })
      } catch {
        onEvent({ type, data: e.data })
      }
    })
  }

  source.onerror = (e) => {
    onError?.(e)
  }

  return {
    close: () => {
      source.close()
    },
  }
}

export function getAnalysisStreamUrl(taskId: number): string {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api'
  return `${baseUrl}/analysis/${taskId}/stream`
}
