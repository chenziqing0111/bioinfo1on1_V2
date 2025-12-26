# BioInfo1on1 技术开发文档 V2.0

> **文档版本**: 2.0 | **状态**: 生产就绪 | **适用于**: Claude Code / Cursor / Windsurf

---

## 1. 项目概览与战略定位

### 1.1 产品定义

**BioInfo1on1** 是生物信息学垂直领域的一对一导师预约平台，旨在连接科研工作者与行业专家，解决生信分析中的技术难题。

### 1.2 核心痛点

- **需求描述模糊**: 学员难以准确表达技术问题，导致匹配效率低
- **专家匹配困难**: 生信领域细分方向众多，人工匹配耗时且不精准
- **课前准备繁重**: 导师需要花费大量时间理解学员背景和问题
- **科研代码保密**: 学员担心代码和数据泄露，不敢分享完整上下文

### 1.3 AI 落地策略

**匹配引擎 (Concierge)**
鉴于初期导师规模（<200人），采用「全量上下文注入 (Context Stuffing)」策略。将所有导师画像（JSON）直接输入 LLM 窗口进行全局最优匹配，确保匹配精度和推理完整性，而非使用 RAG 方案。

**教案引擎 (Lesson Architect)**
基于学员提交的背景、报错代码和需求描述，自动生成 Markdown 格式的教学大纲，减轻导师备课负担。

### 1.4 MVP 范围定义

| 功能模块 | MVP 包含 | 后续迭代 |
|---------|---------|---------|
| 用户系统 | 微信登录、角色区分 | 手机号绑定、多端同步 |
| 导师管理 | 入驻申请、后台审核 | 自助修改、数据分析 |
| 智能匹配 | AI 推荐 Top 3 | 历史偏好学习 |
| 订单流程 | 下单、接单、上课、评价 | 退款、投诉、仲裁 |
| 支付系统 | 接口预留 | 微信支付集成 |
| AI 教案 | 自动生成 Markdown | 模板定制、导出 PDF |

---

## 2. 系统架构设计

### 2.1 技术栈选型

| 层级 | 技术选型 | 选型理由 |
|-----|---------|---------|
| 后端框架 | Python 3.11 + FastAPI | 异步高性能、自动生成 OpenAPI 文档 |
| ORM | SQLModel | 融合 Pydantic + SQLAlchemy，类型安全 |
| 数据库 | PostgreSQL 15+ | JSONB 支持、全文检索、成熟稳定 |
| 缓存 | Redis 7 | 会话管理、速率限制、消息队列 |
| 前端 | Uni-app (Vue 3) | 跨端开发，便于后续扩展 Web/App |
| AI 引擎 | DeepSeek-V3 / Claude 3.5 | 主备双模型，确保服务可用性 |
| 对象存储 | 阿里云 OSS | 存储用户头像、附件等静态资源 |

### 2.2 项目目录结构

```
bioinfo1on1-backend/
├── app/
│   ├── main.py                 # FastAPI 应用入口
│   ├── models.py               # SQLModel 数据模型
│   ├── schemas.py              # Pydantic 请求/响应模型
│   ├── crud.py                 # 数据库 CRUD 操作
│   ├── database.py             # 数据库连接配置
│   ├── routers/
│   │   ├── auth.py             # 认证与授权
│   │   ├── users.py            # 用户管理
│   │   ├── mentors.py          # 导师管理
│   │   ├── appointments.py     # 订单管理
│   │   ├── reviews.py          # 评价系统
│   │   └── ai_engine.py        # AI 匹配与教案
│   ├── core/
│   │   ├── config.py           # 配置管理
│   │   ├── security.py         # 安全与加密
│   │   ├── ai_client.py        # LLM 客户端封装
│   │   └── wechat.py           # 微信 API 封装
│   └── utils/
│       ├── rate_limiter.py     # 速率限制
│       └── background_tasks.py # 异步任务
├── tests/                      # 测试用例
├── docker-compose.yml          # 容器编排
├── Dockerfile
├── requirements.txt
└── .env.example                # 环境变量模板
```

---

## 3. 数据库模型设计

### 3.1 ER 关系概览

```
Users (1) ←→ (0..1) Mentors ←→ (N) MentorTags ←→ (N) Tags
Users (1) ←→ (N) Appointments ←→ (1) Mentors
Appointments (1) ←→ (0..1) LessonPlans
Appointments (1) ←→ (0..2) Reviews
```

### 3.2 Users 表 - 用户基础表

