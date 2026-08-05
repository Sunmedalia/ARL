<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'
import {
  ApiOutlined, AppstoreOutlined, BugOutlined, BulbOutlined, ClockCircleOutlined,
  CodeOutlined, DatabaseOutlined, GithubOutlined, LogoutOutlined, RadarChartOutlined,
  RobotOutlined, SafetyCertificateOutlined, SettingOutlined,
} from '@ant-design/icons-vue'

const route = useRoute(); const router = useRouter(); const auth = useAuthStore()
const collapsed = ref(false)
const selected = computed(() => [route.path])
onMounted(async () => {
  if (route.meta.public) return
  try { await auth.load() } catch { /* interceptor redirects */ }
})
const nav = [
  { label: '态势台', key: '/', icon: AppstoreOutlined },
  { label: 'AI 控制台', key: '/ai', icon: RobotOutlined, signal: true },
  { type: 'divider' },
  { label: '任务', key: '/tasks', icon: RadarChartOutlined },
  { label: '资产', key: 'assets', icon: DatabaseOutlined, children: [
    ['域名', '/domains'], ['IP', '/ips'], ['站点', '/sites'], ['服务', '/services'], ['URL', '/urls'], ['资产组', '/groups'],
  ].map(([label, key]) => ({ label, key })) },
  { label: '发现', key: 'findings', icon: BugOutlined, children: [
    ['漏洞结果', '/vulnerabilities'], ['Nuclei', '/nuclei'], ['文件泄漏', '/leaks'], ['信息猎手', '/wih'],
  ].map(([label, key]) => ({ label, key })) },
  { label: '自动化', key: 'automation', icon: ClockCircleOutlined, children: [
    ['资产监控', '/monitors'], ['扫描策略', '/policies'], ['计划任务', '/schedules'],
  ].map(([label, key]) => ({ label, key })) },
  { label: '规则与插件', key: 'intel', icon: SafetyCertificateOutlined, children: [
    ['指纹规则', '/fingerprints'], ['PoC / 爆破', '/pocs'],
  ].map(([label, key]) => ({ label, key })) },
  { label: 'GitHub', key: 'github', icon: GithubOutlined, children: [
    ['搜索任务', '/githubTasks'], ['监控任务', '/githubMonitors'], ['泄漏结果', '/githubResults'],
  ].map(([label, key]) => ({ label, key })) },
]
function onMenu({ key }: { key: string }) { if (key.startsWith('/')) router.push(key) }
function openLegacy() { window.location.assign('/legacy/') }
</script>

<template>
  <router-view v-if="route.meta.public" />
  <a-layout v-else class="shell">
    <a-layout-sider v-model:collapsed="collapsed" :width="248" :collapsed-width="72" class="sider">
      <button class="brand" @click="router.push('/')" aria-label="返回态势台">
        <span class="beacon"><i /></span>
        <span v-if="!collapsed" class="brand-copy"><strong>ARL</strong><small>RECON LIGHTHOUSE</small></span>
      </button>
      <a-menu mode="inline" theme="dark" :selected-keys="selected" :items="nav" @click="onMenu" />
      <div class="sider-foot" :class="{ compact: collapsed }">
        <span class="system-dot" />
        <span v-if="!collapsed">CONTROL PLANE · ONLINE</span>
      </div>
    </a-layout-sider>
    <a-layout>
      <header class="topbar">
        <button class="collapse" @click="collapsed = !collapsed"><ApiOutlined /></button>
        <div class="breadcrumb"><span>ARL</span><b>/</b><strong>{{ route.path === '/' ? 'OVERVIEW' : route.path.slice(1).toUpperCase() }}</strong></div>
        <div class="top-actions">
          <span class="operator"><i />{{ auth.username || 'ADMIN' }}</span>
          <button title="返回旧版控制台" @click="openLegacy"><CodeOutlined /></button>
          <button title="设置" @click="router.push('/settings')"><SettingOutlined /></button>
          <button title="退出" @click="auth.logout"><LogoutOutlined /></button>
        </div>
      </header>
      <a-layout-content class="content"><router-view /></a-layout-content>
    </a-layout>
  </a-layout>
</template>
