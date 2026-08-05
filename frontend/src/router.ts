import { createRouter, createWebHistory, type RouterHistory } from 'vue-router'
import { useAuthStore } from './stores/auth'
import { resources } from './resources'

const LoginView = () => import('./views/LoginView.vue')
const DashboardView = () => import('./views/DashboardView.vue')
const ResourceView = () => import('./views/ResourceView.vue')
const TasksView = () => import('./views/TasksView.vue')
const TaskDetailView = () => import('./views/TaskDetailView.vue')
const AiConsoleView = () => import('./views/AiConsoleView.vue')
const SettingsView = () => import('./views/SettingsView.vue')
const AssetGroupsView = () => import('./views/AssetGroupsView.vue')
const AssetGroupDetailView = () => import('./views/AssetGroupDetailView.vue')
const MonitorsView = () => import('./views/MonitorsView.vue')
const PoliciesView = () => import('./views/PoliciesView.vue')
const SchedulesView = () => import('./views/SchedulesView.vue')
const FingerprintsView = () => import('./views/FingerprintsView.vue')
const PocsView = () => import('./views/PocsView.vue')
const GithubView = () => import('./views/GithubView.vue')

export function createArlRouter(history: RouterHistory = createWebHistory('/next/')) {
const router = createRouter({
  history,
  routes: [
    { path: '/login', name: 'login', component: LoginView, meta: { public: true } },
    { path: '/', component: DashboardView, meta: { requiresAuth: true } },
    { path: '/tasks', component: TasksView, meta: { requiresAuth: true } },
    { path: '/tasks/:id', component: TaskDetailView, meta: { requiresAuth: true } },
    { path: '/ai', component: AiConsoleView, meta: { requiresAuth: true } },
    { path: '/settings', component: SettingsView, meta: { requiresAuth: true } },
    { path: '/groups', component: AssetGroupsView, meta: { requiresAuth: true } },
    { path: '/groups/:id', component: AssetGroupDetailView, meta: { requiresAuth: true } },
    { path: '/monitors', component: MonitorsView, meta: { requiresAuth: true } },
    { path: '/policies', component: PoliciesView, meta: { requiresAuth: true } },
    { path: '/schedules', component: SchedulesView, meta: { requiresAuth: true } },
    { path: '/fingerprints', component: FingerprintsView, meta: { requiresAuth: true } },
    { path: '/pocs', component: PocsView, meta: { requiresAuth: true } },
    { path: '/githubTasks', component: GithubView, props: { mode: 'tasks' }, meta: { requiresAuth: true } },
    { path: '/githubMonitors', component: GithubView, props: { mode: 'monitors' }, meta: { requiresAuth: true } },
    ...resources.map((item) => ({ path: `/${item.key}`, component: ResourceView, props: { resourceKey: item.key }, meta: { requiresAuth: true } })),
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (!auth.ready) {
    try { await auth.load() } catch { /* an anonymous session is an expected state */ }
  }
  if (to.meta.public && auth.authenticated) return safeRedirect(String(to.query.redirect || '')) || '/'
  if (to.meta.requiresAuth && !auth.authenticated) return { name: 'login', query: { redirect: to.fullPath } }
})
return router
}

export function safeRedirect(value: string) {
  return value.startsWith('/') && !value.startsWith('//') && !value.startsWith('/login') ? value : ''
}

export default createArlRouter()
