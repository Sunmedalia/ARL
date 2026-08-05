import { describe, expect, it, vi } from 'vitest'
import { postSse, queryString, setCsrfToken } from './client'

describe('API client', () => {
  it('omits empty query parameters', () => {
    expect(queryString({ page: 2, name: '', status: null })).toBe('?page=2')
  })

  it('parses segmented SSE responses and sends CSRF', async () => {
    const encoder = new TextEncoder()
    const stream = new ReadableStream({
      start(controller) {
        controller.enqueue(encoder.encode('event: text_delta\ndata: {"text":"资'))
        controller.enqueue(encoder.encode('产"}\n\nevent: done\ndata: {}\n\n'))
        controller.close()
      },
    })
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(stream, { status: 200, headers: { 'Content-Type': 'text/event-stream' } }),
    )
    setCsrfToken('csrf')
    const events: string[] = []
    await postSse('/api/ai/chat/stream', {}, (event) => events.push(event.event))
    expect(events).toEqual(['text_delta', 'done'])
    expect(new Headers(fetchMock.mock.calls[0][1]?.headers).get('X-CSRF-Token')).toBe('csrf')
    fetchMock.mockRestore()
  })
})
