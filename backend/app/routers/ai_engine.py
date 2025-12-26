import json
import asyncio
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import MatchRequest, MatchResponse, MatchRecommendation
from app.core.ai_client import ai_client, parse_ai_response
from app.core.security import get_current_user
from app.models import User, Mentor, LessonPlan
from app import crud

router = APIRouter()


# AI 匹配系统提示词
MATCH_SYSTEM_PROMPT = """你是 BioInfo1on1 平台的生物信息学专家顾问。

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
{{
  "recommendations": [
    {{
      "mentor_id": "uuid-string",
      "score": 0.95,
      "reason": "基于导师背景的具体推荐理由",
      "can_solve": ["能解决的问题1", "能解决的问题2"]
    }}
  ]
}}
"""


# AI 教案生成提示词
LESSON_PLAN_PROMPT = """你是一位资深的生物信息学教学专家。

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


def mentor_to_match_dict(mentor: Mentor) -> dict:
    """将导师转换为匹配用的字典"""
    return {
        "id": str(mentor.id),
        "title": mentor.title,
        "institution": mentor.institution,
        "resume": mentor.resume_json,
        "hourly_rate": float(mentor.hourly_rate),
        "rating": float(mentor.rating),
        "total_sessions": mentor.total_sessions
    }


@router.post("/match", response_model=MatchResponse)
async def ai_match(
    request: MatchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """智能匹配导师"""
    # 1. 获取所有已审核导师
    mentors = await crud.get_approved_mentors(db)
    if not mentors:
        raise HTTPException(
            status_code=404,
            detail={"code": 2004, "message": "暂无可用导师"}
        )

    mentor_json = json.dumps(
        [mentor_to_match_dict(m) for m in mentors],
        ensure_ascii=False,
        indent=2
    )

    # 2. 构造 Prompt
    prompt = MATCH_SYSTEM_PROMPT.format(
        mentor_json=mentor_json,
        user_requirement=request.requirement
    )

    # 3. 调用 AI（带降级逻辑）
    try:
        result = await ai_client.chat(
            messages=[{"role": "user", "content": prompt}],
            model="deepseek-chat",
            timeout=30
        )
    except (asyncio.TimeoutError, Exception) as e:
        # 降级到备用模型
        try:
            result = await ai_client.chat(
                messages=[{"role": "user", "content": prompt}],
                model="claude-3-5-sonnet-20241022",
                timeout=60
            )
        except Exception as fallback_error:
            raise HTTPException(
                status_code=503,
                detail={
                    "code": 3002,
                    "message": f"AI 服务暂时不可用: {str(fallback_error)}"
                }
            )

    # 4. 解析结果
    try:
        parsed = parse_ai_response(result["content"])
        recommendations = [
            MatchRecommendation(**rec) for rec in parsed["recommendations"]
        ]
    except (ValueError, KeyError) as e:
        raise HTTPException(
            status_code=500,
            detail={"code": 3001, "message": f"AI 响应解析失败: {str(e)}"}
        )

    return MatchResponse(recommendations=recommendations)


async def generate_lesson_plan_task(
    appointment_id: UUID,
    requirements: str,
    db_session_maker
):
    """后台任务：生成 AI 教案"""
    async with db_session_maker() as db:
        try:
            result = await ai_client.chat(
                messages=[{
                    "role": "user",
                    "content": LESSON_PLAN_PROMPT.format(requirements=requirements)
                }],
                model="deepseek-chat",
                timeout=60
            )

            lesson_plan = LessonPlan(
                appointment_id=appointment_id,
                content_md=result["content"],
                model_name=result["model"],
                input_tokens=result["usage"]["input_tokens"],
                output_tokens=result["usage"]["output_tokens"],
                is_fallback=False
            )

        except Exception as e:
            # 降级到备用模型
            try:
                result = await ai_client.chat(
                    messages=[{
                        "role": "user",
                        "content": LESSON_PLAN_PROMPT.format(requirements=requirements)
                    }],
                    model="claude-3-5-sonnet-20241022",
                    timeout=120
                )

                lesson_plan = LessonPlan(
                    appointment_id=appointment_id,
                    content_md=result["content"],
                    model_name=result["model"],
                    input_tokens=result["usage"]["input_tokens"],
                    output_tokens=result["usage"]["output_tokens"],
                    is_fallback=True
                )

            except Exception as fallback_error:
                # 记录错误，创建失败占位
                lesson_plan = LessonPlan(
                    appointment_id=appointment_id,
                    content_md=f"# 教案生成失败\n\n错误信息: {str(fallback_error)}",
                    model_name="failed",
                    is_fallback=True
                )

        db.add(lesson_plan)
        await db.commit()
