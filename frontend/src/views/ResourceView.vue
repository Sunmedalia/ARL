<script setup lang="ts">
import { Button as _AButtonImpl, Input as _AInputImpl, Modal as _AModalImpl, Pagination as _APaginationImpl, Select as _ASelectImpl, Table as _ATableImpl, Tag as _ATagImpl } from 'ant-design-vue'
const AButton: any = _AButtonImpl
const AInput: any = _AInputImpl
const AModal: any = _AModalImpl
const APagination: any = _APaginationImpl
const ASelect: any = _ASelectImpl
const ATable: any = _ATableImpl
const ATag: any = _ATagImpl
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { message } from 'ant-design-vue'
import { Modal } from 'ant-design-vue'
import { DeleteOutlined, DownloadOutlined, PlusOutlined, ReloadOutlined, SaveOutlined, SearchOutlined } from '@ant-design/icons-vue'
import PageHeader from '../components/PageHeader.vue'
import { apiRequest, downloadRequest, queryString } from '../api/client'
import { resourceMap } from '../resources'

const props = defineProps<{ resourceKey: string }>()
const definition = computed(() => resourceMap[props.resourceKey])
const rows = ref<Record<string, unknown>[]>([]); const total = ref(0); const page = ref(1); const size = ref(20)
const search = ref(''); const loading = ref(false); let controller: AbortController | undefined
const selected = ref<string[]>([]); const filters = ref<Record<string, string | number>>({}); const tagOpen = ref(false); const tag = ref(''); const tagRecord = ref<Record<string, any>>()
function display(value: unknown) {
  if (value === null || value === undefined || value === '') return '—'
  if (Array.isArray(value)) return value.map((item) => typeof item === 'object' ? JSON.stringify(item) : item).join(', ')
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
}
async function load() {
  controller?.abort(); controller = new AbortController(); loading.value = true
  const filter = definition.value.searchKey ? { [definition.value.searchKey]: search.value, ...filters.value } : { ...filters.value }
  try {
    const data = await apiRequest<{ items: Record<string, unknown>[]; total: number }>(
      definition.value.endpoint + queryString({ page: page.value, size: size.value, ...filter }), {}, controller.signal,
    )
    rows.value = data.items || []; total.value = data.total || 0; selected.value = []
  } catch (error) { if ((error as Error).name !== 'AbortError') message.error((error as Error).message) }
  finally { loading.value = false }
}
function changePage(next: number, nextSize: number) { page.value = next; size.value = nextSize; load() }
function currentFilter() { return { ...(definition.value.searchKey ? {[definition.value.searchKey]:search.value} : {}), ...filters.value } }
async function exportRows() {
  if (!definition.value.exportEndpoint) return
  try { await downloadRequest(definition.value.exportEndpoint + queryString({...currentFilter(), size:100000}), `${definition.value.key}.txt`) }
  catch (error) { message.error((error as Error).message) }
}
function removeRows() {
  if (!selected.value.length || !definition.value.deleteEndpoint) return
  Modal.confirm({ title:`删除 ${selected.value.length} 条记录？`, content:'删除后无法恢复。', okType:'danger', async onOk(){ await apiRequest(definition.value.deleteEndpoint!,{method:'POST',body:JSON.stringify({_id:selected.value})}); message.success('已删除'); await load() } })
}
async function saveResultSet() {
  try { const data=await apiRequest<any>(definition.value.resultSetEndpoint! + queryString(currentFilter())); message.success(`结果集已保存：${data.result_set_id}（${data.result_total} 条）`) }
  catch(error){message.error((error as Error).message)}
}
function openTag(record:Record<string,any>){tagRecord.value=record;tag.value='';tagOpen.value=true}
async function addTag(){if(!tag.value.trim())return;await apiRequest(definition.value.tagEndpoints!.add,{method:'POST',body:JSON.stringify({_id:tagRecord.value?._id,tag:tag.value.trim()})});tagOpen.value=false;message.success('标签已添加');await load()}
async function removeTag(record:Record<string,any>, value:string){await apiRequest(definition.value.tagEndpoints!.remove,{method:'POST',body:JSON.stringify({_id:record._id,tag:value})});message.success('标签已移除');await load()}
function applyFilters(){page.value=1;load()}
function resetFilters(){search.value='';filters.value={};applyFilters()}
watch(() => props.resourceKey, () => { page.value = 1; search.value = ''; filters.value={}; load() })
onMounted(load); onUnmounted(() => controller?.abort())
</script>
<template>
  <section class="page">
    <PageHeader :eyebrow="definition.eyebrow" :title="definition.title" :description="definition.description || '检索完整数据集；导出由服务端按当前筛选条件生成。'">
      <a-button v-if="definition.resultSetEndpoint" @click="saveResultSet"><SaveOutlined />保存结果集</a-button>
      <a-button v-if="definition.deleteEndpoint" danger :disabled="!selected.length" @click="removeRows"><DeleteOutlined />删除 {{selected.length||''}}</a-button>
      <a-button v-if="definition.exportEndpoint" @click="exportRows"><DownloadOutlined />导出全部结果</a-button>
      <a-button @click="load"><ReloadOutlined />刷新</a-button>
    </PageHeader>
    <div class="data-panel">
      <div class="query-strip">
        <a-input v-model:value="search" :placeholder="`搜索${definition.title}`" allow-clear @press-enter="applyFilters"/>
        <template v-for="item in definition.filters" :key="item.key"><a-select v-if="item.options" v-model:value="filters[item.key]" allow-clear :placeholder="item.label" :options="item.options.map(value=>({value,label:value}))"/><a-input v-else v-model:value="filters[item.key]" allow-clear :placeholder="item.label" @press-enter="applyFilters"/></template>
        <a-button type="primary" @click="applyFilters"><SearchOutlined/>筛选</a-button><a-button @click="resetFilters">重置</a-button>
        <span><b>{{ total }}</b> 条记录</span>
      </div>
      <a-table :data-source="rows" :columns="[...definition.columns,...(definition.tagEndpoints?[{title:'操作',key:'action',width:80}]:[])]" :loading="loading" :pagination="false" row-key="_id" :scroll="{ x: 900 }" :row-selection="definition.deleteEndpoint?{selectedRowKeys:selected,onChange:(keys:(string|number)[])=>selected=keys.map(String)}:undefined">
        <template #bodyCell="{ column, record }"><template v-if="column.key==='action'"><a @click="openTag(record)"><PlusOutlined/> 标签</a></template><template v-else-if="column.dataIndex==='tag'&&definition.tagEndpoints"><a-tag v-for="value in (Array.isArray(record.tag)?record.tag:record.tag?[record.tag]:[])" :key="value" closable @close.prevent="removeTag(record,value)">{{value}}</a-tag><span v-if="!record.tag">—</span></template><span v-else class="cell-value">{{ display(record[column.dataIndex]) }}</span></template>
      </a-table>
      <a-pagination :current="page" :page-size="size" :total="total" show-size-changer :show-total="(n:number) => `共 ${n} 条`" @change="changePage" />
    </div>
    <a-modal v-model:open="tagOpen" title="添加站点标签" ok-text="添加" @ok="addTag"><a-input v-model:value="tag" maxlength="40" placeholder="输入标签" @press-enter="addTag"/></a-modal>
  </section>
</template>
