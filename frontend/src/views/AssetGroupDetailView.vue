<script setup lang="ts">
import { Button as _AButtonImpl, InputSearch as _AInputSearchImpl, Modal as _AModalImpl, Pagination as _APaginationImpl, TabPane as _ATabPaneImpl, Table as _ATableImpl, Tabs as _ATabsImpl, Textarea as _ATextareaImpl } from 'ant-design-vue'
const AButton: any = _AButtonImpl
const AInputSearch: any = _AInputSearchImpl
const AModal: any = _AModalImpl
const APagination: any = _APaginationImpl
const ATabPane: any = _ATabPaneImpl
const ATable: any = _ATableImpl
const ATabs: any = _ATabsImpl
const ATextarea: any = _ATextareaImpl
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import PageHeader from '../components/PageHeader.vue'
import { apiRequest, downloadRequest, queryString } from '../api/client'
import { DeleteOutlined, DownloadOutlined, PlusOutlined } from '@ant-design/icons-vue'
const route=useRoute();const router=useRouter();const id=String(route.params.id);const group=ref<any>({});const active=ref('asset_domain');const rows=ref<any[]>([]);const total=ref(0);const page=ref(1);const size=ref(20);const loading=ref(false);const selected=ref<string[]>([]);const search=ref('');const scopeOpen=ref(false);const scopeText=ref('')
const types:any={asset_domain:{label:'域名',field:'domain',export:'/api/asset_domain/export/',del:'/api/asset_domain/delete/',columns:[['域名','domain'],['类型','type'],['解析地址','ips'],['更新时间','update_date']]},asset_ip:{label:'IP',field:'ip',export:'/api/asset_ip/export/',del:'/api/asset_ip/delete/',columns:[['IP','ip'],['类型','ip_type'],['端口','port_info'],['更新时间','update_date']]},asset_site:{label:'站点',field:'site',export:'/api/asset_site/export/',del:'/api/asset_site/delete/',result:'/api/asset_site/save_result_set/',columns:[['站点','site'],['标题','title'],['状态','status'],['标签','tag']]},asset_wih:{label:'信息猎手',field:'content',export:'/api/asset_wih/export/',del:'/api/asset_wih/delete/',columns:[['内容','content'],['类型','record_type'],['来源','source'],['更新时间','update_date']]}}
const current=computed(()=>types[active.value])
async function loadGroup(){const data=await apiRequest<any>('/api/asset_scope/'+queryString({_id:id,size:1}));group.value=data.items?.[0]||{}}
async function load(){loading.value=true;try{const data=await apiRequest<any>(`/api/${active.value}/`+queryString({scope_id:id,[current.value.field]:search.value,page:page.value,size:size.value}));rows.value=data.items||[];total.value=data.total||0;selected.value=[]}catch(e){message.error((e as Error).message)}finally{loading.value=false}}
async function exportAll(){await downloadRequest(current.value.export+queryString({scope_id:id,[current.value.field]:search.value,size:100000}),`${active.value}.txt`)}
function remove(){Modal.confirm({title:`删除 ${selected.value.length} 条资产？`,okType:'danger',async onOk(){await apiRequest(current.value.del,{method:'POST',body:JSON.stringify({_id:selected.value})});await load()}})}
async function saveResult(){const data=await apiRequest<any>(current.value.result+queryString({scope_id:id,[current.value.field]:search.value}));message.success(`结果集 ${data.result_set_id} 已保存，共 ${data.result_total} 条`)}
async function addScope(){await apiRequest('/api/asset_scope/add/',{method:'POST',body:JSON.stringify({scope_id:id,scope:scopeText.value})});scopeOpen.value=false;scopeText.value='';message.success('范围已追加');await loadGroup()}
watch(active,()=>{page.value=1;search.value='';load()});onMounted(async()=>{await loadGroup();await load()})
</script>
<template><section class="page"><PageHeader eyebrow="SCOPE / ASSETS" :title="group.name||'资产组详情'" :description="group.scope"><a-button @click="router.back()">返回</a-button><a-button @click="scopeOpen=true"><PlusOutlined/>追加范围</a-button><a-button v-if="current.result" @click="saveResult">保存结果集</a-button><a-button @click="exportAll"><DownloadOutlined/>导出全部</a-button><a-button danger :disabled="!selected.length" @click="remove"><DeleteOutlined/>删除</a-button></PageHeader><div class="data-panel result-panel"><a-tabs v-model:active-key="active"><a-tab-pane v-for="(type,key) in types" :key="key" :tab="type.label"/></a-tabs><div class="query-strip"><a-input-search v-model:value="search" :placeholder="`搜索${current.label}`" @search="page=1;load()"/><span><b>{{total}}</b> 条</span></div><a-table :data-source="rows" row-key="_id" :loading="loading" :pagination="false" :row-selection="{selectedRowKeys:selected,onChange:(keys:(string|number)[])=>selected=keys.map(String)}" :columns="current.columns.map((x:any)=>({title:x[0],dataIndex:x[1]}))"><template #bodyCell="{column,record}"><span class="cell-value">{{typeof record[column.dataIndex]==='object'?JSON.stringify(record[column.dataIndex]):record[column.dataIndex]||'—'}}</span></template></a-table><a-pagination :current="page" :page-size="size" :total="total" show-size-changer @change="(p:number,s:number)=>{page=p;size=s;load()}"/></div><a-modal v-model:open="scopeOpen" title="追加资产范围" @ok="addScope"><a-textarea v-model:value="scopeText" :rows="6" placeholder="逗号、空格或换行分隔"/></a-modal></section></template>
