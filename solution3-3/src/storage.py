"""
数据存储模块
负责JSON文件的读写操作
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any


import time
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def cleanup_old_files(data_dir: Path, days: int = 30) -> None:
    """
    清理超过指定天数未修改的数据文件
    
    Args:
        data_dir: 数据目录
        days: 保留天数
    """
    if not data_dir.exists():
        return
        
    logger.info(f"开始清理过期文件 (保留 {days} 天)...")
    cutoff_time = datetime.now() - timedelta(days=days)
    count = 0
    
    try:
        for file_path in data_dir.glob("*.json"):
            # 只处理用户数据文件
            if not (file_path.name.startswith("voice_entries_") or 
                    file_path.name.startswith("structured_medicines_")):
                continue
                
            # 检查最后修改时间
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            if mtime < cutoff_time:
                try:
                    file_path.unlink()
                    logger.info(f"删除过期文件: {file_path.name} (最后修改: {mtime})")
                    count += 1
                except OSError as e:
                    logger.error(f"删除文件失败 {file_path.name}: {e}")
                    
        if count > 0:
            logger.info(f"清理完成: 删除了 {count} 个过期文件")
        else:
            logger.info("清理完成: 没有发现过期文件")
            
    except Exception as e:
        logger.error(f"清理过程出错: {e}")



class JSONStorage:
    """JSON文件存储类"""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        logger.info(f"JSONStorage 初始化: {file_path}")

    def load(self) -> List[Dict[str, Any]]:
        """
        从JSON文件加载数据

        Returns:
            数据字典列表，如果文件不存在或解析失败则返回空列表
        """
        if not self.file_path.exists():
            logger.info(f"数据文件不存在: {self.file_path}")
            return []

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                result = data if isinstance(data, list) else []
                logger.info(f"加载文件成功: {self.file_path}, {len(result)} 条")
                return result
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"加载文件失败: {self.file_path}, 错误: {e}")
            return []

    def save(self, data: List[Dict[str, Any]]) -> bool:
        """
        保存数据到JSON文件

        Args:
            data: 要保存的数据字典列表

        Returns:
            保存成功返回True，失败返回False
        """
        try:
            # 确保父目录存在
            self.file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"保存文件成功: {self.file_path}, {len(data)} 条")
            return True
        except IOError as e:
            logger.error(f"保存文件失败: {self.file_path}, 错误: {e}")
            return False

    def clear(self) -> bool:
        """清空数据文件"""
        logger.warning(f"清空文件: {self.file_path}")
        return self.save([])

    def exists(self) -> bool:
        """检查文件是否存在"""
        return self.file_path.exists()
