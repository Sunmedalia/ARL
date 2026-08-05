<script setup lang="ts">
import { Button as _AButtonImpl, Form as _AFormImpl, FormItem as _AFormItemImpl, Input as _AInputImpl, Modal as _AModalImpl, Pagination as _APaginationImpl, Select as _ASelectImpl, Table as _ATableImpl, Textarea as _ATextareaImpl } from 'ant-design-vue'
const AButton: any = _AButtonImpl
const AForm: any = _AFormImpl
const AFormItem: any = _AFormItemImpl
const AInput: any = _AInputImpl
const AModal: any = _AModalImpl
const APagination: any = _APaginationImpl
const ASelect: any = _ASelectImpl
const ATable: any = _ATableImpl
const ATextarea: any = _ATextareaImpl
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { message, Modal } from 'ant-design-vue'
import PageHeader from '../components/PageHeader.vue'
import { apiRequest } from '../api/client'
import { usePagedList } from '../composables/usePagedList'
import { DeleteOutlined, EditOutlined, PauseOutlined, PlayCircleOutlined, PlusOutlined } from '@ant-design/icons-vue'
const props=defineProps<{mode:'tasks'|'monitors'}>();const endpoint=computed(()=>props.mode==='tasks'?'/api/github_task/':'/api/github_scheduler/');let list=usePagedList(endpoint.value,{name:'',status:''});const selected=ref<string[]>([]);const open=ref(false);const editId=ref('');const saving=ref(false);const form=reactive({name:'',keyword:'',cron:'0 */8 * * *'})
const title=computed(()=>props.mode==='tasks'?'GitHub 搜索任务':'GitHub 监控');const eyebrow=computed(()=>props.mode==='tasks'?'GITHUB / TASKS':'GITHUB / MONITOR')
function show(record?:any){editId.value=record?._id||'';Object.assign(form,{name:record?.name||'',keyword:record?.keyword||'',cron:record?.cron||'0 */8 * * *'});open.value=true}
async function save(){if(!form.name.trim()||!form.keyword.trim())return message.error('请填写名称和关键词');if(props.mode==='monitors'&&!form.cron.trim())return message.error('请输入 Cron 表达式');saving.value=true;try{const path=props.mode==='monitors'&&editId.value?'/api/github_scheduler/update/':endpoint.value;const body=props.mode==='tasks'?{name:form.name,keyword:form.keyword}:{...form,...(editId.value?{_id:editId.value}:{})};await apiRequest(path,{method:'POST',body:JSON.stringify(body)});message.success(editId.value?'监控已更新':'任务已创建');open.value=false;await list.search()}catch(e){message.error((e as Error).message)}finally{saving.value=false}}
async function operate(action:'stop'|'recover'){const path=props.mode==='tasks'?'/api/github_task/stop/':`/api/github_scheduler/${action}/`;await apiRequest(path,{method:'POST',body:JSON.stringify({_id:selected.value})});message.success(action==='stop'?'已停止':'已恢复');selected.value=[];await list.load()}
function remove(){Modal.confirm({title:`删除 ${selected.value.length} 项？`,okType:'danger',async onOk(){await apiRequest(props.mode==='tasks'?'/api/github_task/delete/':'/api/github_scheduler/delete/',{method:'POST',body:JSON.stringify({_id:selected.value})});selected.value=[];await list.load()}})}
watch(()=>props.mode,()=>location.reload());onMounted(list.load)
</script>
<template><section class="page"><PageHeader :eyebrow="eyebrow" :title="title" :description="mode==='tasks'?'按关键词执行一次性 GitHub 泄漏检索并控制任务生命周期。':'维护可编辑、可启停的周期 GitHub 泄漏监控。'"><a-button :disabled="!selected.length" @click="operate('stop')"><PauseOutlined/>停止</a-button><a-button v-if="mode==='monitors'" :disabled="!selected.length" @click="operate('recover')"><PlayCircleOutlined/>恢复</a-button><a-button danger :disabled="!selected.length" @click="remove"><DeleteOutlined/>删除</a-button><a-button type="primary" @click="show()"><PlusOutlined/>{{mode==='tasks'?'新建搜索':'新建监控'}}</a-button></PageHeader><div class="data-panel"><div class="query-strip"><a-input v-model:value="list.filters.name" placeholder="名称"/><a-select v-model:value="list.filters.status" allow-clear placeholder="全部状态" :options="['waiting','running','done','error','stop'].map(value=>({value}))"/><a-button @click="list.search">筛选</a-button><span><b>{{list.total}}</b> 项</span></div><a-table :data-source="list.rows" :loading="list.loading" row-key="_id" :pagination="false" :row-selection="{selectedRowKeys:selected,onChange:(keys:(string|number)[])=>selected=keys.map(String)}" :columns="[{title:'名称',dataIndex:'name'},{title:'关键词',dataIndex:'keyword'},{title:'Cron',dataIndex:'cron'},{title:'状态',dataIndex:'status'},{title:'开始 / 下次执行',key:'time'},{title:'操作',key:'action',width:80}]"><template #bodyCell="{column,record}"><span v-if="column.key==='time'">{{record.start_time||record.next_run_date||'—'}}</span><a v-if="column.key==='action'&&mode==='monitors'" @click="show(record)"><EditOutlined/>编辑</a></template></a-table><a-pagination :current="list.page" :page-size="list.size" :total="list.total" @change="list.changePage"/></div><a-modal v-model:open="open" :title="editId?'编辑 GitHub 监控':`新建${title}`" ok-text="保存" :confirm-loading="saving" @ok="save"><a-form layout="vertical"><a-form-item label="名称" required><a-input v-model:value="form.name"/></a-form-item><a-form-item label="关键词" required><a-textarea v-model:value="form.keyword" :rows="4"/></a-form-item><a-form-item v-if="mode==='monitors'" label="Cron" required><a-input v-model:value="form.cron"/></a-form-item></a-form></a-modal></section></template>