```python
class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    openid: str = Field(max_length=64, unique=True, index=True)
    role: UserRole = Field(default=UserRole.STUDENT)  # student/tutor/admin
    nickname: str | None = Field(max_length=50)
    avatar_url: str | None = Field(max_length=500)
    phone: str | None = Field(max_length=100)  # AES 加密存储
    bio: str | None = Field(default=None)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### 3.3 Mentors 表 - 导师详情表

```python
class Mentor(SQLModel, table=True):
    __tablename__ = "mentors"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", unique=True)
    title: str | None = Field(max_length=100)  # 职称
    institution: str | None = Field(max_length=200)  # 所属机构
    honors: str | None = Field(default=None)  # 荣誉与成就
    resume_json: dict = Field(sa_column=Column(JSONB), default={})
    hourly_rate: Decimal = Field(max_digits=10, decimal_places=2)
    available_slots: dict | None = Field(sa_column=Column(JSONB))
    rating: Decimal = Field(default=5.0, max_digits=2, decimal_places=1)
    total_sessions: int = Field(default=0)
    audit_status: AuditStatus = Field(default=AuditStatus.PENDING)
    audit_note: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### 3.4 Tags 表 - 技能标签表

```python
class Tag(SQLModel, table=True):
    __tablename__ = "tags"
    
    id: int = Field(primary_key=True)
    name: str = Field(max_length=50, unique=True)
    category: TagCategory  # language/domain/tool
    display_order: int = Field(default=0)

class MentorTag(SQLModel, table=True):
    """多对多关联表"""
    __tablename__ = "mentor_tags"
    
    mentor_id: UUID = Field(foreign_key="mentors.id", primary_key=True)
    tag_id: int = Field(foreign_key="tags.id", primary_key=True)
```

**预置标签示例**:
- `language`: Python, R, Shell, Nextflow, WDL
- `domain`: 单细胞, 肿瘤免疫, 宏基因组, 蛋白质组, 空间转录组
- `tool`: Seurat, Scanpy, GATK, cellranger, DESeq2

### 3.5 Appointments 表 - 订单表

```python
class Appointment(SQLModel, table=True):
    __tablename__ = "appointments"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    order_no: str = Field(max_length=32, unique=True, index=True)
    learner_id: UUID = Field(foreign_key="users.id")
    mentor_id: UUID = Field(foreign_key="mentors.id")
    status: AppointmentStatus = Field(default=AppointmentStatus.PENDING_ACCEPT)
    price: Decimal = Field(max_digits=10, decimal_places=2)
    duration_minutes: int = Field(default=60)
    scheduled_time: datetime | None = Field(default=None)
    meeting_link: str | None = Field(max_length=500)
    requirements: str | None = Field(default=None)  # AES-256 加密
    accept_nda: bool = Field(default=False)
    nda_signed_at: datetime | None = Field(default=None)
    cancel_reason: str | None = Field(default=None)
    cancelled_by: UUID | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### 3.6 LessonPlans 表 - AI 教案表

```python
class LessonPlan(SQLModel, table=True):
    __tablename__ = "lesson_plans"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    appointment_id: UUID = Field(foreign_key="appointments.id", unique=True)
    content_md: str  # Markdown 教案内容
    model_name: str | None = Field(max_length=50)
    input_tokens: int | None = Field(default=None)
    output_tokens: int | None = Field(default=None)
    is_fallback: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### 3.7 Reviews 表 - 评价表

```python
class Review(SQLModel, table=True):
    __tablename__ = "reviews"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    appointment_id: UUID = Field(foreign_key="appointments.id")
    reviewer_id: UUID = Field(foreign_key="users.id")
    reviewee_id: UUID = Field(foreign_key="users.id")
    rating: Decimal = Field(max_digits=2, decimal_places=1)  # 1.0-5.0
    content: str | None = Field(default=None)
    is_anonymous: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

# 联合唯一约束: 每个订单每人只能评价一次
__table_args__ = (
    UniqueConstraint('appointment_id', 'reviewer_id'),
)
```

### 3.8 resume_json JSONB Schema

```json
{
  "education": [
    {"degree": "博士", "major": "生物信息学", "school": "北京大学", "year": 2020}
  ],
  "experience": [
    {"role": "副研究员", "org": "中科院", "years": "2020-至今"}
  ],
  "publications": [
    {"title": "...", "journal": "Nature", "year": 2023, "citations": 150}
  ],
  "skills": {
    "languages": ["Python", "R"],
    "domains": ["单细胞", "肿瘤免疫"],
    "tools": ["Seurat", "GATK"]
  },
  "specialties": ["10x Genomics 分析", "CNV 检测", "肿瘤突变负荷"]
}
```

### 3.9 枚举定义

