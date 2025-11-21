"""
业务逻辑服务模块
处理条目管理、导出等业务逻辑
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Tuple, List, Any

from .models import EntryList
from .storage import JSONStorage

logger = logging.getLogger(__name__)


class EntryService:
    """条目管理服务类"""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.current_user = "default"
        self.storage = None
        self.entry_list = None
        logger.info(f"EntryService 初始化, 数据目录: {data_dir}")
        self.switch_user(self.current_user)

    def switch_user(self, user_id: str) -> str:
        """
        切换当前用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            状态消息
        """
        if not user_id or not user_id.strip():
            return "❌ 用户名不能为空"
            
        self.current_user = user_id.strip()
        file_path = self.data_dir / f"voice_entries_{self.current_user}.json"
        self.storage = JSONStorage(file_path)
        self.load()
        logger.info(f"切换用户: {self.current_user}, 文件: {file_path}")
        return f"✅ 已切换用户: {self.current_user}"

    def load(self) -> None:
        """从存储加载数据"""
        data = self.storage.load()
        self.entry_list = EntryList.from_dict_list(data)
        logger.info(f"加载数据: {len(data)} 条")

    def save(self) -> bool:
        """保存数据到存储"""
        data = self.entry_list.to_dict_list()
        result = self.storage.save(data)
        if result:
            logger.info(f"保存数据成功: {len(data)} 条")
        else:
            logger.error("保存数据失败")
        return result

    def add_entry(self, text: str) -> Tuple[str, List[List[Any]], str, str]:
        """
        添加新条目

        Args:
            text: 条目文本

        Returns:
            (状态消息, dataframe数据, 统计信息, 清空的文本框)
        """
        if not text or not text.strip():
            logger.warning("添加失败: 空内容")
            return "❌ 请输入内容", self.get_dataframe(), self.get_count(), ""

        try:
            entry = self.entry_list.add(text)
            self.save()
            logger.info(f"添加条目: {text[:50]}..." if len(text) > 50 else f"添加条目: {text}")
            return "✅ 已添加", self.get_dataframe(), self.get_count(), ""
        except Exception as e:
            logger.error(f"添加条目失败: {e}", exc_info=True)
            return f"❌ 添加失败: {e}", self.get_dataframe(), self.get_count(), text

    def clear_all(self) -> Tuple[str, List[List[Any]], str]:
        """
        清空所有条目

        Returns:
            (状态消息, dataframe数据, 统计信息)
        """
        count = self.entry_list.count()
        self.entry_list.clear()
        self.save()
        logger.warning(f"清空所有数据: {count} 条")
        return "✅ 已清空所有条目", [], self.get_count()

    def delete_entry(self, entry_id: int) -> Tuple[str, List[List[Any]], str]:
        """
        删除指定ID的条目

        Args:
            entry_id: 条目ID

        Returns:
            (状态消息, dataframe数据, 统计信息)
        """
        if not entry_id:
            return "❌ 请先选择条目", self.get_dataframe(), self.get_count()

        try:
            entry_id = int(entry_id)
            if self.entry_list.delete_by_id(entry_id):
                self.save()
                return "✅ 已删除", self.get_dataframe(), self.get_count()
            else:
                return "❌ 未找到该条目", self.get_dataframe(), self.get_count()
        except (ValueError, TypeError) as e:
            return f"❌ 删除失败: {e}", self.get_dataframe(), self.get_count()

    def update_entry(self, entry_id: int, new_text: str) -> Tuple[str, List[List[Any]], str, str]:
        """
        更新指定ID的条目

        Args:
            entry_id: 条目ID
            new_text: 新的文本内容

        Returns:
            (状态消息, dataframe数据, 统计信息, 新的entry_id用于刷新选择)
        """
        if not entry_id:
            return "❌ 请先选择条目", self.get_dataframe(), self.get_count(), None

        if not new_text or not new_text.strip():
            return "❌ 内容不能为空", self.get_dataframe(), self.get_count(), entry_id

        try:
            entry_id = int(entry_id)
            if self.entry_list.update_by_id(entry_id, new_text):
                self.save()
                return "✅ 已更新", self.get_dataframe(), self.get_count(), None
            else:
                return "❌ 未找到该条目", self.get_dataframe(), self.get_count(), None
        except ValueError as e:
            return f"❌ 更新失败: {e}", self.get_dataframe(), self.get_count(), entry_id

    def get_entry_choices(self) -> List[Tuple[str, str]]:
        """
        获取条目选择列表（用于下拉框）

        Returns:
            [(显示文本, ID), ...] 倒序排列
        """
        if not self.entry_list:
            return []

        choices = []
        for i, entry in enumerate(self.entry_list.get_reversed()):
            num = len(self.entry_list) - i
            # 截断长文本
            text = entry.text[:40] + ('...' if len(entry.text) > 40 else '')
            display = f"#{num} - {text}"
            choices.append((display, str(entry.id)))

        return choices

    def get_entry_text(self, entry_id: int) -> str:
        """
        根据ID获取条目文本

        Args:
            entry_id: 条目ID

        Returns:
            条目文本，未找到返回空字符串
        """
        if not entry_id:
            return ""

        try:
            entry_id = int(entry_id)
            entry = self.entry_list.get_by_id(entry_id)
            return entry.text if entry else ""
        except (ValueError, TypeError):
            return ""

    def save_dataframe(self, df_data: List[List[Any]]) -> Tuple[str, List[List[Any]], str]:
        """
        保存从Dataframe编辑的数据

        Args:
            df_data: Dataframe数据 [[序号, 文本, 时间, ID], ...] 或 pandas.DataFrame

        Returns:
            (状态消息, dataframe数据, 统计信息)
        """
        # 处理pandas DataFrame - Gradio可能传递DataFrame对象
        try:
            import pandas as pd
            if isinstance(df_data, pd.DataFrame):
                # 转换DataFrame为列表
                df_data = df_data.values.tolist()
        except ImportError:
            pass  # pandas未安装，继续处理

        # 检查是否为空
        if df_data is None or (isinstance(df_data, list) and len(df_data) == 0):
            self.entry_list.clear()
            self.save()
            return "✅ 已清空", [], self.get_count()

        try:
            # 将Dataframe数据转换回Entry对象
            new_entries = []
            for row in df_data:
                # 检查行是否有效
                if not row or not isinstance(row, (list, tuple)) or len(row) < 4:
                    continue

                # row[0] = 序号 (忽略，重新计算)
                # row[1] = 文本
                # row[2] = 时间戳
                # row[3] = ID

                # 处理文本 - 跳过None、空字符串、"None"字符串
                text = row[1]
                if text is None or text == '' or str(text).strip() == '' or str(text).strip().lower() == 'none':
                    continue  # 跳过空行

                text = str(text).strip()

                # 处理ID - 确保是有效整数
                try:
                    entry_id = row[3]
                    if entry_id is None or str(entry_id).strip() == '' or str(entry_id).strip().lower() == 'none':
                        entry_id = int(datetime.now().timestamp() * 1000)
                    else:
                        entry_id = int(float(entry_id))  # 先转float再转int，处理字符串数字
                except (ValueError, TypeError):
                    entry_id = int(datetime.now().timestamp() * 1000)

                # 处理时间戳
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

            # 反序回来（Dataframe是倒序显示的）
            new_entries.reverse()

            # 替换整个列表并保存
            self.entry_list = EntryList.from_dict_list(new_entries)
            save_result = self.save()

            if save_result:
                timestamp = datetime.now().strftime('%H:%M:%S')
                logger.info(f"保存表格修改: {len(new_entries)} 条数据")
                return f"✅ 已保存 {len(new_entries)} 条数据到文件 ({timestamp})", self.get_dataframe(), self.get_count()
            else:
                logger.error("保存表格修改失败")
                return "❌ 保存失败", self.get_dataframe(), self.get_count()

        except Exception as e:
            logger.error(f"保存表格修改失败: {e}", exc_info=True)
            return f"❌ 保存失败: {e}", self.get_dataframe(), self.get_count()

    def get_dataframe(self) -> List[List[Any]]:
        """获取Dataframe格式数据"""
        return self.entry_list.to_dataframe()

    def get_count(self) -> str:
        """获取统计信息"""
        count = self.entry_list.count()
        return f"📊 已收集: **{count}** 条"

    def refresh(self) -> Tuple[List[List[Any]], str]:
        """
        刷新数据（重新加载）

        Returns:
            (dataframe数据, 统计信息)
        """
        logger.info("刷新数据")
        self.load()
        return self.get_dataframe(), self.get_count()

    def export_to_text(self) -> str:
        """
        导出为文本文件

        Returns:
            导出的文件路径，如果没有数据则返回None
        """
        if not self.entry_list or self.entry_list.count() == 0:
            logger.warning("导出失败: 没有数据")
            return None

        filename = f"medicine_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = Path(filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                for i, entry in enumerate(self.entry_list.get_all(), 1):
                    f.write(f"{i}. {entry.text}\n")
            logger.info(f"导出成功: {filepath}, {self.entry_list.count()} 条")
            return str(filepath)
        except IOError as e:
            logger.error(f"导出失败: {e}", exc_info=True)
            return None
