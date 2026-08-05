<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { message } from 'ant-design-vue'
import { DownloadOutlined, ReloadOutlined, SearchOutlined } from '@ant-design/icons-vue'
import PageHeader from '../components/PageHeader.vue'
import { apiRequest, queryString } from '../api/client'
import { resourceMap } from '../resources'

const props = defineProps<{ resourceKey: string }>()
const definition = computed(() => resourceMap[props.resourceKey])
const rows = ref<Record<string, unknown>[]>([]); const total = ref(0); const page = ref(1); const size = ref(20)
const search = ref(''); const loading = ref(false); let controller: AbortController | undefined
function display(value: unknown) {
  if (value === null || value === undefined || value === '') return '—'
  if (Array.isArray(value)) return value.map((item) => typeof item === 'object' ? JSON.stringify(item) : item).join(', ')
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
}
async function load() {
  controller?.abort(); controller = new AbortController(); loading.value = true
  const filter = definition.value.searchKey ? { [definition.value.searchKey]: search.value } : {}
  try {
    const data = await apiRequest<{ items: Record<string, unknown>[]; total: number }>(
      definition.value.endpoint + queryString({ page: page.value, size: size.value, ...filter }), {}, controller.signal,
    )
    rows.value = data.items || []; total.value = data.total || 0
  } catch (error) { if ((error as Error).name !== 'AbortError') message.error((error as Error).message) }
  finally { loading.value = false }
}
function changePage(next: number, nextSize: number) { page.value = next; size.value = nextSize; load() }
function exportRows() {
  const content = rows.value.map((row) => definition.value.columns.map((col) => display(row[col.dataIndex])).join('\t')).join('\n')
  const url = URL.createObjectURL(new Blob([content], { type: 'text/tab-separated-values' }))
  const link = document.createElement('a'); link.href = url; link.download = `${definition.value.key}.tsv`; link.click(); URL.revokeObjectURL(url)
}
watch(() => props.resourceKey, () => { page.value = 1; search.value = ''; load() })
onMounted(load); onUnmounted(() => controller?.abort())
</script>
<template>
  <section class="page">
    <PageHeader :eyebrow="definition.eyebrow" :title="definition.title" description="在受控查询范围内检索、筛选并导出当前数据。">
      <a-button @click="exportRows"><DownloadOutlined />导出当前页</a-button>
      <a-button @click="load"><ReloadOutlined />刷新</a-button>
    </PageHeader>
    <div class="data-panel">
      <div class="query-strip">
        <a-input-search v-model:value="search" :placeholder="`搜索${definition.title}`" allow-clear @search="page = 1; load()"><template #enterButton><SearchOutlined /></template></a-input-search>
        <span><b>{{ total }}</b> 条记录</span>
      </div>
      <a-table :data-source="rows" :columns="definition.columns" :loading="loading" :pagination="false" row-key="_id" :scroll="{ x: 900 }">
        <template #bodyCell="{ column, record }"><span class="cell-value">{{ display(record[column.dataIndex]) }}</span></template>
      </a-table>
      <a-pagination :current="page" :page-size="size" :total="total" show-size-changer :show-total="(n:number) => `共 ${n} 条`" @change="changePage" />
    </div>
  </section>
</template>
