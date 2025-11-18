"""
配置文件
定义应用的配置参数
"""

from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

# 数据目录
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

# 数据文件路径
DATA_FILE = DATA_DIR / "voice_entries.json"

# 服务器配置
SERVER_NAME = "0.0.0.0"
SERVER_PORT = 7860
SHARE = False
SHOW_ERROR = True

# 应用信息
APP_TITLE = "药品信息收集器 V3"
APP_VERSION = "3.0.0"
