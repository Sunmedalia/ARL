import { reactive, ref } from 'vue'
import { message } from 'ant-design-vue'
import { apiRequest, queryString } from '../api/client'

export function usePagedList(endpoint: string, initialFilters: Record<string, unknown> = {}) {
  const rows = ref<Record<string, any>[]>([])
  const total = ref(0); const page = ref(1); const size = ref(20); const loading = ref(false)
  const filters = reactive<Record<string, any>>({...initialFilters})
  async function load(extra: Record<string, unknown> = {}) {
    loading.value = true
    try {
      const data = await apiRequest<any>(endpoint + queryString({page:page.value,size:size.value,...filters,...extra}))
      rows.value=data.items||[];total.value=data.total||0
    } catch(error) { message.error((error as Error).message) }
    finally { loading.value=false }
  }
  function search(){page.value=1;return load()}
  function changePage(next:number,nextSize:number){page.value=next;size.value=nextSize;return load()}
  return {rows,total,page,size,loading,filters,load,search,changePage}
}
