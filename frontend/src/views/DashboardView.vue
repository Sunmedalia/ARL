<script setup lang="ts">
import { Button as _AButtonImpl } from 'ant-design-vue'
const AButton: any = _AButtonImpl
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { apiRequest } from '../api/client'
import PageHeader from '../components/PageHeader.vue'
import { ArrowRightOutlined, RobotOutlined } from '@ant-design/icons-vue'

const router = useRouter(); const counts = ref({ tasks: 0, domains: 0, sites: 0, findings: 0 }); const recent = ref<Record<string, any>[]>([])
onMounted(async () => {
  const endpoints = ['/api/task/?page=1&size=6', '/api/domain/?page=1&size=1', '/api/site/?page=1&size=1', '/api/vuln/?page=1&size=1']
  const values = await Promise.allSettled(endpoints.map((path) => apiRequest<any>(path)))
  const data = values.map((item) => item.status === 'fulfilled' ? item.value : { total: 0, items: [] })
  counts.value = { tasks: data[0].total || 0, domains: data[1].total || 0, sites: data[2].total || 0, findings: data[3].total || 0 }
  recent.value = data[0].items || []
})
const stats = [ ['tasks', '侦察任务', '/tasks'], ['domains', '域名资产', '/domains'], ['sites', '已识别站点', '/sites'], ['findings', '漏洞信号', '/vulnerabilities'] ]
</script>
<template>
  <section class="page dashboard">
    <PageHeader eyebrow="CONTROL / OVERVIEW" title="资产态势台" description="从任务队列到已确认资产，用一条侦察链路观察当前暴露面。">
      <a-button type="primary" @click="router.push('/tasks')">下发侦察任务</a-button>
    </PageHeader>
    <div class="stat-deck">
      <button v-for="([key, label, path], index) in stats" :key="key" @click="router.push(path)">
        <span>0{{ index + 1 }} · {{ label }}</span><strong>{{ counts[key as keyof typeof counts].toLocaleString() }}</strong><ArrowRightOutlined />
      </button>
    </div>
    <div class="dashboard-grid">
      <article class="data-panel recent-panel">
        <div class="panel-title"><div><span class="eyebrow">LIVE QUEUE</span><h2>最近任务</h2></div><a @click="router.push('/tasks')">查看全部</a></div>
        <button v-for="task in recent" :key="task._id" class="task-line" @click="router.push(`/tasks/${task._id}`)">
          <i :class="task.status"/><span><strong>{{ task.name }}</strong><small>{{ task.target }}</small></span><em>{{ task.status }}</em>
        </button>
        <div v-if="!recent.length" class="empty-copy">还没有任务。下发第一个目标后，侦察状态会出现在这里。</div>
      </article>
      <article class="ai-callout">
        <div class="mini-radar"><i/><b/><span/></div>
        <span class="eyebrow">AI / COPILOT</span><h2>用自然语言读取<br/>你的资产面</h2>
        <p>让 AI 组合受限查询、解释发现，并在本会话明确授权后创建扫描任务。</p>
        <a-button ghost @click="router.push('/ai')"><RobotOutlined />打开 AI 控制台</a-button>
      </article>
    </div>
  </section>
</template>
