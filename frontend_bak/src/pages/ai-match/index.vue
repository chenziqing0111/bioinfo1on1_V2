<template>
  <view class="page">
    <view class="container">
      <!-- 输入区域 -->
      <view class="input-section">
        <view class="title">🤖 描述你的问题</view>
        <textarea
          v-model="requirement"
          placeholder="请详细描述你遇到的生信问题，包括：
- 使用的工具和版本
- 报错信息
- 想要实现的功能
- 已经尝试过的方法

示例：我在用 Seurat 分析单细胞数据时，运行 FindMarkers 报错..."
          :maxlength="2000"
          class="input"
          auto-height
        />
        <view class="char-count">{{ requirement.length }}/2000</view>
      </view>

      <!-- 匹配按钮 -->
      <button
        class="match-btn"
        :disabled="requirement.length < 20 || matching"
        :class="{ disabled: requirement.length < 20 || matching }"
        @click="doMatch"
      >
        {{ matching ? '匹配中...' : '🎯 开始智能匹配' }}
      </button>

      <!-- 匹配结果 -->
      <view v-if="matchResult" class="result-section">
        <view class="title">✨ 为你推荐以下导师</view>

        <view
          v-for="(item, index) in matchResult.recommendations"
          :key="item.mentor_id"
          class="recommendation-card"
        >
          <view class="rank-badge">TOP {{ index + 1 }}</view>
          <view class="score-bar">
            <text class="score-label">匹配度</text>
            <view class="score-progress">
              <view
                class="score-fill"
                :style="{ width: (item.score * 100) + '%' }"
              ></view>
            </view>
            <text class="score-value">{{ (item.score * 100).toFixed(0) }}%</text>
          </view>

          <view class="reason">
            <text class="reason-title">推荐理由：</text>
            <text class="reason-content">{{ item.reason }}</text>
          </view>

          <view class="can-solve" v-if="item.can_solve && item.can_solve.length > 0">
            <text class="can-solve-title">可以解决：</text>
            <view class="solve-list">
              <text
                v-for="(solve, idx) in item.can_solve"
                :key="idx"
                class="solve-item"
              >
                • {{ solve }}
              </text>
            </view>
          </view>

          <button class="btn-book" @click="goBook(item.mentor_id)">
            立即预约
          </button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { aiApi } from '@/api/ai'
import { useUserStore } from '@/stores/user'
import type { MatchResult } from '@/types/ai'

const userStore = useUserStore()
const requirement = ref('')
const matching = ref(false)
const matchResult = ref<MatchResult | null>(null)

async function doMatch() {
  if (!userStore.checkLogin()) return

  if (requirement.value.length < 20) {
    uni.showToast({
      title: '请至少输入20个字符',
      icon: 'none'
    })
    return
  }

  matching.value = true
  matchResult.value = null

  try {
    const result = await aiApi.match(requirement.value)
    matchResult.value = result
  } catch (error: any) {
    uni.showToast({
      title: error.message || 'AI匹配失败',
      icon: 'none'
    })
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

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background: #f5f5f5;
}

.container {
  padding: 40rpx;
}

.input-section {
  background: white;
  border-radius: 16rpx;
  padding: 32rpx;
  margin-bottom: 32rpx;

  .title {
    font-size: 32rpx;
    font-weight: 600;
    margin-bottom: 24rpx;
    color: #333;
  }

  .input {
    width: 100%;
    min-height: 300rpx;
    padding: 20rpx;
    border: 2rpx solid #e0e0e0;
    border-radius: 12rpx;
    font-size: 28rpx;
    line-height: 1.6;
  }

  .char-count {
    margin-top: 12rpx;
    text-align: right;
    font-size: 24rpx;
    color: #999;
  }
}

.match-btn {
  width: 100%;
  background: linear-gradient(135deg, #2B579A 0%, #3D6FB8 100%);
  color: white;
  border: none;
  border-radius: 12rpx;
  font-size: 32rpx;
  font-weight: 600;
  padding: 28rpx 0;
  margin-bottom: 40rpx;

  &.disabled {
    opacity: 0.5;
  }
}

.result-section {
  .title {
    font-size: 32rpx;
    font-weight: 600;
    margin-bottom: 32rpx;
    color: #333;
  }
}

.recommendation-card {
  background: white;
  border-radius: 16rpx;
  padding: 32rpx;
  margin-bottom: 32rpx;
  position: relative;

  .rank-badge {
    position: absolute;
    top: -12rpx;
    right: 32rpx;
    background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
    color: white;
    padding: 8rpx 24rpx;
    border-radius: 24rpx;
    font-size: 24rpx;
    font-weight: 600;
  }

  .score-bar {
    display: flex;
    align-items: center;
    gap: 16rpx;
    margin-bottom: 24rpx;
    margin-top: 20rpx;

    .score-label {
      font-size: 26rpx;
      color: #666;
      flex-shrink: 0;
    }

    .score-progress {
      flex: 1;
      height: 16rpx;
      background: #f0f0f0;
      border-radius: 8rpx;
      overflow: hidden;

      .score-fill {
        height: 100%;
        background: linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%);
        transition: width 0.3s ease;
      }
    }

    .score-value {
      font-size: 28rpx;
      font-weight: 600;
      color: #4CAF50;
      flex-shrink: 0;
    }
  }

  .reason {
    margin-bottom: 24rpx;

    .reason-title {
      display: block;
      font-size: 26rpx;
      font-weight: 600;
      color: #333;
      margin-bottom: 12rpx;
    }

    .reason-content {
      display: block;
      font-size: 28rpx;
      line-height: 1.6;
      color: #666;
    }
  }

  .can-solve {
    margin-bottom: 24rpx;

    .can-solve-title {
      display: block;
      font-size: 26rpx;
      font-weight: 600;
      color: #333;
      margin-bottom: 12rpx;
    }

    .solve-list {
      .solve-item {
        display: block;
        font-size: 26rpx;
        line-height: 1.8;
        color: #666;
      }
    }
  }

  .btn-book {
    width: 100%;
    background: #2B579A;
    color: white;
    border: none;
    border-radius: 8rpx;
    font-size: 28rpx;
    padding: 20rpx 0;
  }
}
</style>
