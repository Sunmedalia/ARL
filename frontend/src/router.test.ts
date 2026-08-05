import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory } from 'vue-router'
import { createArlRouter, safeRedirect } from './router'

const session = (status = 200) => new Response(
  JSON.stringify(status === 200 ? {code:200,data:{username:'admin',csrf_token:'token',ai_granted:false,session_expires_at:'later'}} : {code:401,message:'unauthorized'}),
  {status,headers:{'Content-Type':'application/json'}},
)

describe('authentication routing', () => {
  beforeEach(() => { setActivePinia(createPinia()); vi.restoreAllMocks() })

  it('waits for session initialization and preserves the requested URL', async () => {
    vi.spyOn(globalThis,'fetch').mockResolvedValue(session(401))
    const router=createArlRouter(createMemoryHistory())
    await router.push('/tasks?status=running');await router.isReady()
    expect(router.currentRoute.value.path).toBe('/login')
    expect(router.currentRoute.value.query.redirect).toBe('/tasks?status=running')
  })

  it('returns an authenticated operator from login to the original page', async () => {
    const fetchMock=vi.spyOn(globalThis,'fetch').mockResolvedValue(session())
    const router=createArlRouter(createMemoryHistory())
    await router.push('/login?redirect=/tasks');await router.isReady()
    expect(router.currentRoute.value.fullPath).toBe('/tasks')
    await router.push('/settings')
    expect(fetchMock).toHaveBeenCalledTimes(1)
  })

  it('rejects external and recursive redirect values', () => {
    expect(safeRedirect('//example.org')).toBe('')
    expect(safeRedirect('/login?redirect=/tasks')).toBe('')
    expect(safeRedirect('/tasks/123')).toBe('/tasks/123')
  })
})
