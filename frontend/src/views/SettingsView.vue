<script setup lang="ts">
import { Button as _AButtonImpl, Form as _AFormImpl, FormItem as _AFormItemImpl, InputPassword as _AInputPasswordImpl } from 'ant-design-vue'
const AButton: any = _AButtonImpl
const AForm: any = _AFormImpl
const AFormItem: any = _AFormItemImpl
const AInputPassword: any = _AInputPasswordImpl
import { reactive, ref } from 'vue'
import { message } from 'ant-design-vue'
import PageHeader from '../components/PageHeader.vue'
import { apiRequest } from '../api/client'
const form = reactive({ old_password: '', new_password: '', check_password: '' }); const loading = ref(false)
async function save() { if (form.new_password !== form.check_password) return message.error('两次输入的新密码不一致'); loading.value = true; try { await apiRequest('/api/user/change_pass', {method:'POST',body:JSON.stringify(form)}); message.success('密码已更新，请重新登录'); location.assign('/next/login') } catch(e) { message.error((e as Error).message) } finally {loading.value=false} }
</script>
<template><section class="page"><PageHeader eyebrow="ACCOUNT / SECURITY" title="管理员设置" description="更新管理员凭据。保存后，当前会话将立即撤销。"/><div class="settings-card data-panel"><a-form layout="vertical" @finish="save"><a-form-item label="当前密码" required><a-input-password v-model:value="form.old_password"/></a-form-item><a-form-item label="新密码" required><a-input-password v-model:value="form.new_password"/></a-form-item><a-form-item label="确认新密码" required><a-input-password v-model:value="form.check_password"/></a-form-item><a-button type="primary" html-type="submit" :loading="loading">保存新密码</a-button></a-form></div></section></template>
