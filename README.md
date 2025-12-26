# BioInfo1on1 - 生信导师一对一预约平台

## 项目概述

BioInfo1on1 是一个专为生物信息学领域打造的一对一导师预约平台，旨在连接科研工作者与行业专家，通过 AI 智能匹配解决生信分析中的技术难题。

## 技术栈
source bioinfo_env/bin/activate 
### 后端
- **框架**: FastAPI 0.109.0 + Python 3.11
- **ORM**: SQLModel
- **数据库**: PostgreSQL 15+ (支持 JSONB)
- **缓存**: Redis 7
- **AI 引擎**: DeepSeek-V3 / Claude 3.5 (主备双模型)
- **安全**: AES-256 加密 + JWT 认证

### 前端
- **框架**: Uni-app + Vue 3 + TypeScript
- **状态管理**: Pinia
- **目标平台**: 微信小程序 + H5

## 项目结构

```
bioinfo1on1_v2/
├── backend/                 # 后端 FastAPI 项目
│   ├── app/
│   │   ├── main.py         # 应用入口
│   │   ├── models.py       # 数据模型
│   │   ├── schemas.py      # Pydantic 模型
│   │   ├── crud.py         # 数据库操作
│   │   ├── database.py     # 数据库连接
│   │   ├── routers/        # API 路由
│   │   │   ├── auth.py     # 认证接口
│   │   │   ├── mentors.py  # 导师管理
│   │   │   ├── appointments.py  # 订单管理
│   │   │   ├── reviews.py  # 评价系统
│   │   │   └── ai_engine.py     # AI 匹配
│   │   ├── core/           # 核心模块
│   │   │   ├── config.py   # 配置
│   │   │   ├── security.py # 安全模块
│   │   │   ├── ai_client.py     # AI 客户端
│   │   │   └── wechat.py   # 微信 API
│   │   └── utils/          # 工具函数
│   ├── tests/              # 测试用例
│   ├── requirements.txt
│   ├── docker-compose.yml
│   └── .env.example
│
└── frontend/               # 前端 Uni-app 项目
    ├── src/
    │   ├── pages/          # 页面
    │   │   ├── index/      # 首页（导师列表）
    │   │   ├── ai-match/   # AI 智能匹配
    │   │   ├── appointment/     # 订单相关
    │   │   └── user/       # 个人中心
    │   ├── components/     # 公共组件
    │   ├── api/            # API 接口
    │   ├── stores/         # Pinia 状态
    │   ├── types/          # TypeScript 类型
    │   └── utils/          # 工具函数
    ├── package.json
    └── vite.config.ts
```

## 核心功能

### 已完成功能 ✅

#### 后端
1. ✅ 完整的数据库模型设计（Users, Mentors, Appointments, LessonPlans, Reviews）
2. ✅ 微信小程序登录接口 + JWT 认证
3. ✅ AES-256 加密（保护科研代码隐私）
4. ✅ Redis 速率限制
5. ✅ AI 智能匹配引擎（全量上下文注入）
6. ✅ AI 教案自动生成（后台异步任务）
7. ✅ 订单状态机（9 种状态流转）
8. ✅ NDA 保密协议强制校验
9. ✅ 订单 CRUD + 接单/取消/评价流程
10. ✅ 导师入驻申请 + 后台审核
11. ✅ 核心单元测试（状态机、加密、AI 解析）

#### 前端
1. ✅ 首页导师列表展示
2. ✅ AI 智能匹配页（自然语言描述问题）
3. ✅ 创建订单页（含 NDA 签署）
4. ✅ 订单列表页（状态彩色标签）
5. ✅ 个人中心（微信登录）
6. ✅ 请求封装（自动携带 Token + 错误处理）
7. ✅ Pinia 状态管理（用户信息持久化）
8. ✅ TypeScript 类型定义

## 快速开始

### 后端启动

```bash
cd backend

# 复制环境变量
cp .env.example .env
# 编辑 .env 填入实际配置（数据库、微信、AI API Key）

# 安装依赖
pip install -r requirements.txt

# 启动数据库和 Redis（使用 Docker）
docker-compose up -d db redis

# 启动开发服务器
uvicorn app.main:app --reload

# 访问 API 文档
# http://localhost:8000/docs
```

### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 微信小程序开发
npm run dev:mp-weixin
# 用微信开发者工具打开 dist/dev/mp-weixin

