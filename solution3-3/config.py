"""
配置文件
定义应用的配置参数
"""

import logging
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

# 数据目录
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

# 数据文件路径 (将在运行时根据用户动态生成)
# DATA_FILE = DATA_DIR / "voice_entries.json"
# STRUCTURED_DATA_FILE = DATA_DIR / "structured_medicines.json"

# 服务器配置
SERVER_NAME = "0.0.0.0"
SERVER_PORT = 7860
SHARE = False
SHOW_ERROR = True

# 应用信息
APP_TITLE = "药品信息管理系统 V3.1"
APP_VERSION = "3.1.0"

# 日志配置
LOG_FILE = PROJECT_ROOT / "app.log"
LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# LLM配置
LLM_PROVIDER = "claude"  # 支持: claude, openai, ollama

# API Keys - 从环境变量读取，或直接在此填入（不推荐提交到git）
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")  # 请设置环境变量或直接填入
CLAUDE_MODEL = "claude-3-opus-20240229"  # Claude 3 Opus
CLAUDE_MAX_TOKENS = 1024
CLAUDE_TEMPERATURE = 0.3  # 较低的温度以获得更稳定的结果

# LLM批处理配置
LLM_BATCH_SIZE = 10  # 每批处理的条目数量，可根据需要调整

# Debug logging for API Key
if CLAUDE_API_KEY:
    masked_key = CLAUDE_API_KEY[:10] + "..." + CLAUDE_API_KEY[-5:]
    print(f"✅ CLAUDE_API_KEY loaded: {masked_key}")
else:
    print("❌ CLAUDE_API_KEY is MISSING or EMPTY")


# OpenAI配置（备用）
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")  # 请设置环境变量或直接填入
OPENAI_MODEL = "gpt-4"

# Ollama配置（备用）
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama2"
