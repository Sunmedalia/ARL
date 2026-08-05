export interface ResourceDefinition {
  key: string; title: string; eyebrow: string; endpoint: string; searchKey?: string
  description?: string; exportEndpoint?: string; deleteEndpoint?: string; resultSetEndpoint?: string
  tagEndpoints?: { add: string; remove: string }
  filters?: { key: string; label: string; type?: 'text' | 'number'; options?: string[] }[]
  columns: { title: string; dataIndex: string; width?: number }[]
}

export const resources: ResourceDefinition[] = [
  { key: 'domains', title: '域名资产', eyebrow: 'ASSET / DOMAIN', endpoint: '/api/domain/', searchKey: 'domain', exportEndpoint: '/api/domain/export/', deleteEndpoint: '/api/domain/delete/', filters: [{key:'task_id',label:'任务 ID'},{key:'type',label:'记录类型'}], columns: [
    { title: '域名', dataIndex: 'domain' }, { title: '记录类型', dataIndex: 'type' }, { title: '解析地址', dataIndex: 'ips' }, { title: '来源', dataIndex: 'source' }, { title: '任务', dataIndex: 'task_id' }] },
  { key: 'ips', title: 'IP 资产', eyebrow: 'ASSET / IP', endpoint: '/api/ip/', searchKey: 'ip', exportEndpoint: '/api/ip/export/', deleteEndpoint: '/api/ip/delete/', filters: [{key:'task_id',label:'任务 ID'},{key:'ip_type',label:'IP 类型',options:['PUBLIC','PRIVATE']}], columns: [
    { title: 'IP', dataIndex: 'ip' }, { title: '类型', dataIndex: 'ip_type' }, { title: '端口', dataIndex: 'port_info' }, { title: '操作系统', dataIndex: 'os_info' }, { title: '任务', dataIndex: 'task_id' }] },
  { key: 'sites', title: '站点资产', eyebrow: 'ASSET / SITE', endpoint: '/api/site/', searchKey: 'site', exportEndpoint: '/api/site/export/', deleteEndpoint: '/api/site/delete/', resultSetEndpoint: '/api/site/save_result_set/', tagEndpoints: {add:'/api/site/add_tag/',remove:'/api/site/delete_tag/'}, filters: [{key:'task_id',label:'任务 ID'},{key:'status',label:'状态码',type:'number'},{key:'tag',label:'标签'}], columns: [
    { title: '站点', dataIndex: 'site' }, { title: '标题', dataIndex: 'title' }, { title: '状态', dataIndex: 'status' }, { title: '指纹', dataIndex: 'finger' }, { title: '标签', dataIndex: 'tag' }] },
  { key: 'services', title: '服务资产', eyebrow: 'ASSET / SERVICE', endpoint: '/api/service/', searchKey: 'service_name', exportEndpoint: '/api/service/export/', deleteEndpoint: '/api/service/delete/', filters: [{key:'task_id',label:'任务 ID'},{key:'service_info.ip',label:'IP'}], columns: [
    { title: '服务', dataIndex: 'service_name' }, { title: '探测信息', dataIndex: 'service_info' }, { title: '任务', dataIndex: 'task_id' }] },
  { key: 'urls', title: 'URL 资产', eyebrow: 'ASSET / URL', endpoint: '/api/url/', searchKey: 'url', exportEndpoint: '/api/url/export/', deleteEndpoint: '/api/url/delete/', filters: [{key:'task_id',label:'任务 ID'},{key:'status_code',label:'状态码',type:'number'}], columns: [
    { title: 'URL', dataIndex: 'url' }, { title: '状态', dataIndex: 'status_code' }, { title: '标题', dataIndex: 'title' }, { title: '任务', dataIndex: 'task_id' }] },
  { key: 'vulnerabilities', title: '漏洞结果', eyebrow: 'FINDINGS / VULN', endpoint: '/api/vuln/', searchKey: 'vul_name', deleteEndpoint: '/api/vuln/delete/', filters: [{key:'task_id',label:'任务 ID'},{key:'plg_type',label:'插件类型'}], columns: [
    { title: '漏洞', dataIndex: 'vul_name' }, { title: '目标', dataIndex: 'target' }, { title: '插件', dataIndex: 'plg_name' }, { title: '任务', dataIndex: 'task_id' }] },
  { key: 'nuclei', title: 'Nuclei 结果', eyebrow: 'FINDINGS / NUCLEI', endpoint: '/api/nuclei_result/', searchKey: 'vuln_name', deleteEndpoint: '/api/nuclei_result/delete/', filters: [{key:'task_id',label:'任务 ID'},{key:'vuln_severity',label:'严重性',options:['critical','high','medium','low','info']}], columns: [
    { title: '名称', dataIndex: 'vuln_name' }, { title: '严重性', dataIndex: 'vuln_severity' }, { title: 'URL', dataIndex: 'vuln_url' }, { title: '模板', dataIndex: 'template_id' }] },
  { key: 'leaks', title: '文件泄漏', eyebrow: 'FINDINGS / FILES', endpoint: '/api/fileleak/', searchKey: 'url', deleteEndpoint: '/api/fileleak/delete/', filters: [{key:'task_id',label:'任务 ID'}], columns: [
    { title: 'URL', dataIndex: 'url' }, { title: '状态', dataIndex: 'status_code' }, { title: '长度', dataIndex: 'content_length' }, { title: '任务', dataIndex: 'task_id' }] },
  { key: 'wih', title: 'Web 信息猎手', eyebrow: 'FINDINGS / WIH', endpoint: '/api/wih/', searchKey: 'content', exportEndpoint: '/api/wih/export/', deleteEndpoint: '/api/wih/delete/', filters: [{key:'task_id',label:'任务 ID'},{key:'record_type',label:'记录类型'}], columns: [
    { title: '内容', dataIndex: 'content' }, { title: '来源', dataIndex: 'source' }, { title: '类型', dataIndex: 'record_type' }, { title: '任务', dataIndex: 'task_id' }] },
  { key: 'githubResults', title: 'GitHub 结果', eyebrow: 'GITHUB / RESULTS', endpoint: '/api/github_result/', searchKey: 'human_content', columns: [
    { title: '仓库', dataIndex: 'repo_full_name' }, { title: '路径', dataIndex: 'path' }, { title: '匹配内容', dataIndex: 'human_content' }, { title: '任务', dataIndex: 'github_task_id' }] },
]

export const resourceMap = Object.fromEntries(resources.map((item) => [item.key, item]))
