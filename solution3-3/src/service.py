"""
业务逻辑服务模块
处理条目管理、导出等业务逻辑
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Tuple, List, Any, Dict

from .models import EntryList
from .storage import JSONStorage

logger = logging.getLogger(__name__)


class EntryService:
    """条目管理服务类"""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        # 内存缓存：user_id -> EntryList
        self.sessions: Dict[str, EntryList] = {}
        logger.info(f"EntryService 初始化, 数据目录: {data_dir}")

    def _get_storage(self, user_id: str) -> JSONStorage:
        """获取指定用户的存储对象"""
        user_id = user_id.strip() if user_id else "default"
        file_path = self.data_dir / f"voice_entries_{user_id}.json"
        return JSONStorage(file_path)

    def _get_entry_list(self, user_id: str) -> EntryList:
        """获取指定用户的条目列表（带缓存）"""
        user_id = user_id.strip() if user_id else "default"
        
        # 如果缓存中没有，则加载
        if user_id not in self.sessions:
            storage = self._get_storage(user_id)
            data = storage.load()
            self.sessions[user_id] = EntryList.from_dict_list(data)
            logger.info(f"加载用户数据: {user_id}, {len(data)} 条")
            
        return self.sessions[user_id]

    def _save_user_data(self, user_id: str) -> bool:
        """保存指定用户的数据"""
        user_id = user_id.strip() if user_id else "default"
        if user_id not in self.sessions:
            return False
            
        entry_list = self.sessions[user_id]
        storage = self._get_storage(user_id)
        
        data = entry_list.to_dict_list()
        result = storage.save(data)
        
        if result:
            logger.info(f"保存用户数据成功: {user_id}, {len(data)} 条")
        else:
            logger.error(f"保存用户数据失败: {user_id}")
        return result

    def add_entry(self, text: str, user_id: str) -> Tuple[str, List[List[Any]], str, str]:
        """
        添加新条目

        Args:
            text: 条目文本
            user_id: 用户ID

        Returns:
            (状态消息, dataframe数据, 统计信息, 清空的文本框)
        """
        if not text or not text.strip():
            logger.warning("添加失败: 空内容")
            return "❌ 请输入内容", self.get_dataframe(user_id), self.get_count(user_id), ""

        try:
            entry_list = self._get_entry_list(user_id)
            entry_list.add(text)
            self._save_user_data(user_id)
            logger.info(f"用户 {user_id} 添加条目: {text[:50]}...")
            return "✅ 已添加", self.get_dataframe(user_id), self.get_count(user_id), ""
        except Exception as e:
            logger.error(f"添加条目失败: {e}", exc_info=True)
            return f"❌ 添加失败: {e}", self.get_dataframe(user_id), self.get_count(user_id), text

    def clear_all(self, user_id: str) -> Tuple[str, List[List[Any]], str]:
        """
        清空所有条目

        Args:
            user_id: 用户ID

        Returns:
            (状态消息, dataframe数据, 统计信息)
        """
        entry_list = self._get_entry_list(user_id)
        count = entry_list.count()
        entry_list.clear()
        self._save_user_data(user_id)
        logger.warning(f"用户 {user_id} 清空所有数据: {count} 条")
        return "✅ 已清空所有条目", [], self.get_count(user_id)

    def delete_entry(self, entry_id: int, user_id: str) -> Tuple[str, List[List[Any]], str]:
        """
        删除指定ID的条目

        Args:
            entry_id: 条目ID
            user_id: 用户ID

        Returns:
            (状态消息, dataframe数据, 统计信息)
        """
        if not entry_id:
            return "❌ 请先选择条目", self.get_dataframe(user_id), self.get_count(user_id)

        try:
            entry_id = int(entry_id)
            entry_list = self._get_entry_list(user_id)
            if entry_list.delete_by_id(entry_id):
                self._save_user_data(user_id)
                return "✅ 已删除", self.get_dataframe(user_id), self.get_count(user_id)
            else:
                return "❌ 未找到该条目", self.get_dataframe(user_id), self.get_count(user_id)
        except (ValueError, TypeError) as e:
            return f"❌ 删除失败: {e}", self.get_dataframe(user_id), self.get_count(user_id)

    def update_entry(self, entry_id: int, new_text: str, user_id: str) -> Tuple[str, List[List[Any]], str, str]:
        """
        更新指定ID的条目

        Args:
            entry_id: 条目ID
            new_text: 新的文本内容
            user_id: 用户ID

        Returns:
            (状态消息, dataframe数据, 统计信息, 新的entry_id用于刷新选择)
        """
        if not entry_id:
            return "❌ 请先选择条目", self.get_dataframe(user_id), self.get_count(user_id), None

        if not new_text or not new_text.strip():
            return "❌ 内容不能为空", self.get_dataframe(user_id), self.get_count(user_id), entry_id

        try:
            entry_id = int(entry_id)
            entry_list = self._get_entry_list(user_id)
            if entry_list.update_by_id(entry_id, new_text):
                self._save_user_data(user_id)
                return "✅ 已更新", self.get_dataframe(user_id), self.get_count(user_id), None
            else:
                return "❌ 未找到该条目", self.get_dataframe(user_id), self.get_count(user_id), None
        except ValueError as e:
            return f"❌ 更新失败: {e}", self.get_dataframe(user_id), self.get_count(user_id), entry_id

    def get_entry_choices(self, user_id: str) -> List[Tuple[str, str]]:
        """
        获取条目选择列表（用于下拉框）

        Args:
            user_id: 用户ID

        Returns:
            [(显示文本, ID), ...] 倒序排列
        """
        entry_list = self._get_entry_list(user_id)
        if not entry_list:
            return []

        choices = []
        for i, entry in enumerate(entry_list.get_reversed()):
            num = len(entry_list) - i
            # 截断长文本
            text = entry.text[:40] + ('...' if len(entry.text) > 40 else '')
            display = f"#{num} - {text}"
            choices.append((display, str(entry.id)))

        return choices

    def get_entry_text(self, entry_id: int, user_id: str) -> str:
        """
        根据ID获取条目文本

        Args:
            entry_id: 条目ID
            user_id: 用户ID

        Returns:
            条目文本，未找到返回空字符串
        """
        if not entry_id:
            return ""

        try:
            entry_id = int(entry_id)
            entry_list = self._get_entry_list(user_id)
            entry = entry_list.get_by_id(entry_id)
            return entry.text if entry else ""
        except (ValueError, TypeError):
            return ""

    def save_dataframe(self, df_data: List[List[Any]], user_id: str) -> Tuple[str, List[List[Any]], str]:
        """
        保存从Dataframe编辑的数据

        Args:
            df_data: Dataframe数据
            user_id: 用户ID

        Returns:
            (状态消息, dataframe数据, 统计信息)
        """
        # 处理pandas DataFrame
        try:
            import pandas as pd
            if isinstance(df_data, pd.DataFrame):
                df_data = df_data.values.tolist()
        except ImportError:
            pass

        entry_list = self._get_entry_list(user_id)

        # 检查是否为空
        if df_data is None or (isinstance(df_data, list) and len(df_data) == 0):
            entry_list.clear()
            self._save_user_data(user_id)
            return "✅ 已清空", [], self.get_count(user_id)

        try:
            # 将Dataframe数据转换回Entry对象
            new_entries = []
            for row in df_data:
                if not row or not isinstance(row, (list, tuple)) or len(row) < 4:
                    continue

                text = row[1]
                if text is None or text == '' or str(text).strip() == '' or str(text).strip().lower() == 'none':
                    continue

                text = str(text).strip()

                try:
                    entry_id = row[3]
                    if entry_id is None or str(entry_id).strip() == '' or str(entry_id).strip().lower() == 'none':
                        entry_id = int(datetime.now().timestamp() * 1000)
                    else:
                        entry_id = int(float(entry_id))
                except (ValueError, TypeError):
                    entry_id = int(datetime.now().timestamp() * 1000)

                timestamp = row[2]
                if timestamp is None or str(timestamp).strip() == '' or str(timestamp).strip().lower() == 'none':
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                else:
                    timestamp = str(timestamp).strip()

                new_entries.append({
                    'id': entry_id,
                    'text': text,
                    'timestamp': timestamp
                })

            new_entries.reverse()
            
            # 更新列表并保存
            # 注意：这里我们需要替换 EntryList 中的数据，而不是替换 EntryList 对象本身
            # 因为 self.sessions[user_id] 指向的是同一个对象
            entry_list.entries = [] # 清空旧数据
            # 重新加载数据
            temp_list = EntryList.from_dict_list(new_entries)
            entry_list.entries = temp_list.entries
            
            save_result = self._save_user_data(user_id)

            if save_result:
                timestamp = datetime.now().strftime('%H:%M:%S')
                logger.info(f"保存表格修改: {len(new_entries)} 条数据")
                return f"✅ 已保存 {len(new_entries)} 条数据到文件 ({timestamp})", self.get_dataframe(user_id), self.get_count(user_id)
            else:
                logger.error("保存表格修改失败")
                return "❌ 保存失败", self.get_dataframe(user_id), self.get_count(user_id)

        except Exception as e:
            logger.error(f"保存表格修改失败: {e}", exc_info=True)
            return f"❌ 保存失败: {e}", self.get_dataframe(user_id), self.get_count(user_id)

    def get_dataframe(self, user_id: str) -> List[List[Any]]:
        """获取Dataframe格式数据"""
        entry_list = self._get_entry_list(user_id)
        return entry_list.to_dataframe()

    def get_count(self, user_id: str) -> str:
        """获取统计信息"""
        entry_list = self._get_entry_list(user_id)
        count = entry_list.count()
        return f"📊 已收集: **{count}** 条"

    def refresh(self, user_id: str) -> Tuple[List[List[Any]], str]:
        """
        刷新数据（重新加载）

        Args:
            user_id: 用户ID

        Returns:
            (dataframe数据, 统计信息)
        """
        logger.info(f"刷新数据: {user_id}")
        # 强制重新加载
        if user_id in self.sessions:
            del self.sessions[user_id]
        return self.get_dataframe(user_id), self.get_count(user_id)

    def export_to_text(self, user_id: str) -> str:
        """
        导出为文本文件

        Args:
            user_id: 用户ID

        Returns:
            导出的文件路径，如果没有数据则返回None
        """
        entry_list = self._get_entry_list(user_id)
        if not entry_list or entry_list.count() == 0:
            logger.warning("导出失败: 没有数据")
            return None

        filename = f"medicine_list_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = Path(filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                for i, entry in enumerate(entry_list.get_all(), 1):
                    f.write(f"{i}. {entry.text}\n")
            logger.info(f"导出成功: {filepath}, {entry_list.count()} 条")
            return str(filepath)
        except IOError as e:
            logger.error(f"导出失败: {e}", exc_info=True)
            return None