```python
from enum import Enum

class UserRole(str, Enum):
    STUDENT = "student"
    TUTOR = "tutor"
    ADMIN = "admin"

class AuditStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class TagCategory(str, Enum):
    LANGUAGE = "language"
    DOMAIN = "domain"
    TOOL = "tool"

class AppointmentStatus(str, Enum):
    PENDING_ACCEPT = "pending_accept"  # 待接单
    ACCEPTED = "accepted"              # 已接单
    TO_ATTEND = "to_attend"            # 待上课
    IN_PROGRESS = "in_progress"        # 上课中
    EVALUATING = "evaluating"          # 待评价
    COMPLETED = "completed"            # 已完成
    CANCELLED = "cancelled"            # 已取消
    REFUNDING = "refunding"            # 退款中
    REFUNDED = "refunded"              # 已退款
```

---

## 4. API 接口规范

### 4.1 认证模块 `/api/v1/auth`

| 方法 | 路径 | 描述 | 请求体/参数 |
|-----|------|------|-----------|
| POST | `/wx-login` | 微信登录 | `{code: string}` |
| POST | `/refresh` | 刷新 Token | `{refresh_token: string}` |
| GET | `/me` | 获取当前用户 | - |

### 4.2 用户模块 `/api/v1/users`

| 方法 | 路径 | 描述 | 备注 |
|-----|------|------|-----|
| GET | `/{user_id}` | 获取用户信息 | - |
| PUT | `/{user_id}` | 更新用户信息 | 仅限本人 |

### 4.3 导师模块 `/api/v1/mentors`

| 方法 | 路径 | 描述 | 备注 |
|-----|------|------|-----|
| GET | `/` | 导师列表 | 支持分页、筛选 |
| GET | `/{mentor_id}` | 导师详情 | - |
| POST | `/apply` | 申请成为导师 | 需登录 |
| PUT | `/{mentor_id}/audit` | 审核导师 | 仅管理员 |
| GET | `/tags` | 获取所有标签 | 按类别分组 |

### 4.4 订单模块 `/api/v1/appointments`

| 方法 | 路径 | 描述 | 备注 |
|-----|------|------|-----|
| POST | `/` | 创建订单 | 需签署 NDA |
| GET | `/` | 我的订单列表 | 学员/导师视角 |
| GET | `/{appt_id}` | 订单详情 | - |
| POST | `/{appt_id}/accept` | 导师接单 | 触发 AI 教案 |
| POST | `/{appt_id}/cancel` | 取消订单 | 需填写原因 |
| PUT | `/{appt_id}/meeting-link` | 设置会议链接 | 仅导师 |
| GET | `/{appt_id}/lesson-plan` | 获取 AI 教案 | - |

### 4.5 AI 模块 `/api/v1/ai`

| 方法 | 路径 | 描述 | 备注 |
|-----|------|------|-----|
| POST | `/match` | 智能匹配导师 | 返回 Top 3 |
| POST | `/generate-lesson-plan` | 生成教案 | 内部调用 |

### 4.6 评价模块 `/api/v1/reviews`

| 方法 | 路径 | 描述 | 备注 |
|-----|------|------|-----|
| POST | `/` | 提交评价 | 课程结束后 |
| GET | `/mentor/{mentor_id}` | 导师评价列表 | 公开展示 |

### 4.7 统一响应格式

```python
# 成功响应
{
    "success": True,
    "data": {...},
    "message": "操作成功"
}

# 错误响应
{
    "success": False,
    "error": {
        "code": 2001,
        "message": "订单已被接单"
    },
    "data": None
}
```

---

## 5. 订单状态机与业务流程

### 5.1 状态定义

| 状态值 | 显示名称 | 说明 |
|-------|---------|-----|
| `pending_accept` | 待接单 | 学员已下单，等待导师确认 |
| `accepted` | 已接单 | 导师已接单，触发 AI 生成教案 |
| `to_attend` | 待上课 | 已设置会议链接，等待上课时间 |
| `in_progress` | 上课中 | 到达预约时间，课程进行中 |
| `evaluating` | 待评价 | 课程结束，等待双方评价 |
| `completed` | 已完成 | 双方评价完成或评价超时自动完成 |
| `cancelled` | 已取消 | 订单被取消（需记录原因和操作人） |
| `refunding` | 退款中 | 已发起退款，等待处理 |
| `refunded` | 已退款 | 退款完成 |

### 5.2 状态流转规则

```
正常流程: pending_accept → accepted → to_attend → in_progress → evaluating → completed

取消流程: pending_accept → cancelled (学员/导师主动取消)

退款流程: accepted/to_attend → refunding → refunded/cancelled

超时规则: 
- pending_accept 超过 24 小时未接单自动取消
- evaluating 超过 7 天未评价自动完成
```

### 5.3 状态流转图 (Mermaid)

