<script setup lang="ts">
import { Alert as _AAlertImpl, Button as _AButtonImpl, Textarea as _ATextareaImpl, Tooltip as _ATooltipImpl } from 'ant-design-vue'
const AAlert: any = _AAlertImpl
const AButton: any = _AButtonImpl
const ATextarea: any = _ATextareaImpl
const ATooltip: any = _ATooltipImpl
import { computed, nextTick, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { apiRequest, postSse, type SseEvent } from '../api/client'
import { useAuthStore } from '../stores/auth'
import { DeleteOutlined, PlusOutlined, SafetyCertificateOutlined, SendOutlined, StopOutlined, ToolOutlined } from '@ant-design/icons-vue'

interface Conversation { _id: string; title: string; updated_at: string }
interface ChatMessage { role: string; content: string }
interface Timeline { name: string; status: string; duration_ms?: number; result?: any }
const router = useRouter(); const auth = useAuthStore(); const conversations = ref<Conversation[]>([]); const conversationId = ref('')
const messages = ref<ChatMessage[]>([]); const timeline = ref<Timeline[]>([]); const input = ref(''); const streaming = ref(false); const granted = ref(false)
const available = ref(false); const unavailableReason = ref(''); const scrollEl = ref<HTMLElement>(); let controller: AbortController | undefined
const conversationPage=ref(1);const conversationTotal=ref(0)
const rendered = (text: string) => DOMPurify.sanitize(marked.parse(text, { async: false }) as string)
async function loadList(reset=true) { if(reset)conversationPage.value=1;const data = await apiRequest<{items:Conversation[];total:number}>(`/api/ai/conversations?page=${conversationPage.value}&size=20`); conversations.value = reset?(data.items||[]):[...conversations.value,...(data.items||[])];conversationTotal.value=data.total||0;conversationPage.value+=1 }
async function loadConversation(id: string) { const data = await apiRequest<any>(`/api/ai/conversations/${id}`); conversationId.value = id; messages.value = data.messages || []; timeline.value = (data.actions || []).filter((x:any)=>!x.tool_name.startsWith('authorization_')).map((x:any)=>({name:x.tool_name,status:x.status,duration_ms:x.duration_ms,result:x.result})); granted.value = data.granted; await auth.load(id) }
function newChat() { controller?.abort(); conversationId.value=''; messages.value=[]; timeline.value=[]; granted.value=false }
async function removeConversation(id: string) { await apiRequest(`/api/ai/conversations/${id}`, {method:'DELETE'}); if(conversationId.value===id)newChat(); await loadList() }
async function toggleGrant() { if (!conversationId.value) return message.info('先发送一条消息建立对话，再开启执行授权'); const method = granted.value ? 'DELETE' : 'POST'; await apiRequest('/api/ai/grant', {method, body:JSON.stringify({conversation_id:conversationId.value})}); granted.value=!granted.value; message.success(granted.value?'本对话已获得任务创建授权':'已撤销任务创建授权') }
async function send() {
  const text=input.value.trim(); if(!text||streaming.value)return; input.value=''; messages.value.push({role:'user',content:text},{role:'assistant',content:''}); streaming.value=true; controller=new AbortController()
  try { await postSse('/api/ai/chat/stream',{conversation_id:conversationId.value||undefined,message:text},onEvent,controller.signal); await loadList() }
  catch(e){ if((e as Error).name!=='AbortError')message.error((e as Error).message) } finally {streaming.value=false}
}
function onEvent(event:SseEvent<any>) {
  if(event.event==='message_start')conversationId.value=event.data.conversation_id
  if(event.event==='text_delta')messages.value[messages.value.length-1].content+=event.data.text
  if(event.event==='tool_start')timeline.value.push({name:event.data.name,status:'running'})
  if(event.event==='tool_result'){const item=[...timeline.value].reverse().find(x=>x.name===event.data.name&&x.status==='running');if(item)Object.assign(item,{status:event.data.status,duration_ms:event.data.duration_ms,result:event.data.result})}
  if(event.event==='action'&&event.data.type==='task_created')event.data.tasks.forEach((task:any)=>timeline.value.push({name:`任务 ${task.name||task.task_id}`,status:'created',result:task}))
  if(event.event==='error')message.error(event.data.message)
  nextTick(()=>{if(scrollEl.value)scrollEl.value.scrollTop=scrollEl.value.scrollHeight})
}
onMounted(async()=>{try{const status=await apiRequest<any>('/api/ai/status');available.value=status.available;unavailableReason.value=status.reason;await loadList();if(conversations.value[0])await loadConversation(conversations.value[0]._id)}catch{/* auth interceptor */}})
</script>
<template>
  <section class="ai-workspace">
    <aside class="conversation-rail"><div class="rail-head"><div><span class="eyebrow">AI / THREADS</span><h2>对话</h2></div><a-button shape="circle" @click="newChat"><PlusOutlined/></a-button></div><button v-for="item in conversations" :key="item._id" :class="{active:item._id===conversationId}" @click="loadConversation(item._id)"><span>{{item.title}}</span><small>{{item.updated_at?.slice(0,16).replace('T',' ')}}</small><DeleteOutlined @click.stop="removeConversation(item._id)"/></button><button v-if="conversations.length<conversationTotal" class="load-more" @click="loadList(false)"><span>加载更多对话</span></button><div v-if="!conversations.length" class="rail-empty">新对话会保留 90 天</div></aside>
    <main class="chat-stage"><header class="chat-head"><div><span class="eyebrow">ARL NATIVE AI</span><h1>侦察副驾驶</h1></div><a-tooltip :title="conversationId?'授权只绑定当前登录会话与本对话':'发送消息后可授权'"><a-button :danger="granted" :disabled="!conversationId" @click="toggleGrant"><SafetyCertificateOutlined/>{{granted?'撤销执行授权':'开启执行授权'}}</a-button></a-tooltip></header>
      <a-alert v-if="!available" type="warning" show-icon :message="unavailableReason||'AI 服务不可用'" description="普通 ARL 查询与任务功能不受影响。"/>
      <div ref="scrollEl" class="message-stream">
        <div v-if="!messages.length" class="ai-empty"><div class="radar-signature"><i/><i/><i/><b/></div><span class="eyebrow">QUERY · EXPLAIN · ACT</span><h2>从一个侦察问题开始</h2><p>例如：“列出最近失败的任务并分析常见原因”，或“查看 example.com 的站点与漏洞结果”。</p><div><button @click="input='列出最近失败的任务，并总结可能原因'">梳理失败任务</button><button @click="input='查看最近发现的高风险漏洞'">检查风险信号</button></div></div>
        <article v-for="(item,index) in messages" :key="index" :class="['chat-message',item.role]"><span>{{item.role==='user'?'YOU':'ARL AI'}}</span><div v-if="item.role==='assistant'" class="markdown" v-html="rendered(item.content|| (streaming?'正在读取信号…':''))"/><p v-else>{{item.content}}</p></article>
      </div>
      <form class="composer" @submit.prevent="send"><a-textarea v-model:value="input" :disabled="!available" :auto-size="{minRows:1,maxRows:5}" placeholder="询问资产、结果或任务；Shift + Enter 换行" @keydown.enter.exact.prevent="send"/><a-button v-if="streaming" danger shape="circle" @click="controller?.abort()"><StopOutlined/></a-button><a-button v-else type="primary" shape="circle" html-type="submit" :disabled="!available||!input.trim()"><SendOutlined/></a-button><small>AI 只能使用固定工具；扫描创建需要本对话授权。</small></form>
    </main>
    <aside class="tool-rail"><div class="rail-head"><div><span class="eyebrow">TRACE</span><h2>工具时间线</h2></div><ToolOutlined/></div><div v-if="!timeline.length" class="tool-empty">工具调用会在这里显示参数边界、耗时与结果。</div><article v-for="(item,index) in timeline" :key="index" class="tool-event"><i :class="item.status"/><div><strong>{{item.name}}</strong><small>{{item.status}}<template v-if="item.duration_ms!==undefined"> · {{item.duration_ms}}ms</template></small><router-link v-if="item.status==='created'&&item.result?.task_id" :to="`/tasks/${item.result.task_id}`">打开任务</router-link></div></article></aside>
  </section>
</template>
