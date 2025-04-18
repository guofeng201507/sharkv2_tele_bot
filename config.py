import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    LLM_TYPE = os.getenv("LLM_TYPE", "deepseek").lower()

    # DeepSeek API configuration
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

    # Qwen API configuration
    QWEN_API_KEY = os.getenv("QWEN_API_KEY")
    QWEN_API_URL = "https://dashscope.aliyun.com/api/v1/services/aigc/text-generation/generation"

    # Bot behavior settings
    MAX_MESSAGE_LENGTH = 4096  # Telegram message limit
    MAX_HISTORY = 10  # Number of messages to keep in conversation history
    TIMEOUT = 60  # Timeout for API calls in seconds


config = Config()