```mermaid
stateDiagram-v2
    [*] --> pending_accept: 学员下单 (已签NDA)
    pending_accept --> accepted: 导师接单
    pending_accept --> cancelled: 超时/主动取消
    accepted --> to_attend: 设置会议链接
    accepted --> refunding: 申请退款
    to_attend --> in_progress: 到达上课时间
    to_attend --> refunding: 申请退款
    in_progress --> evaluating: 课程结束
    evaluating --> completed: 评价完成/超时
    refunding --> refunded: 退款成功
    refunding --> cancelled: 退款失败
    cancelled --> [*]
    completed --> [*]
    refunded --> [*]
```

### 5.4 状态变更触发器

| 状态变更 | 触发动作 | 实现方式 |
|---------|---------|---------|
| → accepted | 生成 AI 教案 | BackgroundTasks 异步执行 |
| → accepted | 发送订阅消息 | 微信模板消息推送给学员 |
| → to_attend | 发送上课提醒 | 提前 30 分钟推送 |
| → evaluating | 开放评价入口 | 双方可互评 |
| → completed | 更新导师评分 | 重新计算加权平均分 |

---

## 6. 微信生态集成

### 6.1 微信登录流程

```python
# 1. 小程序端调用 wx.login() 获取临时 code
# 2. 小程序将 code 发送到后端

@router.post("/wx-login")
async def wx_login(code: str, db: AsyncSession = Depends(get_db)):
    # 3. 调用微信 code2Session 接口
    url = "https://api.weixin.qq.com/sns/jscode2session"
    params = {
        "appid": settings.WX_APP_ID,
        "secret": settings.WX_APP_SECRET,
        "js_code": code,
        "grant_type": "authorization_code"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()
    
    if "errcode" in data:
        raise HTTPException(status_code=401, detail="微信登录失败")
    
    openid = data["openid"]
    session_key = data["session_key"]  # 用于解密用户信息，不要返回给前端
    
    # 4. 查询或创建用户
    user = await crud.get_user_by_openid(db, openid)
    if not user:
        user = await crud.create_user(db, openid=openid)
    
    # 5. 生成 JWT Token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "is_new_user": user.nickname is None
    }
```

### 6.2 订阅消息配置

| 消息场景 | 触发时机 | 模板字段 |
|---------|---------|---------|
| 预约成功通知 | 导师接单后 | 导师姓名、预约时间、课程主题 |
| 上课提醒 | 上课前 30 分钟 | 导师姓名、上课时间、会议链接 |
| 评价邀请 | 课程结束后 | 课程主题、完成时间 |

```python
async def send_subscribe_message(openid: str, template_id: str, data: dict):
    """发送微信订阅消息"""
    access_token = await get_wx_access_token()
    url = f"https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token={access_token}"
    
    payload = {
        "touser": openid,
        "template_id": template_id,
        "data": data,
        "miniprogram_state": "formal"  # developer/trial/formal
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        return response.json()
```

### 6.3 微信支付接口预留

MVP 阶段暂不集成微信支付，但需预留以下字段和逻辑：

- `order_no`: 业务订单号，格式 `BI{timestamp}{random}`，用于微信支付 `out_trade_no`
- `transaction_id`: 微信支付订单号，支付成功后回填
- `pay_status`: 支付状态枚举 `unpaid / paid / refunded`
- 回调接口: `POST /api/v1/payments/wx-notify` 处理微信异步通知

---

## 7. AI 智能模块

### 7.1 智能匹配引擎 (Concierge)

**策略**: 全量上下文注入 (Context Stuffing)

**适用条件**: 导师数量 < 200 人，预估每人 ~300 tokens，总计 ~60k tokens

```python
MATCH_SYSTEM_PROMPT = """
你是 BioInfo1on1 平台的生物信息学专家顾问。

## 任务
根据学员的需求，从导师列表中选出最匹配的 3 位导师。

## 匹配原则
1. 技术栈匹配：优先选择掌握学员所需编程语言和工具的导师
2. 领域匹配：优先选择研究方向与学员问题相关的导师
3. 经验匹配：根据问题复杂度选择相应资历的导师

## 导师列表
{mentor_json}

## 学员需求
{user_requirement}

## 输出格式（严格 JSON，不要添加任何其他内容）
{
  "recommendations": [
    {
      "mentor_id": "uuid-string",
      "score": 0.95,
      "reason": "基于导师背景的具体推荐理由",
      "can_solve": ["能解决的问题1", "能解决的问题2"]
    }
  ]
}
"""
```

**实现代码**:

```python
@router.post("/match")
async def ai_match(
    request: MatchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. 获取所有已审核导师
    mentors = await crud.get_approved_mentors(db)
    mentor_json = json.dumps([m.to_match_dict() for m in mentors], ensure_ascii=False)
    
    # 2. 构造 Prompt
    prompt = MATCH_SYSTEM_PROMPT.format(
        mentor_json=mentor_json,
        user_requirement=request.requirement
    )
    
    # 3. 调用 AI（带降级逻辑）
    try:
        result = await ai_client.chat(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            timeout=30
        )
    except asyncio.TimeoutError:
        # 降级到备用模型
        result = await ai_client.chat(
            model="claude-3-5-sonnet",
            messages=[{"role": "user", "content": prompt}],
            timeout=60
        )
    
    # 4. 解析结果
    recommendations = parse_ai_response(result)
    
    return {"success": True, "data": recommendations}
```

### 7.2 教案生成引擎 (Lesson Architect)

**触发时机**: 订单状态变为 `accepted` 时异步执行

```python
LESSON_PLAN_PROMPT = """
你是一位资深的生物信息学教学专家。

## 学员背景与需求
{requirements}

## 任务
请为导师生成一份 60 分钟的授课教案，使用 Markdown 格式，包含以下章节：

### 1. 核心概念预习
列出学员需要提前了解的 3-5 个知识点，每个知识点附带简短解释。

### 2. 操作步骤建议
按时间顺序列出代码演示的步骤，包括：
- 环境准备（5分钟）
- 核心讲解（40分钟）
- 实践练习（10分钟）
- 答疑总结（5分钟）

### 3. 报错分析思路
针对学员提供的报错信息，给出：
- 可能的原因
- 排查步骤
- 解决方案

### 4. 推荐资源
列出 3-5 个相关的：
- 官方文档链接
- 经典教程
- 生信论文（如适用）

输出格式：纯 Markdown，不要包含代码块标记。
"""
```

**异步任务实现**:

```python
async def generate_lesson_plan_task(appointment_id: UUID, requirements: str):
    """后台任务：生成 AI 教案"""
    async with get_db_session() as db:
        try:
            result = await ai_client.chat(
                model="deepseek-chat",
                messages=[{"role": "user", "content": LESSON_PLAN_PROMPT.format(requirements=requirements)}],
                timeout=60
            )
            
            lesson_plan = LessonPlan(
                appointment_id=appointment_id,
                content_md=result.content,
                model_name=result.model,
                input_tokens=result.usage.input_tokens,
                output_tokens=result.usage.output_tokens,
                is_fallback=False
            )
            
        except Exception as e:
            # 降级到备用模型
            result = await ai_client.chat(
                model="claude-3-5-sonnet",
                messages=[{"role": "user", "content": LESSON_PLAN_PROMPT.format(requirements=requirements)}]
            )
            
            lesson_plan = LessonPlan(
                appointment_id=appointment_id,
                content_md=result.content,
                model_name="claude-3-5-sonnet",
                input_tokens=result.usage.input_tokens,
                output_tokens=result.usage.output_tokens,
                is_fallback=True
            )
            
            # 记录降级事件
            logger.warning(f"AI fallback for appointment {appointment_id}: {e}")
        
        db.add(lesson_plan)
        await db.commit()
```

### 7.3 降级与容错策略

| 异常场景 | 处理策略 | 日志记录 |
|---------|---------|---------|
| 主模型超时 (>30s) | 切换备用模型 | 记录 `fallback_event` |
| 返回非标准 JSON | 正则清洗后重试 | 记录 `parse_error` |
| API 余额不足 | 告警通知 + 人工介入 | 记录 `quota_exceeded` |
| 重试 3 次仍失败 | 返回友好提示 | 记录 `total_failure` |

```python
def parse_ai_response(content: str) -> dict:
    """解析 AI 返回的 JSON，带清洗逻辑"""
    # 移除可能的 markdown 代码块标记
    content = re.sub(r'^```json\s*', '', content)
    content = re.sub(r'\s*```$', '', content)
    
    # 尝试解析
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # 尝试提取 JSON 部分
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError("无法解析 AI 响应")
```

### 7.4 成本监控

```python
# 每次 AI 调用后记录
async def log_ai_usage(
    model: str,
    input_tokens: int,
    output_tokens: int,
    endpoint: str,
    user_id: UUID
):
    """记录 AI 调用成本"""
    # 价格配置（每千 tokens）
    PRICING = {
        "deepseek-chat": {"input": 0.001, "output": 0.002},
        "claude-3-5-sonnet": {"input": 0.003, "output": 0.015}
    }
    
    price = PRICING.get(model, {"input": 0, "output": 0})
    cost = (input_tokens * price["input"] + output_tokens * price["output"]) / 1000
    
    # 存入数据库或发送到监控系统
    await metrics.record("ai_usage", {
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": cost,
        "endpoint": endpoint,
        "user_id": str(user_id)
    })
