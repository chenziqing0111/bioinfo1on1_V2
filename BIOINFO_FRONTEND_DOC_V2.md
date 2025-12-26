# BioInfo1on1 前端开发文档 V2.0

> **技术栈**: Uni-app (Vue 3 + TypeScript) | **目标平台**: 微信小程序 | **UI 框架**: uv-ui

---

## 1. 项目概览

### 1.1 技术选型

| 类别 | 选型 | 理由 |
|-----|------|-----|
| 框架 | Uni-app + Vue 3 | 跨端能力，后续可扩展 H5/App |
| 语言 | TypeScript | 类型安全，减少运行时错误 |
| 状态管理 | Pinia | Vue 3 官方推荐，轻量 |
| UI 组件 | uv-ui | 专为 uni-app 优化，组件丰富 |
| 请求库 | uni.request 封装 | 原生性能最优 |
| 样式 | SCSS | 变量、混入支持好 |

### 1.2 用户角色与核心流程

```
学员 (Student)
├── 首页浏览导师
├── AI 智能匹配
├── 创建预约订单
├── 查看 AI 教案
├── 上课 & 评价
└── 个人中心

导师 (Tutor)
├── 入驻申请
├── 接单管理
├── 查看学员需求
├── 设置会议链接
├── 上课 & 评价
└── 个人中心 & 收益
```

---

## 2. 项目目录结构

```
bioinfo1on1-miniprogram/
├── src/
│   ├── api/                    # API 接口封装
│   │   ├── index.ts            # 请求实例
│   │   ├── auth.ts             # 认证接口
│   │   ├── mentor.ts           # 导师接口
│   │   ├── appointment.ts      # 订单接口
│   │   └── ai.ts               # AI 接口
│   │
│   ├── components/             # 公共组件
│   │   ├── MentorCard.vue      # 导师卡片
│   │   ├── AppointmentCard.vue # 订单卡片
│   │   ├── TagSelector.vue     # 标签选择器
│   │   ├── NDAModal.vue        # NDA 协议弹窗
│   │   ├── RatingStars.vue     # 评分星星
│   │   └── Empty.vue           # 空状态
│   │
│   ├── pages/                  # 页面
│   │   ├── index/              # 首页（导师列表）
│   │   ├── mentor/             # 导师详情
│   │   ├── ai-match/           # AI 智能匹配
│   │   ├── appointment/        # 订单相关
│   │   │   ├── create.vue      # 创建订单
│   │   │   ├── detail.vue      # 订单详情
│   │   │   ├── list.vue        # 订单列表
│   │   │   └── lesson-plan.vue # AI 教案
│   │   ├── tutor/              # 导师端
│   │   │   ├── apply.vue       # 入驻申请
│   │   │   ├── orders.vue      # 接单管理
│   │   │   └── profile.vue     # 导师资料
│   │   ├── user/               # 用户中心
│   │   │   ├── index.vue       # 个人中心
│   │   │   └── settings.vue    # 设置
│   │   └── review/             # 评价
│   │       └── create.vue      # 提交评价
│   │
│   ├── stores/                 # Pinia 状态管理
│   │   ├── user.ts             # 用户状态
│   │   └── appointment.ts      # 订单状态
│   │
│   ├── utils/                  # 工具函数
│   │   ├── request.ts          # 请求封装
│   │   ├── auth.ts             # 登录工具
│   │   └── format.ts           # 格式化工具
│   │
│   ├── types/                  # TypeScript 类型
│   │   ├── user.d.ts
│   │   ├── mentor.d.ts
│   │   └── appointment.d.ts
│   │
│   ├── static/                 # 静态资源
│   ├── styles/                 # 全局样式
│   │
│   ├── App.vue
│   ├── main.ts
│   ├── pages.json              # 页面路由配置
│   └── manifest.json           # 应用配置
│
├── package.json
├── tsconfig.json
└── vite.config.ts
```

---

## 3. 页面路由设计 (pages.json)

