<template>
  <view class="page">
    <!-- 加载状态 -->
    <view v-if="loading" class="loading-container">
      <view class="loading-animation">
        <view class="dot"></view>
        <view class="dot"></view>
        <view class="dot"></view>
      </view>
      <text class="loading-text">AI 正在生成教案...</text>
      <text class="loading-hint">这可能需要几秒钟时间</text>
    </view>

    <!-- 教案内容 -->
    <template v-else-if="lessonPlan">
      <view class="container">
        <!-- 信息标签 -->
        <view class="info-bar">
          <view v-if="lessonPlan.model_name" class="info-tag model">
            <text>{{ lessonPlan.model_name }}</text>
          </view>
          <view v-if="lessonPlan.is_fallback" class="info-tag fallback">
            <text>备用模型</text>
          </view>
          <text class="create-time">生成于 {{ formatDate(lessonPlan.created_at) }}</text>
        </view>

        <!-- Markdown 内容 -->
        <view class="content-card">
          <rich-text class="markdown-content" :nodes="renderedContent"></rich-text>
        </view>
      </view>
    </template>

    <!-- 空状态 / 生成中 -->
    <view v-else-if="generating" class="loading-container">
      <view class="loading-animation">
        <view class="dot"></view>
        <view class="dot"></view>
        <view class="dot"></view>
      </view>
      <text class="loading-text">教案生成中...</text>
      <text class="loading-hint">请稍后刷新查看</text>
      <button class="btn-refresh" @click="loadData">刷新</button>
    </view>

    <!-- 错误状态 -->
    <view v-else class="error">
      <text class="error-text">教案暂未生成</text>
      <text class="error-hint">教案将在导师接单后自动生成</text>
      <button class="btn-retry" @click="loadData">重试</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { appointmentApi } from '@/api/appointment'
import type { LessonPlan } from '@/types/appointment'

const lessonPlan = ref<LessonPlan | null>(null)
const loading = ref(true)
const generating = ref(false)
const appointmentId = ref('')

onMounted(() => {
  // 获取页面参数
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1] as any
  const options = currentPage.options || {}

  appointmentId.value = options.id

  if (!appointmentId.value) {
    uni.showToast({
      title: '缺少订单ID',
      icon: 'none'
    })
    setTimeout(() => {
      uni.navigateBack()
    }, 1500)
    return
  }

  loadData()
})

async function loadData() {
  loading.value = true
  generating.value = false
  try {
    lessonPlan.value = await appointmentApi.getLessonPlan(appointmentId.value)
  } catch (error: any) {
    console.error('加载教案失败', error)
    // 检查是否是教案还在生成中
    if (error.message?.includes('生成中') || error.message?.includes('generating')) {
      generating.value = true
    }
    lessonPlan.value = null
  } finally {
    loading.value = false
  }
}

