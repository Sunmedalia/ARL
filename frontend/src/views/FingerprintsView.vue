<script setup lang="ts">
import { Button as _AButtonImpl, Form as _AFormImpl, FormItem as _AFormItemImpl, Input as _AInputImpl, Modal as _AModalImpl, Pagination as _APaginationImpl, Table as _ATableImpl, Textarea as _ATextareaImpl } from 'ant-design-vue'
const AButton: any = _AButtonImpl
const AForm: any = _AFormImpl
const AFormItem: any = _AFormItemImpl
const AInput: any = _AInputImpl
const AModal: any = _AModalImpl
const APagination: any = _APaginationImpl
const ATable: any = _ATableImpl
const ATextarea: any = _ATextareaImpl
import { onMounted, reactive, ref } from 'vue'
import { message, Modal } from 'ant-design-vue'
import PageHeader from '../components/PageHeader.vue'
import { apiRequest, downloadRequest } from '../api/client'
import { usePagedList } from '../composables/usePagedList'
import { DeleteOutlined, DownloadOutlined, PlusOutlined, UploadOutlined } from '@ant-design/icons-vue'
const list=usePagedList('/api/fingerprint/',{name:''});const selected=ref<string[]>([]);const open=ref(false);const saving=ref(false);const file=ref<File>();const form=reactive({name:'',human_rule:''})
async function create(){if(!form.name.trim()||!form.human_rule.trim())return message.error('请填写名称和规则');saving.value=true;try{await apiRequest('/api/fingerprint/',{method:'POST',body:JSON.stringify(form)});message.success('指纹已添加');open.value=false;Object.assign(form,{name:'',human_rule:''});await list.search()}catch(e){message.error((e as Error).message)}finally{saving.value=false}}
function remove(){Modal.confirm({title:`删除 ${selected.value.length} 条指纹？`,okType:'danger',async onOk(){await apiRequest('/api/fingerprint/delete/',{method:'POST',body:JSON.stringify({_id:selected.value})});selected.value=[];await list.load()}})}
async function upload(){if(!file.value)return;const data=new FormData();data.append('file',file.value);try{await apiRequest('/api/fingerprint/upload/',{method:'POST',body:data});message.success('指纹文件已导入');file.value=undefined;await list.load()}catch(e){message.error((e as Error).message)}}
onMounted(list.load)
</script>
<template><section class="page"><PageHeader eyebrow="INTEL / FINGERPRINT" title="指纹规则" description="新增、批量删除、导入和完整导出站点指纹表达式。"><label class="file-button"><input type="file" accept=".yml,.yaml,.json" @change="file=($event.target as HTMLInputElement).files?.[0]"/><UploadOutlined/>{{file?.name||'选择导入文件'}}</label><a-button v-if="file" @click="upload">确认导入</a-button><a-button @click="downloadRequest('/api/fingerprint/export/','fingerprints.yml')"><DownloadOutlined/>导出全部</a-button><a-button danger :disabled="!selected.length" @click="remove"><DeleteOutlined/>删除</a-button><a-button type="primary" @click="open=true"><PlusOutlined/>新增指纹</a-button></PageHeader><div class="data-panel"><div class="query-strip"><a-input v-model:value="list.filters.name" placeholder="指纹名称" @press-enter="list.search"/><a-button @click="list.search">筛选</a-button><span><b>{{list.total}}</b> 条规则</span></div><a-table :data-source="list.rows" row-key="_id" :loading="list.loading" :pagination="false" :row-selection="{selectedRowKeys:selected,onChange:(keys:(string|number)[])=>selected=keys.map(String)}" :columns="[{title:'名称',dataIndex:'name'},{title:'规则',dataIndex:'human_rule'},{title:'更新时间',dataIndex:'update_date'}]"/><a-pagination :current="list.page" :page-size="list.size" :total="list.total" @change="list.changePage"/></div><a-modal v-model:open="open" title="新增指纹规则" ok-text="保存" :confirm-loading="saving" @ok="create"><a-form layout="vertical"><a-form-item label="名称" required><a-input v-model:value="form.name"/></a-form-item><a-form-item label="人类可读规则" required><a-textarea v-model:value="form.human_rule" :rows="7" placeholder="例如：title='Example' && body='keyword'"/></a-form-item></a-form></a-modal></section></template>
