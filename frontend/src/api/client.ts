export interface ApiEnvelope<T> { code: number; message: string; data?: T; items?: unknown[] }

let csrfToken = ''
export const setCsrfToken = (token: string) => { csrfToken = token }
export const getCsrfToken = () => csrfToken

export class ApiError extends Error {
  constructor(public status: number, message: string, public payload?: unknown) { super(message) }
}

export async function apiRequest<T>(path: string, init: RequestInit = {}, signal?: AbortSignal): Promise<T> {
  const method = (init.method || 'GET').toUpperCase()
  const headers = new Headers(init.headers)
  headers.set('Accept', 'application/json')
  if (init.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json')
  if (csrfToken) headers.set('X-CSRF-Token', csrfToken)
  const response = await fetch(path, { ...init, headers, credentials: 'same-origin', signal })
  const payload = await response.json().catch(() => ({ code: response.status, message: response.statusText }))
  if (response.status === 401 || payload.code === 401) {
    if (!location.pathname.endsWith('/login')) location.assign('/next/login')
    throw new ApiError(401, payload.message || '登录已失效', payload)
  }
  if (!response.ok || (payload.code && payload.code !== 200)) {
    throw new ApiError(response.status, payload.message || '请求失败', payload)
  }
  return (payload.data ?? payload) as T
}

export function queryString(values: Record<string, unknown>) {
  const query = new URLSearchParams()
  Object.entries(values).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') query.set(key, String(value))
  })
  const value = query.toString()
  return value ? `?${value}` : ''
}

export interface SseEvent<T = Record<string, unknown>> { event: string; data: T }

export async function postSse(
  path: string,
  body: unknown,
  onEvent: (event: SseEvent) => void,
  signal?: AbortSignal,
) {
  const response = await fetch(path, {
    method: 'POST', credentials: 'same-origin', signal,
    headers: { 'Content-Type': 'application/json', Accept: 'text/event-stream', 'X-CSRF-Token': csrfToken },
    body: JSON.stringify(body),
  })
  if (!response.ok || !response.body) {
    const payload = await response.json().catch(() => ({}))
    throw new ApiError(response.status, payload.message || '无法建立 AI 流')
  }
  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  while (true) {
    const { done, value } = await reader.read()
    buffer += decoder.decode(value || new Uint8Array(), { stream: !done })
    const blocks = buffer.split(/\r?\n\r?\n/)
    buffer = blocks.pop() || ''
    blocks.forEach((block) => {
      let event = 'message'; const data: string[] = []
      block.split(/\r?\n/).forEach((line) => {
        if (line.startsWith('event:')) event = line.slice(6).trim()
        if (line.startsWith('data:')) data.push(line.slice(5).trimStart())
      })
      if (data.length) onEvent({ event, data: JSON.parse(data.join('\n')) })
    })
    if (done) break
  }
}