```json
{
  "pages": [
    { "path": "pages/index/index", "style": { "navigationBarTitleText": "BioInfo1on1" } },
    { "path": "pages/mentor/detail", "style": { "navigationBarTitleText": "导师详情" } },
    { "path": "pages/ai-match/index", "style": { "navigationBarTitleText": "智能匹配" } },
    { "path": "pages/appointment/create", "style": { "navigationBarTitleText": "预约咨询" } },
    { "path": "pages/appointment/detail", "style": { "navigationBarTitleText": "订单详情" } },
    { "path": "pages/appointment/list", "style": { "navigationBarTitleText": "我的订单" } },
    { "path": "pages/appointment/lesson-plan", "style": { "navigationBarTitleText": "AI 教案" } },
    { "path": "pages/tutor/apply", "style": { "navigationBarTitleText": "成为导师" } },
    { "path": "pages/tutor/orders", "style": { "navigationBarTitleText": "接单管理" } },
    { "path": "pages/user/index", "style": { "navigationBarTitleText": "个人中心" } },
    { "path": "pages/review/create", "style": { "navigationBarTitleText": "评价" } }
  ],
  "tabBar": {
    "color": "#999999",
    "selectedColor": "#2B579A",
    "list": [
      { "pagePath": "pages/index/index", "text": "首页", "iconPath": "static/icons/home.png", "selectedIconPath": "static/icons/home-active.png" },
      { "pagePath": "pages/ai-match/index", "text": "智能匹配", "iconPath": "static/icons/ai.png", "selectedIconPath": "static/icons/ai-active.png" },
      { "pagePath": "pages/appointment/list", "text": "订单", "iconPath": "static/icons/order.png", "selectedIconPath": "static/icons/order-active.png" },
      { "pagePath": "pages/user/index", "text": "我的", "iconPath": "static/icons/user.png", "selectedIconPath": "static/icons/user-active.png" }
    ]
  }
}
```

---

## 4. 请求封装 (src/utils/request.ts)

```typescript
import { useUserStore } from '@/stores/user'

const BASE_URL = import.meta.env.VITE_API_BASE_URL

interface ApiResponse<T = any> {
  success: boolean
  data: T
  error?: { code: number; message: string }
}

export async function request<T = any>(options: {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  showLoading?: boolean
}): Promise<T> {
  const userStore = useUserStore()
  const { url, method = 'GET', data, showLoading = true } = options

  if (showLoading) uni.showLoading({ title: '加载中...' })

  try {
    const response = await uni.request({
      url: `${BASE_URL}${url}`,
      method,
      data,
      header: {
        'Content-Type': 'application/json',
        ...(userStore.token ? { Authorization: `Bearer ${userStore.token}` } : {})
      }
    })

    const result = response.data as ApiResponse<T>
    if (showLoading) uni.hideLoading()

    if (!result.success) {
      // Token 过期
      if (result.error?.code === 1001 || result.error?.code === 1002) {
        userStore.logout()
        uni.navigateTo({ url: '/pages/user/index' })
      }
      throw new Error(result.error?.message || '请求失败')
    }

    return result.data
  } catch (error: any) {
    if (showLoading) uni.hideLoading()
    uni.showToast({ title: error.message, icon: 'none' })
    throw error
  }
}

export const get = <T>(url: string, data?: any) => request<T>({ url, method: 'GET', data })
export const post = <T>(url: string, data?: any) => request<T>({ url, method: 'POST', data })
export const put = <T>(url: string, data?: any) => request<T>({ url, method: 'PUT', data })
```

---

## 5. API 接口定义

```typescript
// src/api/auth.ts
import { post, get } from '@/utils/request'

export const authApi = {
  wxLogin: (code: string) => post('/api/v1/auth/wx-login', { code }),
  getMe: () => get('/api/v1/auth/me')
}

// src/api/mentor.ts
export const mentorApi = {
  getList: (params?: any) => get('/api/v1/mentors', params),
  getDetail: (id: string) => get(`/api/v1/mentors/${id}`),
  apply: (data: any) => post('/api/v1/mentors/apply', data),
  getTags: () => get('/api/v1/mentors/tags')
}

// src/api/appointment.ts
export const appointmentApi = {
  create: (data: any) => post('/api/v1/appointments', data),
  getList: (params?: any) => get('/api/v1/appointments', params),
  getDetail: (id: string) => get(`/api/v1/appointments/${id}`),
  accept: (id: string, meetingLink: string) => post(`/api/v1/appointments/${id}/accept`, { meeting_link: meetingLink }),
  cancel: (id: string, reason: string) => post(`/api/v1/appointments/${id}/cancel`, { reason }),
  getLessonPlan: (id: string) => get(`/api/v1/appointments/${id}/lesson-plan`)
}

// src/api/ai.ts
export const aiApi = {
  match: (requirement: string) => post('/api/v1/ai/match', { requirement })
}
```

