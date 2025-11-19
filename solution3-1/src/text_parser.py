"""
文本结构化解析服务
将原始文本转换为结构化药品数据
"""

import logging
from typing import List, Tuple
from .models import Entry, EntryList, StructuredMedicine, StructuredMedicineList
from .storage import JSONStorage
from .llm_client import create_llm_client
import config

logger = logging.getLogger(__name__)


class MedicineParserService:
    """药品文本解析服务"""

    def __init__(self, llm_client=None, structured_storage: JSONStorage = None):
        """
        初始化解析服务

        Args:
            llm_client: LLM客户端（如果为None，则自动创建）
            structured_storage: 结构化数据存储（如果为None，则自动创建）
        """
        # 初始化LLM客户端
        if llm_client is None:
            self.llm_client = create_llm_client(
                provider=config.LLM_PROVIDER,
                api_key=config.CLAUDE_API_KEY,
                model=config.CLAUDE_MODEL,
                max_tokens=config.CLAUDE_MAX_TOKENS,
                temperature=config.CLAUDE_TEMPERATURE
            )
        else:
            self.llm_client = llm_client

        # 初始化存储
        if structured_storage is None:
            self.structured_storage = JSONStorage(config.STRUCTURED_DATA_FILE)
        else:
            self.structured_storage = structured_storage

        # 加载已有的结构化数据
        self.structured_list = StructuredMedicineList()
        self.load_structured_data()

        logger.info("MedicineParserService 初始化完成")

    def load_structured_data(self) -> None:
        """从存储加载结构化数据"""
        data = self.structured_storage.load()
        if data:
            self.structured_list = StructuredMedicineList.from_dict_list(data)
            logger.info(f"加载结构化数据: {len(data)} 条")
        else:
            logger.info("无已有结构化数据")

    def save_structured_data(self) -> bool:
        """保存结构化数据到存储"""
        data = self.structured_list.to_dict_list()
        result = self.structured_storage.save(data)
        if result:
            logger.info(f"保存结构化数据成功: {len(data)} 条")
        return result

    def parse_single_text(self, text: str) -> StructuredMedicine:
        """
        解析单条文本

        Args:
            text: 原始文本

        Returns:
            StructuredMedicine对象
        """
        logger.info(f"开始解析文本: {text}")

        # 调用LLM解析
        parsed_data = self.llm_client.parse_medicine_text(text)

        # 创建StructuredMedicine对象
        medicine = StructuredMedicine.create(
            original_text=text,
            drug_name=parsed_data.get('drug_name', ''),
            brand_name=parsed_data.get('brand_name', ''),
            generic_name=parsed_data.get('generic_name', ''),
            quantity=parsed_data.get('quantity', 0.0),
            unit=parsed_data.get('unit', ''),
            specification=parsed_data.get('specification', ''),
            package_count=parsed_data.get('package_count', ''),
            expiry_date=parsed_data.get('expiry_date', '')
        )

        logger.info(f"解析完成: {medicine.drug_name}")
        return medicine

    def parse_batch(self, entries: List[Entry]) -> Tuple[List[StructuredMedicine], List[str]]:
        """
        批量解析文本

        Args:
            entries: Entry对象列表

        Returns:
            (成功解析的StructuredMedicine列表, 失败的文本列表)
        """
        logger.info(f"开始批量解析: {len(entries)} 条")

        success_list = []
        failed_list = []

        for entry in entries:
            try:
                medicine = self.parse_single_text(entry.text)
                if medicine.is_valid():
                    success_list.append(medicine)
                else:
                    logger.warning(f"解析结果无效: {entry.text}")
                    failed_list.append(entry.text)
            except Exception as e:
                logger.error(f"解析失败: {entry.text}, 错误: {e}")
                failed_list.append(entry.text)

        logger.info(f"批量解析完成: 成功 {len(success_list)}, 失败 {len(failed_list)}")
        return success_list, failed_list

    def parse_and_save(self, entries: List[Entry]) -> Tuple[int, int, List[str]]:
        """
        解析并保存

        Args:
            entries: Entry对象列表

        Returns:
            (成功数量, 失败数量, 失败文本列表)
        """
        success_list, failed_list = self.parse_batch(entries)

        # 添加到列表
        for medicine in success_list:
            try:
                self.structured_list.add(medicine)
            except ValueError as e:
                logger.error(f"添加失败: {e}")
                failed_list.append(medicine.original_text)

        # 保存
        self.save_structured_data()

        return len(success_list), len(failed_list), failed_list

    def get_all_structured(self) -> List[StructuredMedicine]:
        """获取所有结构化数据"""
        return self.structured_list.get_all()

    def get_structured_dataframe(self) -> List[List]:
        """获取结构化数据的Dataframe格式"""
        return self.structured_list.to_dataframe()

    def filter_by_drug_name(self, drug_name: str) -> List[List]:
        """按药名筛选并返回Dataframe格式"""
        filtered = self.structured_list.filter_by_drug_name(drug_name)
        return self._medicines_to_dataframe(filtered)

    def filter_by_expiry(self, before_date: str = None, after_date: str = None) -> List[List]:
        """按有效期筛选并返回Dataframe格式"""
        filtered = self.structured_list.filter_by_expiry(before_date, after_date)
        return self._medicines_to_dataframe(filtered)

    def sort_by_drug_name(self, reverse: bool = False) -> List[List]:
        """按药名排序并返回Dataframe格式"""
        sorted_list = self.structured_list.sort_by_drug_name(reverse)
        return self._medicines_to_dataframe(sorted_list)

    def sort_by_expiry(self, reverse: bool = False) -> List[List]:
        """按有效期排序并返回Dataframe格式"""
        sorted_list = self.structured_list.sort_by_expiry(reverse)
        return self._medicines_to_dataframe(sorted_list)

    def _medicines_to_dataframe(self, medicines: List[StructuredMedicine]) -> List[List]:
        """将药品列表转换为Dataframe格式"""
        return [
            medicine.to_dataframe_row(i + 1)
            for i, medicine in enumerate(medicines)
        ]

    def get_statistics(self) -> dict:
        """获取统计信息"""
        total = self.structured_list.count()

        # 统计各字段的填充率
        all_medicines = self.structured_list.get_all()

        stats = {
            'total': total,
            'with_brand_name': sum(1 for m in all_medicines if m.brand_name),
            'with_generic_name': sum(1 for m in all_medicines if m.generic_name),
            'with_specification': sum(1 for m in all_medicines if m.specification),
            'with_expiry_date': sum(1 for m in all_medicines if m.expiry_date),
        }

        return stats

    def clear_all(self) -> None:
        """清空所有结构化数据"""
        self.structured_list.clear()
        self.save_structured_data()
        logger.warning("已清空所有结构化数据")