```

---

## 8. 安全规范与合规

### 8.1 数据加密

| 数据类型 | 加密方式 | 说明 |
|---------|---------|-----|
| 用户手机号 | AES-256 (Fernet) | 存储加密，读取解密 |
| 学员需求代码 | AES-256 (Fernet) | 保护科研代码不被泄露 |
| JWT Token | HS256 签名 | 使用 JWT_SECRET 签名 |
| 数据库连接 | SSL/TLS | 生产环境强制加密 |

```python
# app/core/security.py
from cryptography.fernet import Fernet
from passlib.context import CryptContext
import jwt

class Encryptor:
    """AES-256 加密工具"""
    
    def __init__(self, key: str):
        self.fernet = Fernet(key.encode())
    
    def encrypt(self, plaintext: str) -> str:
        return self.fernet.encrypt(plaintext.encode()).decode()
    
    def decrypt(self, ciphertext: str) -> str:
        return self.fernet.decrypt(ciphertext.encode()).decode()

# 初始化
encryptor = Encryptor(settings.AES_ENCRYPTION_KEY)

# 使用示例
encrypted_code = encryptor.encrypt(user_code)
decrypted_code = encryptor.decrypt(encrypted_code)
```

### 8.2 速率限制 (Rate Limiting)

| 接口 | 限制策略 | 备注 |
|-----|---------|-----|
| `/api/v1/ai/match` | 10 次/分钟/用户 | 防止滥用 AI 资源 |
| `/api/v1/auth/wx-login` | 5 次/分钟/IP | 防止暴力登录 |
| 其他接口 | 100 次/分钟/用户 | 通用限制 |

```python
# app/utils/rate_limiter.py
from fastapi import Request, HTTPException
import redis.asyncio as redis

class RateLimiter:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    async def check(self, key: str, limit: int, window: int = 60) -> bool:
        """检查是否超过速率限制"""
        current = await self.redis.incr(key)
        if current == 1:
            await self.redis.expire(key, window)
        return current <= limit

# 装饰器
def rate_limit(limit: int, window: int = 60, key_func=None):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            key = key_func(request) if key_func else f"rate:{request.client.host}"
            if not await rate_limiter.check(key, limit, window):
                raise HTTPException(status_code=429, detail="请求过于频繁")
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator
```

### 8.3 输入校验与防护

- **Prompt 注入防护**: 对用户输入进行转义，禁止特殊指令字符
- **SQL 注入防护**: 使用 SQLModel ORM，禁止拼接原始 SQL
- **XSS 防护**: 前端对用户输入进行 HTML 转义
- **文件上传**: 限制文件类型（txt, py, R, sh），大小上限 1MB

```python
import bleach

def sanitize_input(text: str) -> str:
    """清理用户输入，防止注入攻击"""
    # 移除 HTML 标签
    text = bleach.clean(text, tags=[], strip=True)
    
    # 移除潜在的 Prompt 注入模式
    dangerous_patterns = [
        r"ignore previous instructions",
        r"system:",
        r"assistant:",
        r"<\|.*?\|>",
    ]
    for pattern in dangerous_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    
    return text.strip()