# H5 开发
npm run dev:h5
# 浏览器访问 http://localhost:5173
```

### 数据库初始化

应用首次启动时会自动创建所有表结构。你可以手动插入一些测试数据：

```sql
-- 插入测试标签
INSERT INTO tags (name, category, display_order) VALUES
('Python', 'language', 1),
('R', 'language', 2),
('单细胞', 'domain', 1),
('肿瘤免疫', 'domain', 2),
('Seurat', 'tool', 1),
('Scanpy', 'tool', 2);
```

## 环境变量配置

### 后端 (.env)

```bash
# 数据库
DATABASE_URL=postgresql+asyncpg://bioinfo:bioinfo123@localhost:5432/bioinfo1on1
REDIS_URL=redis://localhost:6379/0

# 微信小程序
WX_APP_ID=your_appid
WX_APP_SECRET=your_secret

# AI 引擎
DEEPSEEK_API_KEY=sk-xxxxxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
CLAUDE_API_KEY=sk-ant-xxxxxxxx

# 安全
JWT_SECRET=your-secret-key-at-least-32-chars
AES_ENCRYPTION_KEY=your-fernet-key  # 使用 Fernet.generate_key() 生成
```

### 前端 (.env)

```bash
VITE_API_BASE_URL=http://localhost:8000
```

## API 文档

启动后端后，访问 http://localhost:8000/docs 查看完整的 OpenAPI 文档。

### 核心接口

| 模块 | 方法 | 路径 | 说明 |
|-----|------|------|-----|
| 认证 | POST | `/api/v1/auth/wx-login` | 微信登录 |
| 认证 | GET | `/api/v1/auth/me` | 获取当前用户 |
| 导师 | GET | `/api/v1/mentors` | 导师列表 |
| 导师 | POST | `/api/v1/mentors/apply` | 申请成为导师 |
| AI | POST | `/api/v1/ai/match` | 智能匹配导师 |
| 订单 | POST | `/api/v1/appointments` | 创建订单 |
| 订单 | POST | `/api/v1/appointments/{id}/accept` | 导师接单 |
| 订单 | GET | `/api/v1/appointments/{id}/lesson-plan` | 获取 AI 教案 |

## 测试

### 运行后端测试

```bash
cd backend
pytest tests/ -v
```

测试覆盖：
- ✅ 订单状态机测试（正常流程、非法转换、取消/退款）
- ✅ 加密工具测试（AES 加解密一致性）
- ✅ JWT 测试（Token 生成和验证）
- ✅ AI 响应解析测试（JSON 清洗、Markdown 包裹）

## 核心特性

### 1. AI 智能匹配
- **策略**: 全量上下文注入（Context Stuffing）
- **适用**: 导师数量 < 200 人
- **模型**: DeepSeek-V3（主）+ Claude 3.5（备）
- **降级**: 30秒超时自动切换备用模型

### 2. AI 教案生成
- **触发**: 导师接单后异步生成
- **内容**: 核心概念、操作步骤、报错分析、推荐资源
- **格式**: Markdown

### 3. 数据安全
- **AES-256 加密**: 学员需求代码、手机号
- **NDA 强制签署**: 创建订单必须同意保密协议
- **JWT 认证**: 所有敏感接口需要登录

### 4. 订单状态机
- 9 种状态：待接单 → 已接单 → 待上课 → 上课中 → 待评价 → 已完成
- 支持取消、退款流程
- 超时自动处理

## 部署

### 使用 Docker Compose（推荐）

```bash
cd backend

# 编辑 .env 配置生产环境变量
cp .env.example .env

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f api
```

### 单独部署

#### 后端
```bash
# 使用 gunicorn + uvicorn workers
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### 前端
```bash
# 构建生产版本
npm run build:mp-weixin  # 微信小程序
npm run build:h5         # H5 网页

# H5 产物在 dist/build/h5，可部署到任意静态服务器
```

## 项目亮点

1. **AI 驱动的匹配**: 使用 LLM 进行智能导师推荐，而非传统的规则匹配
2. **保密协议机制**: 强制 NDA 签署 + 代码加密存储，保护科研隐私
3. **双模型降级**: DeepSeek + Claude 确保 AI 服务高可用
4. **状态机设计**: 严格的订单状态流转控制
5. **跨端支持**: 一套代码，微信小程序 + H5 双端运行

## 后续规划

- [ ] 微信支付集成
- [ ] 实时消息推送
- [ ] 导师数据分析仪表盘
- [ ] 评价系统优化
- [ ] 订单详情页完善
- [ ] AI 教案预览页
- [ ] 导师详情页
- [ ] 退款流程
- [ ] 历史偏好学习（AI 匹配优化）

## 开发团队

本项目由 Claude Code（Opus 4.5）全自动开发完成，无人工干预。

## 许可证

MIT License
