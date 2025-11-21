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


# ============================================================================
# 结构化数据模型
# ============================================================================

@dataclass
class StructuredMedicine:
    """结构化药品信息数据模型"""

    id: int
    original_text: str          # 原始文本
    drug_name: str             # 药名（通用名）
    brand_name: str = ""       # 商品名
    generic_name: str = ""     # 学术名/化学名
    quantity: float = 0.0      # 数量
    unit: str = ""            # 单位
    specification: str = ""    # 规格
    package_count: str = ""    # 包装数量
    expiry_date: str = ""     # 有效期
    timestamp: str = ""        # 录入时间
    confidence: float = 1.0    # 置信度（LLM提取的可信度）

    @classmethod
    def create(cls, original_text: str, **kwargs) -> "StructuredMedicine":
        """创建新的StructuredMedicine实例"""
        return cls(
            id=int(datetime.now().timestamp() * 1000),
            original_text=original_text.strip(),
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            **kwargs
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StructuredMedicine":
        """从字典创建StructuredMedicine实例"""
        return cls(**data)

    def to_dataframe_row(self, number: int) -> List[Any]:
        """
        转换为Dataframe行格式
        [序号, 药名, 商品名, 学术名, 数量, 单位, 规格, 包装, 有效期, 原始文本, 时间]
        """
        return [
            number,
            self.drug_name,
            self.brand_name,
            self.generic_name,
            self.quantity,
            self.unit,
            self.specification,
            self.package_count,
            self.expiry_date,
            self.original_text,
            self.timestamp
        ]

    def is_valid(self) -> bool:
        """检查数据是否有效（至少有药名）"""
        return bool(self.drug_name and self.drug_name.strip())


class StructuredMedicineList:
    """结构化药品列表管理类"""

    def __init__(self, medicines: List[StructuredMedicine] = None):
        self.medicines = medicines or []

    def add(self, medicine: StructuredMedicine) -> None:
        """添加新的结构化药品"""
        if not medicine.is_valid():
            raise ValueError("药品信息无效：缺少药名")
        self.medicines.append(medicine)

    def get_all(self) -> List[StructuredMedicine]:
        """获取所有结构化药品"""
        return self.medicines.copy()

    def get_reversed(self) -> List[StructuredMedicine]:
        """获取倒序的列表（最新的在前）"""
        return list(reversed(self.medicines))

    def clear(self) -> None:
        """清空所有数据"""
        self.medicines.clear()

    def get_by_id(self, medicine_id: int) -> StructuredMedicine:
        """根据ID获取药品信息"""
        for medicine in self.medicines:
            if medicine.id == medicine_id:
                return medicine
        return None

    def update_by_id(self, medicine_id: int, **kwargs) -> bool:
        """根据ID更新药品信息"""
        medicine = self.get_by_id(medicine_id)
        if medicine:
            for key, value in kwargs.items():
                if hasattr(medicine, key):
                    setattr(medicine, key, value)
            return True
        return False

    def delete_by_id(self, medicine_id: int) -> bool:
        """根据ID删除药品信息"""
        original_length = len(self.medicines)
        self.medicines = [m for m in self.medicines if m.id != medicine_id]
        return len(self.medicines) < original_length

    def filter_by_drug_name(self, drug_name: str) -> List[StructuredMedicine]:
        """根据药名筛选"""
        return [m for m in self.medicines if drug_name.lower() in m.drug_name.lower()]

    def filter_by_expiry(self, before_date: str = None, after_date: str = None) -> List[StructuredMedicine]:
        """根据有效期筛选"""
        result = self.medicines.copy()
        if before_date:
            result = [m for m in result if m.expiry_date and m.expiry_date <= before_date]
        if after_date:
            result = [m for m in result if m.expiry_date and m.expiry_date >= after_date]
        return result

    def sort_by_drug_name(self, reverse: bool = False) -> List[StructuredMedicine]:
        """按药名排序"""
        return sorted(self.medicines, key=lambda m: m.drug_name, reverse=reverse)

    def sort_by_expiry(self, reverse: bool = False) -> List[StructuredMedicine]:
        """按有效期排序"""
        return sorted(
            self.medicines,
            key=lambda m: m.expiry_date if m.expiry_date else "9999-99-99",
            reverse=reverse
        )

    def count(self) -> int:
        """获取数量"""
        return len(self.medicines)

    def to_dict_list(self) -> List[Dict[str, Any]]:
        """转换为字典列表"""
        return [m.to_dict() for m in self.medicines]

    def to_dataframe(self) -> List[List[Any]]:
        """
        转换为Dataframe格式（倒序，最新的在上面）
        返回: [[序号, 药名, 商品名, 学术名, 数量, 单位, 规格, 包装, 有效期, 原始文本, 时间], ...]
        """
        reversed_medicines = self.get_reversed()
        total = len(self.medicines)

        return [
            medicine.to_dataframe_row(total - i)
            for i, medicine in enumerate(reversed_medicines)
        ]

    @classmethod
    def from_dict_list(cls, data: List[Dict[str, Any]]) -> "StructuredMedicineList":
        """从字典列表创建StructuredMedicineList实例"""
        medicines = [StructuredMedicine.from_dict(item) for item in data]
        return cls(medicines)

    def __len__(self) -> int:
        """支持len()函数"""
        return len(self.medicines)

    def __bool__(self) -> bool:
        """支持布尔判断"""
        return bool(self.medicines)
