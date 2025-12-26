from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # 应用配置
    APP_NAME: str = "BioInfo1on1"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # 数据库
    DATABASE_URL: str
    REDIS_URL: str

    # 微信
    WX_APP_ID: str
    WX_APP_SECRET: str

    # AI 引擎
    DEEPSEEK_API_KEY: str
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    CLAUDE_API_KEY: str
    AI_TIMEOUT_SECONDS: int = 30

    # 安全
    JWT_SECRET: str
    JWT_EXPIRE_HOURS: int = 24
    JWT_REFRESH_EXPIRE_DAYS: int = 7
    AES_ENCRYPTION_KEY: str

    # 对象存储
    OSS_ACCESS_KEY: str = ""
    OSS_SECRET_KEY: str = ""
    OSS_BUCKET: str = "bioinfo1on1"
    OSS_ENDPOINT: str = "oss-cn-beijing.aliyuncs.com"

    # 日志
    LOG_LEVEL: str = "INFO"


settings = Settings()
