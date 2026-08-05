import { createApp } from 'vue'
import { createPinia } from 'pinia'
import {
  Alert, Button, Divider, Drawer, Form, Input, Layout, Menu, Pagination,
  Select, Skeleton, Switch, Table, Tabs, Tag, Tooltip,
} from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'
import './styles.css'
import App from './App.vue'
import router from './router'

const app = createApp(App).use(createPinia()).use(router)
;[Alert, Button, Divider, Drawer, Form, Input, Layout, Menu, Pagination, Select,
  Skeleton, Switch, Table, Tabs, Tag, Tooltip].forEach((component) => app.use(component))
app.mount('#app')