```

### 8.4 NDA 保密协议

```python
@router.post("/")
async def create_appointment(
    request: CreateAppointmentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 硬性校验：必须签署 NDA
    if not request.accept_nda:
        raise HTTPException(
            status_code=400,
            detail={"code": 2003, "message": "必须签署保密协议"}
        )
    
    # 加密需求内容
    encrypted_requirements = encryptor.encrypt(request.requirements)
    
    appointment = Appointment(
        learner_id=current_user.id,
        mentor_id=request.mentor_id,
        requirements=encrypted_requirements,
        accept_nda=True,
        nda_signed_at=datetime.utcnow(),
        # ...
    )
    
    db.add(appointment)
    await db.commit()
    
    return {"success": True, "data": appointment}
```

---

## 9. 环境配置与部署

### 9.1 环境变量清单 (.env)

```bash
# ===== 应用配置 =====
APP_NAME=BioInfo1on1
APP_ENV=development  # development/staging/production
DEBUG=true

# ===== 数据库 =====
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/bioinfo1on1
REDIS_URL=redis://localhost:6379/0

# ===== 微信小程序 =====
WX_APP_ID=wx1234567890abcdef
WX_APP_SECRET=your_wechat_app_secret

# ===== AI 引擎 =====
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
CLAUDE_API_KEY=sk-ant-xxxxxxxxxxxxxxxx
AI_TIMEOUT_SECONDS=30

# ===== 安全 =====
JWT_SECRET=your-256-bit-secret-key-at-least-32-chars
JWT_EXPIRE_HOURS=24
JWT_REFRESH_EXPIRE_DAYS=7
AES_ENCRYPTION_KEY=your-32-byte-base64-encoded-key

# ===== 对象存储 =====
OSS_ACCESS_KEY=your_oss_access_key
OSS_SECRET_KEY=your_oss_secret_key
OSS_BUCKET=bioinfo1on1
OSS_ENDPOINT=oss-cn-beijing.aliyuncs.com

# ===== 日志 =====
LOG_LEVEL=INFO
```

### 9.2 requirements.txt

```
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlmodel==0.0.14
asyncpg==0.29.0
redis==5.0.1
httpx==0.26.0
python-jose[cryptography]==3.3.0
cryptography==42.0.0
pydantic-settings==2.1.0
python-multipart==0.0.6
bleach==6.1.0
```

### 9.3 Docker 部署配置

**Dockerfile**:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml**:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${DB_USER:-bioinfo}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-bioinfo123}
      POSTGRES_DB: ${DB_NAME:-bioinfo1on1}
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redisdata:/data

volumes:
  pgdata:
  redisdata:
```

---

## 10. 错误码规范

### 10.1 错误码分类

| 范围 | 类别 | 说明 |
|-----|------|-----|
| 1xxx | 认证错误 | Token 相关、权限相关 |
| 2xxx | 业务错误 | 订单、用户、导师相关业务逻辑错误 |
| 3xxx | AI 模块错误 | 匹配、教案生成相关 |
| 4xxx | 外部服务错误 | 微信、支付、OSS 等第三方服务 |
| 5xxx | 系统错误 | 数据库、缓存等内部错误 |

### 10.2 常用错误码

| Code | Message | HTTP Status |
|------|---------|-------------|
| 1001 | Token 已过期 | 401 |
| 1002 | 无效的 Token | 401 |
| 1003 | 权限不足 | 403 |
| 2001 | 订单已被接单，无法重复操作 | 409 |
| 2002 | 订单状态不允许此操作 | 400 |
| 2003 | 必须签署保密协议 | 400 |
| 2004 | 导师审核未通过 | 403 |
| 2005 | 不能预约自己 | 400 |
| 2006 | 该时段已被预约 | 409 |
| 3001 | AI 响应解析失败 | 500 |
| 3002 | AI 服务暂时不可用 | 503 |
| 3003 | AI 额度不足 | 503 |
| 4001 | 微信登录失败 | 401 |
| 4002 | 微信支付失败 | 400 |
| 5001 | 数据库连接失败 | 500 |
| 5002 | 缓存服务不可用 | 503 |

---

## 11. 测试策略

### 11.1 测试分层

| 层级 | 覆盖范围 | 工具 |
|-----|---------|-----|
| 单元测试 | 加密工具、状态机逻辑、工具函数 | pytest |
| 接口测试 | 全部 API 端点 | pytest + httpx |
| 集成测试 | 订单全流程、AI 调用 | pytest + testcontainers |
| E2E 测试 | 小程序核心流程 | 小程序开发者工具 |

### 11.2 核心测试用例

```python
# tests/test_appointment_state.py

import pytest
from app.models import AppointmentStatus

class TestAppointmentStateMachine:
    """订单状态机测试"""
    
    def test_normal_flow(self):
        """测试正常流程"""
        flow = [
            AppointmentStatus.PENDING_ACCEPT,
            AppointmentStatus.ACCEPTED,
            AppointmentStatus.TO_ATTEND,
            AppointmentStatus.IN_PROGRESS,
            AppointmentStatus.EVALUATING,
            AppointmentStatus.COMPLETED
        ]
        for i in range(len(flow) - 1):
            assert is_valid_transition(flow[i], flow[i+1])
    
    def test_invalid_transition(self):
        """测试非法状态转换"""
        with pytest.raises(InvalidStateTransition):
            # completed 不能回到 accepted
            validate_transition(
                AppointmentStatus.COMPLETED,
                AppointmentStatus.ACCEPTED
            )
    
    def test_cancel_from_pending(self):
        """测试待接单状态可以取消"""
        assert is_valid_transition(
            AppointmentStatus.PENDING_ACCEPT,
            AppointmentStatus.CANCELLED
        )


# tests/test_security.py

class TestEncryption:
    """加密工具测试"""
    
    def test_encrypt_decrypt_roundtrip(self):
        """测试加解密一致性"""
        original = "def hello(): print('world')"
        encrypted = encryptor.encrypt(original)
        decrypted = encryptor.decrypt(encrypted)
        assert decrypted == original
    
    def test_encrypted_is_different(self):
        """测试加密后内容不同"""
        original = "sensitive code"
        encrypted = encryptor.encrypt(original)
        assert encrypted != original


# tests/test_ai_engine.py

class TestAIEngine:
    """AI 模块测试"""
    
    @pytest.fixture
    def mock_ai_response(self):
        return '{"recommendations": [{"mentor_id": "123", "score": 0.9, "reason": "test"}]}'
    
    def test_parse_valid_json(self, mock_ai_response):
        """测试正常 JSON 解析"""
        result = parse_ai_response(mock_ai_response)
        assert "recommendations" in result
    
    def test_parse_with_markdown_wrapper(self):
        """测试带 markdown 标记的 JSON"""
        wrapped = '```json\n{"test": true}\n```'
        result = parse_ai_response(wrapped)
        assert result["test"] == True
    
    def test_fallback_on_timeout(self, mocker):
        """测试超时降级"""
        mocker.patch('app.core.ai_client.deepseek_chat', side_effect=asyncio.TimeoutError)
        mocker.patch('app.core.ai_client.claude_chat', return_value={"content": "{}"})
        
        result = await ai_match(requirement="test")
        assert result.model == "claude-3-5-sonnet"
```

---

## 12. Claude Code 开发指令

以下指令可直接发送给 Claude Code 以启动开发：

### 任务一：项目初始化与数据模型

```
请根据文档第 2-3 章，初始化 FastAPI 项目结构。

1. 创建 app/ 目录及所有子目录
2. 使用 SQLModel 在 models.py 中创建所有数据模型：
   - Users, Mentors, Tags, MentorTags, Appointments, LessonPlans, Reviews
3. 创建所有枚举类型（UserRole, AuditStatus, TagCategory, AppointmentStatus）
4. 配置 PostgreSQL 异步连接（asyncpg）
5. 创建 database.py 包含 get_db 依赖注入
```

### 任务二：安全模块实现

```
在 app/core/security.py 中实现：

1. Encryptor 类：基于 cryptography (Fernet) 的 AES-256 加密
   - encrypt(plaintext) -> ciphertext
   - decrypt(ciphertext) -> plaintext
   
2. JWT 工具函数：
   - create_access_token(data, expires_delta)
   - verify_token(token) -> payload
   
3. 速率限制装饰器（基于 Redis）：
   - rate_limit(limit, window, key_func)
```

### 任务三：微信登录接口

```
在 app/routers/auth.py 中实现：

POST /api/v1/auth/wx-login
- 输入: {code: string}
- 逻辑:
  1. 调用微信 code2Session 接口
  2. 根据 openid 查询或创建用户
  3. 生成 JWT Token
- 输出: {access_token, token_type, is_new_user}

同时实现 get_current_user 依赖注入，用于保护其他接口。
```

### 任务四：AI 匹配接口

```
在 app/routers/ai_engine.py 中实现：

POST /api/v1/ai/match
- 输入: {requirement: string}
- 逻辑:
  1. 获取所有 audit_status='approved' 的导师
  2. 将导师画像序列化为 JSON
  3. 使用全量上下文注入策略构造 Prompt
  4. 调用 DeepSeek API（30秒超时）
  5. 超时时降级到 Claude
  6. 解析 JSON 响应（带清洗逻辑）
- 输出: {recommendations: [...]}

在 app/core/ai_client.py 中封装 LLM 调用客户端。
```

### 任务五：订单状态机

```
实现订单 CRUD 及状态流转：

1. 在 app/routers/appointments.py 中实现所有订单接口
2. 创建状态转换校验函数 validate_transition(from_status, to_status)
3. POST /{appt_id}/accept 接口：
   - 校验当前状态必须是 pending_accept
   - 更新状态为 accepted
   - 使用 BackgroundTasks 异步触发教案生成
4. 创建订单时校验 accept_nda=true，否则返回 2003 错误
5. 需求内容使用 AES 加密存储
```

### 任务六：测试用例

```
在 tests/ 目录下编写测试：

1. tests/test_appointment_state.py
   - 测试正常状态流转
   - 测试非法状态转换抛出异常
   - 测试超时自动取消逻辑

2. tests/test_security.py
   - 测试加解密往返一致性
   - 测试 JWT 生成和验证

3. tests/test_ai_engine.py
   - Mock AI 响应，测试 JSON 解析
   - 测试降级逻辑
   - 测试 Prompt 注入防护
```

---

## 附录：快速启动命令

```bash
# 克隆项目后
cd bioinfo1on1-backend

# 复制环境变量
cp .env.example .env
# 编辑 .env 填入实际配置

# 启动服务（开发环境）
docker-compose up -d db redis
pip install -r requirements.txt
uvicorn app.main:app --reload

# 启动服务（生产环境）
docker-compose up -d

# 运行测试
pytest tests/ -v

# 查看 API 文档
# http://localhost:8000/docs
```

---

**文档结束** | 如有问题请联系开发团队