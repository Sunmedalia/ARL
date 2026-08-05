export interface ResourceDefinition {
  key: string; title: string; eyebrow: string; endpoint: string; searchKey?: string
  columns: { title: string; dataIndex: string; width?: number }[]
}

export const resources: ResourceDefinition[] = [
  { key: 'domains', title: '域名资产', eyebrow: 'ASSET / DOMAIN', endpoint: '/api/domain/', searchKey: 'domain', columns: [
    { title: '域名', dataIndex: 'domain' }, { title: '记录类型', dataIndex: 'type' }, { title: '解析地址', dataIndex: 'ips' }, { title: '任务', dataIndex: 'task_id' }] },
  { key: 'ips', title: 'IP 资产', eyebrow: 'ASSET / IP', endpoint: '/api/ip/', searchKey: 'ip', columns: [
    { title: 'IP', dataIndex: 'ip' }, { title: '类型', dataIndex: 'ip_type' }, { title: '端口', dataIndex: 'port_info' }, { title: '任务', dataIndex: 'task_id' }] },
  { key: 'sites', title: '站点资产', eyebrow: 'ASSET / SITE', endpoint: '/api/site/', searchKey: 'site', columns: [
    { title: '站点', dataIndex: 'site' }, { title: '标题', dataIndex: 'title' }, { title: '状态', dataIndex: 'status' }, { title: '指纹', dataIndex: 'finger' }] },
  { key: 'services', title: '服务资产', eyebrow: 'ASSET / SERVICE', endpoint: '/api/service/', searchKey: 'service_name', columns: [
    { title: '服务', dataIndex: 'service_name' }, { title: '探测信息', dataIndex: 'service_info' }, { title: '任务', dataIndex: 'task_id' }] },
  { key: 'urls', title: 'URL 资产', eyebrow: 'ASSET / URL', endpoint: '/api/url/', searchKey: 'url', columns: [
    { title: 'URL', dataIndex: 'url' }, { title: '状态', dataIndex: 'status_code' }, { title: '标题', dataIndex: 'title' }, { title: '任务', dataIndex: 'task_id' }] },
  { key: 'groups', title: '资产组', eyebrow: 'SCOPE / GROUPS', endpoint: '/api/asset_scope/', searchKey: 'name', columns: [
    { title: '名称', dataIndex: 'name' }, { title: '类型', dataIndex: 'scope_type' }, { title: '范围', dataIndex: 'scope' }, { title: '黑名单', dataIndex: 'black_scope' }] },
  { key: 'monitors', title: '资产监控', eyebrow: 'AUTOMATION / MONITOR', endpoint: '/api/scheduler/', searchKey: 'name', columns: [
    { title: '名称', dataIndex: 'name' }, { title: '目标', dataIndex: 'target' }, { title: '状态', dataIndex: 'status' }, { title: '下次执行', dataIndex: 'next_run_time' }] },
  { key: 'policies', title: '扫描策略', eyebrow: 'CONTROL / POLICY', endpoint: '/api/policy/', searchKey: 'name', columns: [
    { title: '名称', dataIndex: 'name' }, { title: '说明', dataIndex: 'desc' }, { title: '更新时间', dataIndex: 'update_date' }] },
  { key: 'schedules', title: '计划任务', eyebrow: 'AUTOMATION / SCHEDULE', endpoint: '/api/task_schedule/', searchKey: 'name', columns: [
    { title: '名称', dataIndex: 'name' }, { title: '目标', dataIndex: 'target' }, { title: 'Cron', dataIndex: 'cron' }, { title: '状态', dataIndex: 'status' }] },
  { key: 'fingerprints', title: '指纹规则', eyebrow: 'INTEL / FINGERPRINT', endpoint: '/api/fingerprint/', searchKey: 'name', columns: [
    { title: '名称', dataIndex: 'name' }, { title: '规则', dataIndex: 'human_rule' }, { title: '更新时间', dataIndex: 'update_date' }] },
  { key: 'pocs', title: 'PoC 与爆破插件', eyebrow: 'INTEL / PLUGINS', endpoint: '/api/poc/', searchKey: 'plugin_name', columns: [
    { title: '插件 ID', dataIndex: 'plugin_name' }, { title: '应用', dataIndex: 'app_name' }, { title: '漏洞', dataIndex: 'vul_name' }, { title: '类型', dataIndex: 'plugin_type' }] },
  { key: 'vulnerabilities', title: '漏洞结果', eyebrow: 'FINDINGS / VULN', endpoint: '/api/vuln/', searchKey: 'vul_name', columns: [
    { title: '漏洞', dataIndex: 'vul_name' }, { title: '目标', dataIndex: 'target' }, { title: '插件', dataIndex: 'plg_name' }, { title: '任务', dataIndex: 'task_id' }] },
  { key: 'nuclei', title: 'Nuclei 结果', eyebrow: 'FINDINGS / NUCLEI', endpoint: '/api/nuclei_result/', searchKey: 'vuln_name', columns: [
    { title: '名称', dataIndex: 'vuln_name' }, { title: '严重性', dataIndex: 'vuln_severity' }, { title: 'URL', dataIndex: 'vuln_url' }, { title: '模板', dataIndex: 'template_id' }] },
  { key: 'leaks', title: '文件泄漏', eyebrow: 'FINDINGS / FILES', endpoint: '/api/fileleak/', searchKey: 'url', columns: [
    { title: 'URL', dataIndex: 'url' }, { title: '状态', dataIndex: 'status_code' }, { title: '长度', dataIndex: 'content_length' }, { title: '任务', dataIndex: 'task_id' }] },
  { key: 'wih', title: 'Web 信息猎手', eyebrow: 'FINDINGS / WIH', endpoint: '/api/wih/', searchKey: 'content', columns: [
    { title: '内容', dataIndex: 'content' }, { title: '来源', dataIndex: 'source' }, { title: '类型', dataIndex: 'record_type' }, { title: '任务', dataIndex: 'task_id' }] },
  { key: 'githubTasks', title: 'GitHub 任务', eyebrow: 'GITHUB / TASKS', endpoint: '/api/github_task/', searchKey: 'name', columns: [
    { title: '名称', dataIndex: 'name' }, { title: '关键词', dataIndex: 'keyword' }, { title: '状态', dataIndex: 'status' }, { title: '更新时间', dataIndex: 'update_date' }] },
  { key: 'githubMonitors', title: 'GitHub 监控', eyebrow: 'GITHUB / MONITOR', endpoint: '/api/github_scheduler/', searchKey: 'name', columns: [
    { title: '名称', dataIndex: 'name' }, { title: '关键词', dataIndex: 'keyword' }, { title: '状态', dataIndex: 'status' }, { title: '下次执行', dataIndex: 'next_run_time' }] },
  { key: 'githubResults', title: 'GitHub 结果', eyebrow: 'GITHUB / RESULTS', endpoint: '/api/github_result/', searchKey: 'human_content', columns: [
    { title: '仓库', dataIndex: 'repo_full_name' }, { title: '路径', dataIndex: 'path' }, { title: '匹配内容', dataIndex: 'human_content' }, { title: '任务', dataIndex: 'github_task_id' }] },
]

export const resourceMap = Object.fromEntries(resources.map((item) => [item.key, item]))
