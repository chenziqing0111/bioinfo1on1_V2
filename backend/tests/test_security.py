import pytest
from app.core.security import Encryptor, create_access_token, verify_token
from cryptography.fernet import Fernet


class TestEncryption:
    """加密工具测试"""

    def setup_method(self):
        """每个测试前初始化"""
        # 生成一个有效的测试密钥
        self.test_key = Fernet.generate_key().decode()
        self.encryptor = Encryptor(self.test_key)

    def test_encrypt_decrypt_roundtrip(self):
        """测试加解密一致性"""
        original = "def hello(): print('world')"
        encrypted = self.encryptor.encrypt(original)
        decrypted = self.encryptor.decrypt(encrypted)
        assert decrypted == original

    def test_encrypted_is_different(self):
        """测试加密后内容不同"""
        original = "sensitive code"
        encrypted = self.encryptor.encrypt(original)
        assert encrypted != original

    def test_encrypt_unicode(self):
        """测试加密中文内容"""
        original = "这是一段保密的中文代码"
        encrypted = self.encryptor.encrypt(original)
        decrypted = self.encryptor.decrypt(encrypted)
        assert decrypted == original


class TestJWT:
    """JWT 工具测试"""

    def test_create_and_verify_token(self):
        """测试创建和验证 Token"""
        payload = {"sub": "user-123", "role": "student"}
        token = create_access_token(payload)

        # 验证 token
        decoded = verify_token(token)
        assert decoded["sub"] == "user-123"
        assert decoded["role"] == "student"

    def test_invalid_token(self):
        """测试无效 Token"""
        with pytest.raises(Exception) as exc_info:
            verify_token("invalid.token.here")
        assert exc_info.value.status_code == 401

    def test_token_contains_expiry(self):
        """测试 Token 包含过期时间"""
        payload = {"sub": "user-123"}
        token = create_access_token(payload)
        decoded = verify_token(token)
        assert "exp" in decoded
