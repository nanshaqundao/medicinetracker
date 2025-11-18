"""
数据模型模块
定义Entry和EntryList数据结构
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Any


@dataclass
class Entry:
    """药品条目数据模型"""

    id: int
    text: str
    timestamp: str

    @classmethod
    def create(cls, text: str) -> "Entry":
        """创建新的Entry实例"""
        return cls(
            id=int(datetime.now().timestamp() * 1000),
            text=text.strip(),
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Entry":
        """从字典创建Entry实例"""
        return cls(
            id=data['id'],
            text=data['text'],
            timestamp=data['timestamp']
        )

    def to_dataframe_row(self, number: int) -> List[Any]:
        """转换为Dataframe行格式 [序号, 文本, 时间, ID]"""
        return [number, self.text, self.timestamp, self.id]


class EntryList:
    """条目列表管理类"""

    def __init__(self, entries: List[Entry] = None):
        self.entries = entries or []

    def add(self, text: str) -> Entry:
        """添加新条目"""
        if not text or not text.strip():
            raise ValueError("条目内容不能为空")

        entry = Entry.create(text)
        self.entries.append(entry)
        return entry

    def get_all(self) -> List[Entry]:
        """获取所有条目"""
        return self.entries.copy()

    def get_reversed(self) -> List[Entry]:
        """获取倒序的条目列表（最新的在前）"""
        return list(reversed(self.entries))

    def clear(self) -> None:
        """清空所有条目"""
        self.entries.clear()

    def delete_by_id(self, entry_id: int) -> bool:
        """
        根据ID删除条目

        Args:
            entry_id: 条目ID

        Returns:
            删除成功返回True，未找到返回False
        """
        original_length = len(self.entries)
        self.entries = [e for e in self.entries if e.id != entry_id]
        return len(self.entries) < original_length

    def update_by_id(self, entry_id: int, new_text: str) -> bool:
        """
        根据ID更新条目

        Args:
            entry_id: 条目ID
            new_text: 新的文本内容

        Returns:
            更新成功返回True，未找到返回False
        """
        if not new_text or not new_text.strip():
            raise ValueError("条目内容不能为空")

        for entry in self.entries:
            if entry.id == entry_id:
                entry.text = new_text.strip()
                return True
        return False

    def get_by_id(self, entry_id: int) -> Entry:
        """
        根据ID获取条目

        Args:
            entry_id: 条目ID

        Returns:
            找到返回Entry对象，未找到返回None
        """
        for entry in self.entries:
            if entry.id == entry_id:
                return entry
        return None

    def count(self) -> int:
        """获取条目数量"""
        return len(self.entries)

    def to_dict_list(self) -> List[Dict[str, Any]]:
        """转换为字典列表"""
        return [entry.to_dict() for entry in self.entries]

    def to_dataframe(self) -> List[List[Any]]:
        """
        转换为Dataframe格式（倒序，最新的在上面）
        返回: [[序号, 文本, 时间, ID], ...]
        """
        reversed_entries = self.get_reversed()
        total = len(self.entries)

        return [
            entry.to_dataframe_row(total - i)
            for i, entry in enumerate(reversed_entries)
        ]

    @classmethod
    def from_dict_list(cls, data: List[Dict[str, Any]]) -> "EntryList":
        """从字典列表创建EntryList实例"""
        entries = [Entry.from_dict(item) for item in data]
        return cls(entries)

    def __len__(self) -> int:
        """支持len()函数"""
        return len(self.entries)

    def __bool__(self) -> bool:
        """支持布尔判断"""
        return bool(self.entries)
