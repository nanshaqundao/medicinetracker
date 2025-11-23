"""
文本结构化解析服务
将原始文本转换为结构化药品数据
"""

import logging
from pathlib import Path
from typing import List, Tuple, Dict
from .models import Entry, EntryList, StructuredMedicine, StructuredMedicineList
from .storage import JSONStorage
from .llm_client import create_llm_client
import config

logger = logging.getLogger(__name__)


class MedicineParserService:
    """药品文本解析服务"""

    def __init__(self, data_dir: Path, llm_client=None):
        """
        初始化解析服务

        Args:
            data_dir: 数据目录
            llm_client: LLM客户端（如果为None，则自动创建）
        """
        self.data_dir = data_dir
        # 内存缓存：user_id -> StructuredMedicineList
        self.sessions: Dict[str, StructuredMedicineList] = {}
        
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

        logger.info("MedicineParserService 初始化完成")

    def _get_storage(self, user_id: str) -> JSONStorage:
        """获取指定用户的存储对象"""
        user_id = user_id.strip() if user_id else "default"
        file_path = self.data_dir / f"structured_medicines_{user_id}.json"
        return JSONStorage(file_path)

    def _get_structured_list(self, user_id: str) -> StructuredMedicineList:
        """获取指定用户的结构化数据列表（带缓存）"""
        user_id = user_id.strip() if user_id else "default"
        
        # 如果缓存中没有，则加载
        if user_id not in self.sessions:
            storage = self._get_storage(user_id)
            data = storage.load()
            if data:
                self.sessions[user_id] = StructuredMedicineList.from_dict_list(data)
                logger.info(f"加载用户结构化数据: {user_id}, {len(data)} 条")
            else:
                self.sessions[user_id] = StructuredMedicineList()
                logger.info(f"初始化用户结构化数据: {user_id}")
            
        return self.sessions[user_id]

    def load_structured_data(self, user_id: str) -> None:
        """从存储加载结构化数据（强制刷新）"""
        if user_id in self.sessions:
            del self.sessions[user_id]
        self._get_structured_list(user_id)

    def save_structured_data(self, user_id: str) -> bool:
        """保存结构化数据到存储"""
        structured_list = self._get_structured_list(user_id)
        storage = self._get_storage(user_id)
        
        data = structured_list.to_dict_list()
        result = storage.save(data)
        if result:
            logger.info(f"保存结构化数据成功: {user_id}, {len(data)} 条")
        return result

    def export_to_csv(self, user_id: str) -> str:
        """
        导出结构化数据为CSV文件
        
        Args:
            user_id: 用户ID
            
        Returns:
            导出的文件路径，如果没有数据则返回None
        """
        from pathlib import Path
        from datetime import datetime
        import pandas as pd
        
        structured_list = self._get_structured_list(user_id)
        if not structured_list or structured_list.count() == 0:
            logger.warning("导出失败: 没有数据")
            return None
        
        filename = f"structured_medicines_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = Path("data") / filename
        
        # 确保data目录存在
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # 转换为DataFrame
            df_data = structured_list.to_dataframe()
            headers = ["#", "药名", "商品名", "学术名", "数量", "单位", "规格", "包装", "有效期", "原文", "时间"]
            df = pd.DataFrame(df_data, columns=headers)
            
            # 导出CSV
            df.to_csv(filepath, index=False, encoding='utf-8-sig')  # utf-8-sig以支持Excel打开
            logger.info(f"导出成功: {filepath}, {structured_list.count()} 条")
            return str(filepath)
        except Exception as e:
            logger.error(f"导出失败: {e}", exc_info=True)
            return None

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
        
        # 从配置读取批次大小
        import config
        batch_size = config.LLM_BATCH_SIZE
        logger.info(f"使用批次大小: {batch_size}")
        
        # 分批处理
        for i in range(0, len(entries), batch_size):
            batch = entries[i:i+batch_size]
            texts = [entry.text for entry in batch]
            
            try:
                # 调用批量API
                logger.info(f"处理批次 {i//batch_size + 1}: {len(texts)} 条")
                parsed_results = self.llm_client.parse_medicine_batch(texts)
                
                # 将结果映射回原始数据
                for j, parsed_data in enumerate(parsed_results):
                    original_text = batch[j].text
                    
                    try:
                        # 创建StructuredMedicine对象
                        medicine = StructuredMedicine.create(
                            original_text=original_text,
                            drug_name=parsed_data.get('drug_name', ''),
                            brand_name=parsed_data.get('brand_name', ''),
                            generic_name=parsed_data.get('generic_name', ''),
                            quantity=parsed_data.get('quantity', 0.0),
                            unit=parsed_data.get('unit', ''),
                            specification=parsed_data.get('specification', ''),
                            package_count=parsed_data.get('package_count', ''),
                            expiry_date=parsed_data.get('expiry_date', '')
                        )
                        
                        if medicine.is_valid():
                            success_list.append(medicine)
                        else:
                            logger.warning(f"解析结果无效: {original_text}")
                            failed_list.append(original_text)
                    except Exception as e:
                        logger.error(f"创建Medicine对象失败: {original_text}, 错误: {e}")
                        failed_list.append(original_text)
                        
            except Exception as e:
                logger.error(f"批次处理失败: {e}", exc_info=True)
                # 如果批次失败，将所有文本加入失败列表
                for entry in batch:
                    failed_list.append(entry.text)
        
        logger.info(f"批量解析完成: 成功 {len(success_list)}, 失败 {len(failed_list)}")
        return success_list, failed_list

    def parse_and_save(self, entries: List[Entry], user_id: str, append: bool = False) -> Tuple[int, int, List[str]]:
        """
        解析并保存
        
        Args:
            entries: Entry对象列表
            user_id: 用户ID
            append: 是否追加模式（True=追加，False=覆盖）
            
        Returns:
            (成功数量, 失败数量, 失败文本列表)
        """
        success_list, failed_list = self.parse_batch(entries)
        structured_list = self._get_structured_list(user_id)
        
        # 如果不是追加模式，先清空
        if not append:
            structured_list.clear()

        # 添加到列表
        for medicine in success_list:
            try:
                structured_list.add(medicine)
            except ValueError as e:
                logger.error(f"添加失败: {e}")
                failed_list.append(medicine.original_text)

        # 保存
        self.save_structured_data(user_id)

        return len(success_list), len(failed_list), failed_list

    def get_all_structured(self, user_id: str) -> List[StructuredMedicine]:
        """获取所有结构化数据"""
        structured_list = self._get_structured_list(user_id)
        return structured_list.get_all()

    def get_structured_dataframe(self, user_id: str) -> List[List]:
        """获取结构化数据的Dataframe格式"""
        structured_list = self._get_structured_list(user_id)
        return structured_list.to_dataframe()

    def filter_by_drug_name(self, drug_name: str, user_id: str) -> List[List]:
        """按药名筛选并返回Dataframe格式"""
        structured_list = self._get_structured_list(user_id)
        filtered = structured_list.filter_by_drug_name(drug_name)
        return self._medicines_to_dataframe(filtered)

    def filter_by_expiry(self, user_id: str, before_date: str = None, after_date: str = None) -> List[List]:
        """按有效期筛选并返回Dataframe格式"""
        structured_list = self._get_structured_list(user_id)
        filtered = structured_list.filter_by_expiry(before_date, after_date)
        return self._medicines_to_dataframe(filtered)

    def sort_by_drug_name(self, user_id: str, reverse: bool = False) -> List[List]:
        """按药名排序并返回Dataframe格式"""
        structured_list = self._get_structured_list(user_id)
        sorted_list = structured_list.sort_by_drug_name(reverse)
        return self._medicines_to_dataframe(sorted_list)

    def sort_by_expiry(self, user_id: str, reverse: bool = False) -> List[List]:
        """按有效期排序并返回Dataframe格式"""
        structured_list = self._get_structured_list(user_id)
        sorted_list = structured_list.sort_by_expiry(reverse)
        return self._medicines_to_dataframe(sorted_list)

    def _medicines_to_dataframe(self, medicines: List[StructuredMedicine]) -> List[List]:
        """将药品列表转换为Dataframe格式"""
        return [
            medicine.to_dataframe_row(i + 1)
            for i, medicine in enumerate(medicines)
        ]

    def update_from_dataframe(self, user_id: str, df_data: List[List]) -> bool:
        """
        从Dataframe数据更新结构化列表
        
        Args:
            user_id: 用户ID
            df_data: Dataframe数据列表
            
        Returns:
            是否更新成功
        """
        try:
            structured_list = self._get_structured_list(user_id)
            structured_list.clear()
            
            for row in df_data:
                # headers=["#", "药名", "商品名", "学术名", "数量", "单位", "规格", "包装", "有效期", "原文", "时间"]
                if len(row) < 10:
                    continue
                    
                # 从row重建StructuredMedicine
                # 注意：row[0]是序号，跳过
                # 使用create方法会自动生成ID和时间（如果未提供）
                # 这里我们尽量保留原有信息
                
                medicine = StructuredMedicine.create(
                    original_text=str(row[9]) if row[9] else "",
                    drug_name=str(row[1]) if row[1] else "",
                    brand_name=str(row[2]) if row[2] else "",
                    generic_name=str(row[3]) if row[3] else "",
                    quantity=float(row[4]) if row[4] else 0.0,
                    unit=str(row[5]) if row[5] else "",
                    specification=str(row[6]) if row[6] else "",
                    package_count=str(row[7]) if row[7] else "",
                    expiry_date=str(row[8]) if row[8] else ""
                )
                # 如果有时间，覆盖默认生成的
                if len(row) > 10 and row[10]:
                    medicine.timestamp = str(row[10])
                    
                structured_list.add(medicine)
                
            return True
        except Exception as e:
            logger.error(f"更新结构化数据失败: {e}")
            return False

    def get_statistics(self, user_id: str) -> dict:
        """获取统计信息"""
        structured_list = self._get_structured_list(user_id)
        total = structured_list.count()

        # 统计各字段的填充率
        all_medicines = structured_list.get_all()

        stats = {
            'total': total,
            'with_brand_name': sum(1 for m in all_medicines if m.brand_name),
            'with_generic_name': sum(1 for m in all_medicines if m.generic_name),
            'with_specification': sum(1 for m in all_medicines if m.specification),
            'with_expiry_date': sum(1 for m in all_medicines if m.expiry_date),
        }

        return stats

    def clear_all(self, user_id: str) -> None:
        """清空所有结构化数据"""
        structured_list = self._get_structured_list(user_id)
        structured_list.clear()
        self.save_structured_data(user_id)
        logger.warning(f"用户 {user_id} 已清空所有结构化数据")
