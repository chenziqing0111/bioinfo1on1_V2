import pytest
from app.core.ai_client import parse_ai_response


class TestAIEngine:
    """AI 模块测试"""

    def test_parse_valid_json(self):
        """测试正常 JSON 解析"""
        mock_response = '{"recommendations": [{"mentor_id": "123", "score": 0.9, "reason": "test"}]}'
        result = parse_ai_response(mock_response)
        assert "recommendations" in result
        assert len(result["recommendations"]) == 1
        assert result["recommendations"][0]["mentor_id"] == "123"

    def test_parse_with_markdown_wrapper(self):
        """测试带 markdown 标记的 JSON"""
        wrapped = '```json\n{"test": true}\n```'
        result = parse_ai_response(wrapped)
        assert result["test"] == True

    def test_parse_with_extra_text(self):
        """测试带额外文本的 JSON"""
        response_with_text = '''这是一些额外的文本
        {
          "recommendations": [
            {"mentor_id": "456", "score": 0.85, "reason": "good match"}
          ]
        }
        还有一些尾部文本'''
        result = parse_ai_response(response_with_text)
        assert "recommendations" in result

    def test_parse_invalid_json(self):
        """测试无效 JSON 抛出异常"""
        with pytest.raises(ValueError) as exc_info:
            parse_ai_response("这不是 JSON")
        assert "无法解析 AI 响应" in str(exc_info.value)

    def test_parse_multiline_json(self):
        """测试多行 JSON"""
        multiline = '''{
  "recommendations": [
    {
      "mentor_id": "uuid-123",
      "score": 0.92,
      "reason": "专业对口",
      "can_solve": ["问题1", "问题2"]
    }
  ]
}'''
        result = parse_ai_response(multiline)
        assert len(result["recommendations"]) == 1
        assert result["recommendations"][0]["score"] == 0.92


class TestAIClientMock:
    """AI 客户端模拟测试"""

    @pytest.mark.asyncio
    async def test_fallback_on_timeout(self, mocker):
        """测试超时降级（需要 mock）"""
        # 这个测试需要 mock AI 客户端
        # 实际项目中可以使用 pytest-mock
        pass