---

## 6. 状态管理 (Pinia)

```typescript
// src/stores/user.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(uni.getStorageSync('token') || '')
  const userInfo = ref<any>(null)
  
  const isLoggedIn = computed(() => !!token.value)
  const isTutor = computed(() => userInfo.value?.role === 'tutor')
  
  async function wxLogin() {
    const { code } = await uni.login({ provider: 'weixin' })
    const result = await authApi.wxLogin(code)
    
    token.value = result.access_token
    uni.setStorageSync('token', token.value)
    
    await fetchUserInfo()
    return result.is_new_user
  }
  
  async function fetchUserInfo() {
    if (!token.value) return
    userInfo.value = await authApi.getMe()
  }
  
  function logout() {
    token.value = ''
    userInfo.value = null
    uni.removeStorageSync('token')
  }
  
  function checkLogin(redirect = true): boolean {
    if (!isLoggedIn.value && redirect) {
      uni.navigateTo({ url: '/pages/user/index' })
    }
    return isLoggedIn.value
  }
  
  return { token, userInfo, isLoggedIn, isTutor, wxLogin, fetchUserInfo, logout, checkLogin }
})
```

---

## 7. 核心页面示例

### 7.1 AI 智能匹配页

```vue
<template>
  <view class="page">
    <!-- 输入区域 -->
    <view class="input-section">
      <view class="title">🤖 描述你的问题</view>
      <textarea
        v-model="requirement"
        placeholder="请详细描述你遇到的生信问题..."
        :maxlength="2000"
        class="input"
      />
      <view class="char-count">{{ requirement.length }}/2000</view>
    </view>
    
    <!-- 匹配按钮 -->
    <button 
      class="match-btn" 
      :disabled="requirement.length < 20 || matching"
      @click="doMatch"
    >
      {{ matching ? '匹配中...' : '🎯 开始智能匹配' }}
    </button>
    
    <!-- 匹配结果 -->
    <view v-if="matchResult" class="result-section">
      <view class="title">✨ 为你推荐</view>
      <view 
        v-for="(item, index) in matchResult.recommendations" 
        :key="item.mentor_id"
        class="recommendation-card"
      >
        <view class="rank">TOP {{ index + 1 }}</view>
        <view class="score">匹配度: {{ (item.score * 100).toFixed(0) }}%</view>
        <view class="reason">{{ item.reason }}</view>
        <button @click="goBook(item.mentor_id)">立即预约</button>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { aiApi } from '@/api/ai'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const requirement = ref('')
const matching = ref(false)
const matchResult = ref<any>(null)

async function doMatch() {
  if (!userStore.checkLogin()) return
  
  matching.value = true
  try {
    matchResult.value = await aiApi.match(requirement.value)
  } finally {
    matching.value = false
  }
}

function goBook(mentorId: string) {
  uni.navigateTo({ 
    url: `/pages/appointment/create?mentor_id=${mentorId}&requirement=${encodeURIComponent(requirement.value)}`
  })
}
</script>
```

### 7.2 创建订单页核心逻辑

