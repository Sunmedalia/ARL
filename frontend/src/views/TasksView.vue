<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import PageHeader from '../components/PageHeader.vue'
import { apiRequest, queryString } from '../api/client'
import { PlusOutlined, ReloadOutlined } from '@ant-design/icons-vue'

const router = useRouter(); const rows = ref<Record<string, any>[]>([]); const total = ref(0); const page = ref(1); const loading = ref(false); const open = ref(false); const saving = ref(false)
const filter = reactive({ name: '', status: '' })
const form = reactive({ name: '', target: '', domain_brute: true, domain_brute_type: 'test', port_scan: true, port_scan_type: 'test', site_identify: true, site_capture: false, service_detection: false, file_leak: false, nuclei_scan: false, web_info_hunter: false })
async function load() { loading.value = true; try { const data = await apiRequest<any>('/api/task/' + queryString({ page: page.value, size: 20, ...filter })); rows.value = data.items || []; total.value = data.total || 0 } catch (e) { message.error((e as Error).message) } finally { loading.value = false } }
async function createTask() { saving.value = true; try { await apiRequest('/api/task/', { method: 'POST', body: JSON.stringify(form) }); message.success('任务已下发'); open.value = false; await load() } catch (e) { message.error((e as Error).message) } finally { saving.value = false } }
const columns = [{ title: '状态', dataIndex: 'status', width: 110 }, { title: '任务名', dataIndex: 'name' }, { title: '目标', dataIndex: 'target' }, { title: '类型', dataIndex: 'type' }, { title: '开始时间', dataIndex: 'start_time' }, { title: '操作', key: 'action', width: 90 }]
onMounted(load)
</script>
<template>
  <section class="page">
    <PageHeader eyebrow="RECON / TASKS" title="侦察任务" description="下发资产发现任务并追踪域名、IP、站点与漏洞结果。">
      <a-button @click="load"><ReloadOutlined />刷新</a-button><a-button type="primary" @click="open = true"><PlusOutlined />下发任务</a-button>
    </PageHeader>
    <div class="data-panel"><div class="query-strip task-filters"><a-input v-model:value="filter.name" placeholder="任务名" allow-clear/><a-select v-model:value="filter.status" placeholder="全部状态" allow-clear :options="['waiting','done','error','stop'].map(value => ({value}))"/><a-button @click="page=1;load()">筛选</a-button><span><b>{{ total }}</b> 个任务</span></div>
      <a-table :columns="columns" :data-source="rows" :loading="loading" :pagination="false" row-key="_id" :scroll="{x:900}">
        <template #bodyCell="{ column, record }"><template v-if="column.key === 'action'"><a @click="router.push(`/tasks/${record._id}`)">详情</a></template><template v-else-if="column.dataIndex === 'status'"><a-tag :color="record.status === 'done' ? 'green' : record.status === 'error' ? 'red' : 'blue'">{{ record.status }}</a-tag></template></template>
      </a-table><a-pagination :current="page" :total="total" :page-size="20" @change="(n:number)=>{page=n;load()}"/></div>
    <a-drawer v-model:open="open" title="下发资产发现任务" width="min(640px, 94vw)">
      <a-form layout="vertical" @finish="createTask"><a-form-item label="任务名" required><a-input v-model:value="form.name" maxlength="120"/></a-form-item><a-form-item label="目标" required extra="支持域名、IP、CIDR；使用逗号或换行分隔。"><a-textarea v-model:value="form.target" :rows="5"/></a-form-item>
        <div class="form-grid"><a-form-item label="域名爆破"><a-switch v-model:checked="form.domain_brute"/></a-form-item><a-form-item label="爆破字典"><a-select v-model:value="form.domain_brute_type" :options="[{value:'test',label:'测试字典'},{value:'big',label:'大字典'}]"/></a-form-item><a-form-item label="端口扫描"><a-switch v-model:checked="form.port_scan"/></a-form-item><a-form-item label="端口范围"><a-select v-model:value="form.port_scan_type" :options="['test','top100','top1000','all'].map(value=>({value,label:value}))"/></a-form-item></div>
        <a-divider>站点与风险选项</a-divider><div class="switch-grid"><label><a-switch v-model:checked="form.site_identify"/>站点识别</label><label><a-switch v-model:checked="form.site_capture"/>站点截图</label><label><a-switch v-model:checked="form.service_detection"/>服务识别</label><label><a-switch v-model:checked="form.file_leak"/>文件泄漏</label><label><a-switch v-model:checked="form.nuclei_scan"/>Nuclei</label><label><a-switch v-model:checked="form.web_info_hunter"/>Web 信息猎手</label></div>
        <div class="drawer-actions"><a-button @click="open=false">取消</a-button><a-button type="primary" html-type="submit" :loading="saving">确认下发</a-button></div></a-form>
    </a-drawer>
  </section>
</template>
