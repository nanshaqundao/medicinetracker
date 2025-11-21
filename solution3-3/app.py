#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
药品信息收集器 V3 - 主应用入口
Medicine Voice Collector V3 - Main Application Entry
"""

import logging
from src.storage import JSONStorage
from src.service import EntryService
from src.text_parser import MedicineParserService
from src.ui import GradioUI
import config


def setup_logging():
    """配置日志系统"""
    logging.basicConfig(
        level=config.LOG_LEVEL,
        format=config.LOG_FORMAT,
        datefmt=config.LOG_DATE_FORMAT,
        handlers=[
            logging.FileHandler(config.LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()  # 同时输出到控制台
        ]
    )


def main():
    """主函数"""
    # 初始化日志
    setup_logging()
    logger = logging.getLogger(__name__)

    print("=" * 70)
    print(f"🚀 {config.APP_TITLE}")
    print("=" * 70)
    print(f"📍 访问: http://localhost:{config.SERVER_PORT}")
    print("🎤 点击按钮开始语音输入")
    print("📊 数据自动保存")
    print(f"📝 日志文件: {config.LOG_FILE}")
    print("=" * 70)

    logger.info(f"应用启动: {config.APP_TITLE} v{config.APP_VERSION}")
    logger.info(f"服务器地址: {config.SERVER_NAME}:{config.SERVER_PORT}")
    logger.info(f"数据目录: {config.DATA_DIR}")

    # 清理过期数据
    from src.storage import cleanup_old_files
    cleanup_old_files(config.DATA_DIR, days=30)

    # 初始化服务层
    logger.info("初始化服务层...")
    service = EntryService(config.DATA_DIR)

    # 初始化解析服务层
    logger.info("初始化解析服务层...")
    parser_service = MedicineParserService(config.DATA_DIR)

    # 初始化UI层
    logger.info("初始化UI层...")
    ui = GradioUI(service, parser_service)

    # 启动应用
    logger.info("启动Gradio应用...")
    try:
        ui.launch(
            share=config.SHARE,
            server_name=config.SERVER_NAME,
            server_port=config.SERVER_PORT,
            show_error=config.SHOW_ERROR
        )
    except Exception as e:
        logger.error(f"应用启动失败: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