```vue
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { mentorApi } from '@/api/mentor'
import { appointmentApi } from '@/api/appointment'

const mentor = ref<any>(null)
const scheduledTime = ref(Date.now() + 86400000)
const duration = ref(60)
const requirements = ref('')
const acceptNda = ref(false)

const totalPrice = computed(() => 
  mentor.value ? (duration.value * mentor.value.hourly_rate / 60).toFixed(2) : 0
)

const canSubmit = computed(() => 
  mentor.value && requirements.value.length >= 20 && acceptNda.value
)

onMounted(async () => {
  const pages = getCurrentPages()
  const options = (pages[pages.length - 1] as any).options
  mentor.value = await mentorApi.getDetail(options.mentor_id)
  requirements.value = decodeURIComponent(options.requirement || '')
})

async function handleSubmit() {
  if (!acceptNda.value) {
    return uni.showToast({ title: '请先同意保密协议', icon: 'none' })
  }
  
  const result = await appointmentApi.create({
    mentor_id: mentor.value.id,
    scheduled_time: new Date(scheduledTime.value).toISOString(),
    duration_minutes: duration.value,
    requirements: requirements.value,
    accept_nda: true
  })
  
  uni.showToast({ title: '预约成功', icon: 'success' })
  setTimeout(() => {
    uni.redirectTo({ url: `/pages/appointment/detail?id=${result.id}` })
  }, 1500)
}
</script>
```

---

## 8. TypeScript 类型定义

```typescript
// src/types/appointment.d.ts
export type AppointmentStatus = 
  | 'pending_accept' | 'accepted' | 'to_attend' 
  | 'in_progress' | 'evaluating' | 'completed' 
  | 'cancelled' | 'refunding' | 'refunded'

export interface Appointment {
  id: string
  order_no: string
  learner_id: string
  mentor_id: string
  status: AppointmentStatus
  price: number
  duration_minutes: number
  scheduled_time: string | null
  meeting_link: string | null
  requirements: string | null
  accept_nda: boolean
  created_at: string
}

export interface LessonPlan {
  id: string
  appointment_id: string
  content_md: string
  model_name: string | null
  is_fallback: boolean
}

// src/types/ai.d.ts
export interface MatchResult {
  recommendations: {
    mentor_id: string
    score: number
    reason: string
    can_solve: string[]
  }[]
}
```

---

## 9. 开发指令 (给 Claude Code)

### 任务一：初始化项目

```
使用 Vue 3 + TypeScript 初始化 uni-app 项目：

npx degit dcloudio/uni-preset-vue#vite-ts bioinfo1on1-miniprogram
cd bioinfo1on1-miniprogram
npm install pinia @vueuse/core

创建完整目录结构：api/, components/, pages/, stores/, types/, utils/
```

### 任务二：实现请求封装

```
在 src/utils/request.ts 中实现：
- Token 自动携带
- 统一错误处理  
- Token 过期自动跳转登录
```

### 任务三：实现核心页面

```
按优先级实现：
1. pages/index/index.vue - 首页导师列表
2. pages/ai-match/index.vue - AI 智能匹配
3. pages/appointment/create.vue - 创建订单（含 NDA 签署）
4. pages/appointment/list.vue - 订单列表
5. pages/user/index.vue - 个人中心（含微信登录）
```

### 任务四：实现公共组件

```
components/MentorCard.vue - 导师卡片
components/NDAModal.vue - NDA 协议弹窗
components/Empty.vue - 空状态
```

---

## 10. 多端兼容方案

### 10.1 支持的平台

```bash
# 微信小程序
npm run dev:mp-weixin
npm run build:mp-weixin

# H5 网页端 ✅
npm run dev:h5
npm run build:h5

# App (需要 HBuilderX)
npm run dev:app
npm run build:app

# 其他小程序
npm run dev:mp-alipay      # 支付宝
npm run dev:mp-toutiao     # 抖音
```

### 10.2 登录兼容处理

微信小程序和 H5 的登录方式不同，需要条件编译：

```typescript
// src/stores/user.ts
async function login() {
  // #ifdef MP-WEIXIN
  // 小程序登录
  const { code } = await uni.login({ provider: 'weixin' })
  const result = await authApi.wxLogin(code)
  // #endif
  
  // #ifdef H5
  // H5 使用微信网页授权 或 手机号登录
  const result = await authApi.h5Login(phone, code)
  // #endif
  
  token.value = result.access_token
  uni.setStorageSync('token', token.value)
}
```

### 10.3 API 兼容处理

