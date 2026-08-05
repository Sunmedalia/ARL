<script setup lang="ts">
import { Button as _AButtonImpl, Drawer as _ADrawerImpl, Form as _AFormImpl, FormItem as _AFormItemImpl, Input as _AInputImpl, Pagination as _APaginationImpl, Radio as _ARadioImpl, RadioGroup as _ARadioGroupImpl, Table as _ATableImpl, Textarea as _ATextareaImpl } from 'ant-design-vue'
const AButton: any = _AButtonImpl
const ADrawer: any = _ADrawerImpl
const AForm: any = _AFormImpl
const AFormItem: any = _AFormItemImpl
const AInput: any = _AInputImpl
const APagination: any = _APaginationImpl
const ARadio: any = _ARadioImpl
const ARadioGroup: any = _ARadioGroupImpl
const ATable: any = _ATableImpl
const ATextarea: any = _ATextareaImpl
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import PageHeader from '../components/PageHeader.vue'
import { apiRequest } from '../api/client'
import { usePagedList } from '../composables/usePagedList'
import { DeleteOutlined, PlusOutlined, ReloadOutlined } from '@ant-design/icons-vue'

const router=useRouter();const list=usePagedList('/api/asset_scope/',{name:''});const open=ref(false);const saving=ref(false);const selected=ref<string[]>([])
const form=reactive({name:'',scope_type:'domain',scope:'',black_scope:''})
async function create(){if(!form.name.trim()||!form.scope.trim())return message.error('请填写名称和资产范围');saving.value=true;try{await apiRequest('/api/asset_scope/',{method:'POST',body:JSON.stringify(form)});message.success('资产组已创建');open.value=false;Object.assign(form,{name:'',scope_type:'domain',scope:'',black_scope:''});await list.search()}catch(e){message.error((e as Error).message)}finally{saving.value=false}}
function remove(){if(!selected.value.length)return;Modal.confirm({title:`删除 ${selected.value.length} 个资产组？`,content:'资产组及其关联资产将被删除。',okType:'danger',async onOk(){await apiRequest('/api/asset_scope/delete/',{method:'POST',body:JSON.stringify({scope_id:selected.value})});selected.value=[];message.success('资产组已删除');await list.load()}})}
onMounted(list.load)
</script>
<template><section class="page"><PageHeader eyebrow="SCOPE / GROUPS" title="资产组" description="维护授权资产边界，并进入资产组查看已同步的域名、IP、站点与信息猎手结果。"><a-button @click="list.load"><ReloadOutlined/>刷新</a-button><a-button danger :disabled="!selected.length" @click="remove"><DeleteOutlined/>删除</a-button><a-button type="primary" @click="open=true"><PlusOutlined/>新建资产组</a-button></PageHeader>
<div class="data-panel"><div class="query-strip"><a-input v-model:value="list.filters.name" placeholder="资产组名称" allow-clear @press-enter="list.search"/><a-button type="primary" @click="list.search">筛选</a-button><span><b>{{list.total}}</b> 个资产组</span></div><a-table :data-source="list.rows" :loading="list.loading" row-key="_id" :pagination="false" :row-selection="{selectedRowKeys:selected,onChange:(keys:(string|number)[])=>selected=keys.map(String)}" :columns="[{title:'名称',dataIndex:'name'},{title:'类型',dataIndex:'scope_type',width:100},{title:'资产范围',dataIndex:'scope'},{title:'黑名单',dataIndex:'black_scope'},{title:'操作',key:'action',width:90}]"><template #bodyCell="{column,record}"><a v-if="column.key==='action'" @click="router.push(`/groups/${record._id}`)">管理资产</a></template></a-table><a-pagination :current="list.page" :page-size="list.size" :total="list.total" show-size-changer @change="list.changePage"/></div>
<a-drawer v-model:open="open" title="新建资产组" width="min(600px,94vw)"><a-form layout="vertical" @finish="create"><a-form-item label="名称" required><a-input v-model:value="form.name"/></a-form-item><a-form-item label="类型" required><a-radio-group v-model:value="form.scope_type"><a-radio value="domain">域名</a-radio><a-radio value="ip">IP / CIDR</a-radio></a-radio-group></a-form-item><a-form-item label="资产范围" required extra="逗号、空格或换行分隔"><a-textarea v-model:value="form.scope" :rows="7"/></a-form-item><a-form-item label="黑名单"><a-textarea v-model:value="form.black_scope" :rows="4"/></a-form-item><div class="drawer-actions"><a-button @click="open=false">取消</a-button><a-button type="primary" html-type="submit" :loading="saving">创建</a-button></div></a-form></a-drawer></section></template>
