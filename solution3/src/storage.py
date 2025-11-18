"""
数据存储模块
负责JSON文件的读写操作
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


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
