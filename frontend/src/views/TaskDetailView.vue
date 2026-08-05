<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import PageHeader from '../components/PageHeader.vue'
import { apiRequest, queryString } from '../api/client'

const route = useRoute(); const router = useRouter(); const task = ref<Record<string, any>>({}); const loading = ref(true)
const resultTypes = [
  ['domain','域名'], ['ip','IP'], ['site','站点'], ['service','服务'], ['url','URL'], ['vuln','漏洞'], ['nuclei_result','Nuclei'], ['fileleak','文件泄漏'], ['wih','信息猎手'],
]
const active = ref('domain'); const rows = ref<Record<string, any>[]>([]); const resultLoading = ref(false)
async function loadResults() { resultLoading.value = true; try { const data = await apiRequest<any>(`/api/${active.value}/` + queryString({task_id: route.params.id, page: 1, size: 50})); rows.value = data.items || [] } catch (e) { message.error((e as Error).message) } finally { resultLoading.value = false } }
onMounted(async () => { try { const data = await apiRequest<any>('/api/task/' + queryString({_id: route.params.id, size: 1})); task.value = data.items?.[0] || {}; await loadResults() } finally { loading.value = false } })
</script>
<template>
  <section class="page">
    <PageHeader eyebrow="RECON / TASK DETAIL" :title="task.name || '任务详情'" :description="task.target"><a-button @click="router.back()">返回</a-button></PageHeader>
    <a-skeleton v-if="loading" active/>
    <template v-else><div class="task-summary data-panel"><div><span>状态</span><a-tag color="blue">{{ task.status }}</a-tag></div><div><span>类型</span><strong>{{ task.type || '—' }}</strong></div><div><span>开始</span><strong>{{ task.start_time || '—' }}</strong></div><div><span>结束</span><strong>{{ task.end_time || '—' }}</strong></div></div>
      <div class="data-panel result-panel"><a-tabs v-model:active-key="active" @change="loadResults"><a-tab-pane v-for="([key,label]) in resultTypes" :key="key" :tab="label"/></a-tabs><a-table :data-source="rows" :loading="resultLoading" :pagination="false" row-key="_id" :scroll="{x:900}"><a-table-column title="记录" key="record"><template #default="{record}"><code>{{ JSON.stringify(record, null, 2) }}</code></template></a-table-column></a-table></div>
    </template>
  </section>
</template>
