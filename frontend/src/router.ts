import { createRouter, createWebHistory } from 'vue-router'
import { resources } from './resources'
import LoginView from './views/LoginView.vue'

const DashboardView = () => import('./views/DashboardView.vue')
const ResourceView = () => import('./views/ResourceView.vue')
const TasksView = () => import('./views/TasksView.vue')
const TaskDetailView = () => import('./views/TaskDetailView.vue')
const AiConsoleView = () => import('./views/AiConsoleView.vue')
const SettingsView = () => import('./views/SettingsView.vue')

const router = createRouter({
  history: createWebHistory('/next/'),
  routes: [
    { path: '/login', component: LoginView, meta: { public: true } },
    { path: '/', component: DashboardView },
    { path: '/tasks', component: TasksView },
    { path: '/tasks/:id', component: TaskDetailView },
    { path: '/ai', component: AiConsoleView },
    { path: '/settings', component: SettingsView },
    ...resources.map((item) => ({ path: `/${item.key}`, component: ResourceView, props: { resourceKey: item.key } })),
  ],
})

router.beforeEach((to) => {
  if (!to.meta.public && !document.cookie.includes('')) {
    // The session cookie is HttpOnly; authentication is resolved by API calls.
  }
})

export default router
