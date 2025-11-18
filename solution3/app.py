#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
药品信息收集器 V3 - 主应用入口
Medicine Voice Collector V3 - Main Application Entry
"""

from src.storage import JSONStorage
from src.service import EntryService
from src.ui import GradioUI
import config


def main():
    """主函数"""
    print("=" * 70)
    print(f"🚀 {config.APP_TITLE}")
    print("=" * 70)
    print(f"📍 访问: http://localhost:{config.SERVER_PORT}")
    print("🎤 点击按钮开始语音输入")
    print("📊 数据自动保存")
    print("=" * 70)

    # 初始化存储层
    storage = JSONStorage(config.DATA_FILE)

    # 初始化服务层
    service = EntryService(storage)

    # 初始化UI层
    ui = GradioUI(service)

    # 启动应用
    ui.launch(
        share=config.SHARE,
        server_name=config.SERVER_NAME,
        server_port=config.SERVER_PORT,
        show_error=config.SHOW_ERROR
    )


if __name__ == "__main__":
    main()