// 简单的 Markdown 转 HTML
function parseMarkdown(md: string): string {
  if (!md) return ''

  let html = md
    // 转义 HTML 特殊字符
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')

    // 标题
    .replace(/^### (.+)$/gm, '<h3 class="md-h3">$1</h3>')
    .replace(/^## (.+)$/gm, '<h2 class="md-h2">$1</h2>')
    .replace(/^# (.+)$/gm, '<h1 class="md-h1">$1</h1>')

    // 粗体和斜体
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/__(.+?)__/g, '<strong>$1</strong>')
    .replace(/_(.+?)_/g, '<em>$1</em>')

    // 行内代码
    .replace(/`([^`]+)`/g, '<code class="md-code">$1</code>')

    // 无序列表
    .replace(/^[\-\*] (.+)$/gm, '<li class="md-li">$1</li>')

    // 有序列表
    .replace(/^\d+\. (.+)$/gm, '<li class="md-li">$1</li>')

    // 分隔线
    .replace(/^---$/gm, '<hr class="md-hr"/>')

    // 换行
    .replace(/\n\n/g, '</p><p class="md-p">')
    .replace(/\n/g, '<br/>')

  // 包装段落
  html = '<p class="md-p">' + html + '</p>'

  // 清理空段落
  html = html.replace(/<p class="md-p"><\/p>/g, '')
  html = html.replace(/<p class="md-p"><br\/>/g, '<p class="md-p">')

  // 包装列表项
  html = html.replace(/(<li class="md-li">.*?<\/li>)+/gs, (match) => {
    return '<ul class="md-ul">' + match + '</ul>'
  })

  return html
}

const renderedContent = computed(() => {
  if (!lessonPlan.value?.content_md) return ''
  return parseMarkdown(lessonPlan.value.content_md)
})

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background: #f5f5f5;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 160rpx 40rpx;

  .loading-animation {
    display: flex;
    gap: 16rpx;
    margin-bottom: 40rpx;

    .dot {
      width: 20rpx;
      height: 20rpx;
      background: #2B579A;
      border-radius: 50%;
      animation: bounce 1.4s infinite ease-in-out;

      &:nth-child(1) {
        animation-delay: -0.32s;
      }

      &:nth-child(2) {
        animation-delay: -0.16s;
      }
    }
  }

  .loading-text {
    font-size: 32rpx;
    font-weight: 600;
    color: #333;
    margin-bottom: 16rpx;
  }

  .loading-hint {
    font-size: 26rpx;
    color: #999;
    margin-bottom: 40rpx;
  }

  .btn-refresh {
    background: #2B579A;
    color: white;
    border: none;
    border-radius: 48rpx;
    font-size: 28rpx;
    padding: 20rpx 60rpx;
  }
}

@keyframes bounce {
  0%,
  80%,
  100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.container {
  padding: 40rpx;
}

.info-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 16rpx;
  margin-bottom: 24rpx;

  .info-tag {
    padding: 8rpx 20rpx;
    border-radius: 24rpx;
    font-size: 24rpx;

    &.model {
      background: #f0f5ff;
      color: #2B579A;
    }

    &.fallback {
      background: #fff3cd;
      color: #856404;
    }
  }

  .create-time {
    font-size: 24rpx;
    color: #999;
    margin-left: auto;
  }
}

.content-card {
  background: white;
  border-radius: 16rpx;
  padding: 32rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.markdown-content {
  font-size: 28rpx;
  line-height: 1.8;
  color: #333;

  :deep(.md-h1) {
    font-size: 40rpx;
    font-weight: 700;
    color: #1a1a1a;
    margin: 32rpx 0 20rpx;
    padding-bottom: 16rpx;
    border-bottom: 2rpx solid #e0e0e0;
  }

  :deep(.md-h2) {
    font-size: 34rpx;
    font-weight: 600;
    color: #2B579A;
    margin: 28rpx 0 16rpx;
  }

  :deep(.md-h3) {
    font-size: 30rpx;
    font-weight: 600;
    color: #333;
    margin: 24rpx 0 12rpx;
  }

  :deep(.md-p) {
    margin: 16rpx 0;
  }

  :deep(.md-ul) {
    margin: 16rpx 0;
    padding-left: 40rpx;
  }

  :deep(.md-li) {
    margin: 8rpx 0;
    position: relative;

    &::before {
      content: '•';
      position: absolute;
      left: -24rpx;
      color: #2B579A;
    }
  }

  :deep(.md-code) {
    background: #f5f5f5;
    padding: 4rpx 12rpx;
    border-radius: 8rpx;
    font-family: monospace;
    font-size: 26rpx;
    color: #e83e8c;
  }

  :deep(.md-hr) {
    border: none;
    border-top: 2rpx solid #e0e0e0;
    margin: 32rpx 0;
  }

  :deep(strong) {
    font-weight: 600;
    color: #1a1a1a;
  }

  :deep(em) {
    font-style: italic;
  }
}

.error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 160rpx 40rpx;

  .error-text {
    font-size: 32rpx;
    font-weight: 600;
    color: #333;
    margin-bottom: 16rpx;
  }

  .error-hint {
    font-size: 26rpx;
    color: #999;
    margin-bottom: 40rpx;
    text-align: center;
  }

  .btn-retry {
    background: #2B579A;
    color: white;
    border: none;
    border-radius: 48rpx;
    font-size: 28rpx;
    padding: 20rpx 60rpx;
  }
}
</style>
