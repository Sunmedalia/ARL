<script setup lang="ts">
import { Button as _AButtonImpl, Input as _AInputImpl, InputPassword as _AInputPasswordImpl } from 'ant-design-vue'
const AButton: any = _AButtonImpl
const AInput: any = _AInputImpl
const AInputPassword: any = _AInputPasswordImpl
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { useAuthStore } from '../stores/auth'
import { safeRedirect } from '../router'

const username = ref(''); const password = ref(''); const loading = ref(false)
const auth = useAuthStore(); const router = useRouter(); const route = useRoute()
async function login() {
  loading.value = true
  try { await auth.login(username.value.trim(), password.value); await router.replace(safeRedirect(String(route.query.redirect || '')) || '/') }
  catch (error) { message.error(error instanceof Error ? error.message : '登录失败') }
  finally { loading.value = false }
}
</script>
<template>
  <main class="login-page">
    <section class="login-atmosphere" aria-hidden="true">
      <div class="range-ring ring-a"/><div class="range-ring ring-b"/><div class="range-ring ring-c"/>
      <div class="sweep"/><div class="lighthouse"><i/><b/></div>
      <p>ASSET RECONNAISSANCE<br/>LIGHTHOUSE</p>
    </section>
    <section class="login-panel">
      <div class="login-form">
        <span class="eyebrow">SECURE OPERATOR ACCESS</span>
        <h1>进入侦察控制台</h1>
        <p>连接资产、任务与威胁信号。登录会话将在浏览器关闭或 8 小时后失效。</p>
        <form @submit.prevent="login">
          <label>管理员账号<a-input v-model:value="username" size="large" autocomplete="username" /></label>
          <label>密码<a-input-password v-model:value="password" size="large" autocomplete="current-password" /></label>
          <a-button html-type="submit" type="primary" size="large" block :loading="loading">验证并进入</a-button>
        </form>
        <small>ARL / ADMIN PLANE / SESSION AUTH</small>
      </div>
    </section>
  </main>
</template>
