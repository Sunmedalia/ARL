<script setup lang="ts">
import { Button as _AButtonImpl, Input as _AInputImpl, Pagination as _APaginationImpl, Select as _ASelectImpl, Table as _ATableImpl } from 'ant-design-vue'
const AButton: any = _AButtonImpl
const AInput: any = _AInputImpl
const APagination: any = _APaginationImpl
const ASelect: any = _ASelectImpl
const ATable: any = _ATableImpl
import { onMounted, reactive, ref } from 'vue'
import { message, Modal } from 'ant-design-vue'
import PageHeader from '../components/PageHeader.vue'
import { apiRequest } from '../api/client'
import { usePagedList } from '../composables/usePagedList'
import { DeleteOutlined, ReloadOutlined } from '@ant-design/icons-vue'
const list=usePagedList('/api/poc/',{plugin_name:'',app_name:'',plugin_type:''})
async function sync(){await apiRequest('/api/poc/sync/');message.success('PoC 数据已同步');await list.load()}
function remove(){Modal.confirm({title:'清空全部 PoC 与爆破插件？',content:'可以随后通过“同步插件”从内置清单重新导入。',okType:'danger',async onOk(){await apiRequest('/api/poc/delete/');message.success('插件数据已清空');await list.load()}})}
onMounted(list.load)
</script>
<template><section class="page"><PageHeader eyebrow="INTEL / PLUGINS" title="PoC 与爆破插件" description="从内置 NPoC 清单同步插件，按应用和类型筛选；清空后可随时重新同步。"><a-button @click="sync"><ReloadOutlined/>同步插件</a-button><a-button danger @click="remove"><DeleteOutlined/>清空全部</a-button></PageHeader><div class="data-panel"><div class="query-strip"><a-input v-model:value="list.filters.plugin_name" placeholder="插件 ID"/><a-input v-model:value="list.filters.app_name" placeholder="应用"/><a-select v-model:value="list.filters.plugin_type" allow-clear placeholder="全部类型" :options="['poc','brute'].map(value=>({value}))"/><a-button @click="list.search">筛选</a-button><span><b>{{list.total}}</b> 个插件</span></div><a-table :data-source="list.rows" :loading="list.loading" row-key="plugin_name" :pagination="false" :columns="[{title:'插件 ID',dataIndex:'plugin_name'},{title:'应用',dataIndex:'app_name'},{title:'漏洞',dataIndex:'vul_name'},{title:'协议',dataIndex:'scheme'},{title:'类型',dataIndex:'plugin_type'},{title:'分类',dataIndex:'category'}]"/><a-pagination :current="list.page" :page-size="list.size" :total="list.total" @change="list.changePage"/></div></section></template>