```typescript
// src/api/auth.ts
export const authApi = {
  // 小程序登录
  wxLogin: (code: string) => post('/api/v1/auth/wx-login', { code }),
  
  // H5 手机号登录（需要后端新增接口）
  sendSmsCode: (phone: string) => post('/api/v1/auth/sms/send', { phone }),
  h5Login: (phone: string, code: string) => post('/api/v1/auth/sms/verify', { phone, code }),
  
  // H5 微信网页授权登录（可选）
  getWxAuthUrl: () => get('/api/v1/auth/wx-h5/url'),
  wxH5Login: (code: string) => post('/api/v1/auth/wx-h5/login', { code })
}
```

### 10.4 条件编译语法

```vue
<template>
  <!-- 仅小程序显示 -->
  <!-- #ifdef MP-WEIXIN -->
  <button open-type="getPhoneNumber" @getphonenumber="onGetPhone">
    微信手机号快捷登录
  </button>
  <!-- #endif -->
  
  <!-- 仅 H5 显示 -->
  <!-- #ifdef H5 -->
  <view class="h5-login">
    <input v-model="phone" placeholder="请输入手机号" />
    <button @click="sendCode">获取验证码</button>
    <input v-model="smsCode" placeholder="验证码" />
    <button @click="login">登录</button>
  </view>
  <!-- #endif -->
</template>
```

### 10.5 样式兼容

```scss
// 不同平台的样式差异
.container {
  padding: 20rpx;
  
  /* #ifdef H5 */
  max-width: 750px;
  margin: 0 auto;
  /* #endif */
}

// 底部安全区域
.bottom-bar {
  padding-bottom: constant(safe-area-inset-bottom);
  padding-bottom: env(safe-area-inset-bottom);
}
```

### 10.6 H5 部署配置

```javascript
// vite.config.ts
export default defineConfig({
  // H5 部署到子路径时配置
  h5: {
    router: {
      base: '/bioinfo/'  // 如果部署到 https://xxx.com/bioinfo/
    },
    devServer: {
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true
        }
      }
    }
  }
})
```

```json
// manifest.json
{
  "h5": {
    "title": "BioInfo1on1 - 生信导师预约",
    "router": {
      "mode": "history",
      "base": "/"
    },
    "sdkConfigs": {
      "maps": {}
    }
  }
}
```

### 10.7 后端需要新增的 H5 登录接口

```python
# app/routers/auth.py - 新增 H5 登录支持

@router.post("/sms/send")
async def send_sms_code(phone: str):
    """发送短信验证码"""
    code = generate_random_code(6)
    await redis.setex(f"sms:{phone}", 300, code)  # 5分钟有效
    await sms_client.send(phone, code)
    return {"success": True, "message": "验证码已发送"}

@router.post("/sms/verify")
async def verify_sms_code(phone: str, code: str, db: AsyncSession = Depends(get_db)):
    """验证短信验证码并登录"""
    cached_code = await redis.get(f"sms:{phone}")
    if not cached_code or cached_code != code:
        raise HTTPException(status_code=400, detail="验证码错误")
    
    # 查询或创建用户
    user = await crud.get_user_by_phone(db, phone)
    if not user:
        user = await crud.create_user(db, phone=phone)
    
    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "is_new_user": user.nickname is None}
```

---

## 11. 快速启动

```bash
# 安装依赖
npm install

# 开发（微信小程序）
npm run dev:mp-weixin
# 用微信开发者工具打开 dist/dev/mp-weixin

# 开发（H5 网页）
npm run dev:h5
# 浏览器访问 http://localhost:5173

# 构建生产版本
npm run build:h5
# 产物在 dist/build/h5，可部署到任意静态服务器
```

---

## 12. 平台差异速查表

| 功能 | 小程序 | H5 |
|-----|-------|-----|
| 登录方式 | wx.login() | 手机号/微信网页授权 |
| 支付 | wx.requestPayment() | 微信 JSAPI / H5 支付 |
| 分享 | 原生分享按钮 | 自定义分享组件 |
| 扫码 | wx.scanCode() | 需要调用摄像头 API |
| 地图 | 原生 map 组件 | 腾讯地图 JS SDK |
| 推送 | 订阅消息 | WebSocket / 轮询 |

---

**前端文档结束** | 一套代码，小程序 + H5 双端运行 🚀