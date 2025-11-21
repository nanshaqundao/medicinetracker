"""
测试service模块
"""

import pytest
from pathlib import Path
from src.storage import JSONStorage
from src.service import EntryService


@pytest.fixture
def temp_service(tmp_path):
    """创建临时服务"""
    file_path = tmp_path / "test_entries.json"
    storage = JSONStorage(file_path)
    return EntryService(storage)


class TestEntryService:
    """测试EntryService类"""

    def test_add_entry(self, temp_service):
        """测试添加条目"""
        status, df_data, count, text = temp_service.add_entry("测试药品1")

        assert "✅" in status
        assert len(df_data) == 1
        assert "1" in count
        assert text == ""  # 应该清空输入框

    def test_add_empty_entry(self, temp_service):
        """测试添加空条目"""
        status, df_data, count, text = temp_service.add_entry("")

        assert "❌" in status
        assert len(df_data) == 0

    def test_add_multiple_entries(self, temp_service):
        """测试添加多个条目"""
        temp_service.add_entry("药品1")
        temp_service.add_entry("药品2")
        status, df_data, count, _ = temp_service.add_entry("药品3")

        assert len(df_data) == 3
        assert "3" in count

    def test_clear_all(self, temp_service):
        """测试清空所有"""
        temp_service.add_entry("药品1")
        temp_service.add_entry("药品2")

        status, df_data, count = temp_service.clear_all()

        assert "✅" in status
        assert len(df_data) == 0
        assert "0" in count

    def test_get_dataframe(self, temp_service):
        """测试获取Dataframe数据"""
        temp_service.add_entry("药品A")
        temp_service.add_entry("药品B")

        df_data = temp_service.get_dataframe()
        assert len(df_data) == 2
        # 验证倒序
        assert df_data[0][1] == "药品B"
        assert df_data[1][1] == "药品A"

    def test_get_count(self, temp_service):
        """测试获取统计"""
        count = temp_service.get_count()
        assert "0" in count

        temp_service.add_entry("药品1")
        count = temp_service.get_count()
        assert "1" in count

    def test_refresh(self, temp_service):
        """测试刷新"""
        temp_service.add_entry("药品1")

        # 刷新应该重新加载数据
        df_data, count = temp_service.refresh()
        assert len(df_data) == 1
        assert "1" in count

    def test_export_to_text(self, temp_service):
        """测试导出文本"""
        # 空列表导出应该返回None
        result = temp_service.export_to_text()
        assert result is None

        # 添加数据后导出
        temp_service.add_entry("药品1")
        temp_service.add_entry("药品2")

        filepath = temp_service.export_to_text()
        assert filepath is not None

        # 验证文件内容
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "1. 药品1" in content
            assert "2. 药品2" in content

        # 清理导出文件
        Path(filepath).unlink()

    def test_data_persistence(self, temp_service):
        """测试数据持久化"""
        # 添加数据
        temp_service.add_entry("药品X")
        temp_service.add_entry("药品Y")

        # 创建新服务实例（模拟重启应用）
        new_service = EntryService(temp_service.storage)

        # 验证数据还在
        df_data = new_service.get_dataframe()
        assert len(df_data) == 2
        assert df_data[0][1] == "药品Y"
        assert df_data[1][1] == "药品X"

    def test_delete_entry(self, temp_service):
        """测试删除条目"""
        # 先清空
        temp_service.clear_all()

        # 添加一些数据并获取所有ID
        import time
        temp_service.add_entry("药品1")
        time.sleep(0.001)  # 确保时间戳不同
        temp_service.add_entry("药品2")
        time.sleep(0.001)
        temp_service.add_entry("药品3")

        # 获取当前所有数据
        df_data = temp_service.get_dataframe()

        # 删除第二条（df_data是倒序的，所以索引1是倒数第二条，即药品2）
        entry_id = df_data[1][3]  # 第二行的ID列

        # 删除
        status, df_data, count = temp_service.delete_entry(entry_id)

        assert "✅" in status
        assert len(df_data) == 2
        assert "2" in count

        # 验证删除的是正确的条目
        texts = [row[1] for row in df_data]
        assert "药品1" in texts
        assert "药品3" in texts

    def test_delete_entry_not_found(self, temp_service):
        """测试删除不存在的条目"""
        temp_service.add_entry("药品1")

        status, _, _ = temp_service.delete_entry(999999)
        assert "❌" in status

    def test_delete_entry_no_selection(self, temp_service):
        """测试未选择条目时删除"""
        status, _, _ = temp_service.delete_entry(None)
        assert "❌" in status
        assert "选择" in status

    def test_update_entry(self, temp_service):
        """测试更新条目"""
        # 添加数据
        _, df_data, _, _ = temp_service.add_entry("原始药品")

        # 获取ID
        entry_id = df_data[0][3]

        # 更新
        status, df_data, count, _ = temp_service.update_entry(entry_id, "更新后的药品")

        assert "✅" in status
        assert df_data[0][1] == "更新后的药品"

    def test_update_entry_empty_text(self, temp_service):
        """测试更新为空文本"""
        _, df_data, _, _ = temp_service.add_entry("药品1")
        entry_id = df_data[0][3]

        status, _, _, _ = temp_service.update_entry(entry_id, "")
        assert "❌" in status

        status, _, _, _ = temp_service.update_entry(entry_id, "   ")
        assert "❌" in status

    def test_update_entry_not_found(self, temp_service):
        """测试更新不存在的条目"""
        temp_service.add_entry("药品1")

        status, _, _, _ = temp_service.update_entry(999999, "新文本")
        assert "❌" in status

    def test_update_entry_no_selection(self, temp_service):
        """测试未选择条目时更新"""
        status, _, _, _ = temp_service.update_entry(None, "新文本")
        assert "❌" in status
        assert "选择" in status

    def test_get_entry_choices(self, temp_service):
        """测试获取条目选择列表"""
        # 空列表
        choices = temp_service.get_entry_choices()
        assert choices == []

        # 添加数据
        temp_service.add_entry("药品A")
        temp_service.add_entry("药品B")
        temp_service.add_entry("药品C")

        choices = temp_service.get_entry_choices()
        assert len(choices) == 3

        # 验证格式 (显示文本, ID)
        assert isinstance(choices[0], tuple)
        assert len(choices[0]) == 2

        # 验证倒序（最新的在前）
        assert "3" in choices[0][0]  # 第一个应该是#3
        assert "药品C" in choices[0][0]

    def test_get_entry_text(self, temp_service):
        """测试获取条目文本"""
        # 添加数据
        _, df_data, _, _ = temp_service.add_entry("测试药品")
        entry_id = df_data[0][3]

        # 获取文本
        text = temp_service.get_entry_text(entry_id)
        assert text == "测试药品"

    def test_get_entry_text_not_found(self, temp_service):
        """测试获取不存在的条目文本"""
        text = temp_service.get_entry_text(999999)
        assert text == ""

    def test_get_entry_text_none(self, temp_service):
        """测试传入None"""
        text = temp_service.get_entry_text(None)
        assert text == ""

    def test_save_dataframe(self, temp_service):
        """测试保存Dataframe编辑"""
        # 添加初始数据
        temp_service.add_entry("药品1")
        temp_service.add_entry("药品2")

        # 获取当前dataframe
        df_data = temp_service.get_dataframe()

        # 模拟编辑: 修改第一条的文本
        df_data[0][1] = "修改后的药品2"

        # 保存
        status, new_df, count = temp_service.save_dataframe(df_data)

        assert "✅" in status
        assert new_df[0][1] == "修改后的药品2"

    def test_save_dataframe_delete_row(self, temp_service):
        """测试通过Dataframe删除行"""
        # 添加3条数据
        import time
        temp_service.add_entry("药品1")
        time.sleep(0.001)
        temp_service.add_entry("药品2")
        time.sleep(0.001)
        temp_service.add_entry("药品3")

        # 获取dataframe
        df_data = temp_service.get_dataframe()

        # 删除中间一行（索引1）
        df_data.pop(1)

        # 保存
        status, new_df, count = temp_service.save_dataframe(df_data)

        assert "✅" in status
        assert len(new_df) == 2
        assert "2" in count

    def test_save_dataframe_empty(self, temp_service):
        """测试保存空Dataframe"""
        temp_service.add_entry("药品1")

        # 保存空列表
        status, new_df, count = temp_service.save_dataframe([])

        assert "✅" in status
        assert len(new_df) == 0
        assert "0" in count

    def test_save_dataframe_with_none_values(self, temp_service):
        """测试保存包含None值的Dataframe（模拟Gradio删除行为）"""
        temp_service.add_entry("药品1")
        temp_service.add_entry("药品2")

        # 获取dataframe
        df_data = temp_service.get_dataframe()

        # 模拟Gradio返回的数据：包含None值的行
        df_data_with_none = [
            [1, "药品A", "2025-01-01 10:00:00", 12345],
            [2, None, "2025-01-01 11:00:00", 12346],  # 文本为None - 应该被跳过
            [3, "药品C", "2025-01-01 12:00:00", 12347],
        ]

        status, new_df, count = temp_service.save_dataframe(df_data_with_none)

        assert "✅" in status
        assert len(new_df) == 2  # None行被跳过
        assert "2" in count

    def test_save_dataframe_with_string_ids(self, temp_service):
        """测试保存包含字符串ID的Dataframe（Gradio可能返回字符串）"""
        # 模拟Gradio返回字符串ID（倒序，最新在前）
        df_data = [
            [2, "药品2", "2025-01-01 11:00:00", "12346.0"],  # ID是浮点字符串，最新在前
            [1, "药品1", "2025-01-01 10:00:00", "12345"],  # ID是字符串
        ]

        status, new_df, count = temp_service.save_dataframe(df_data)

        assert "✅" in status
        assert len(new_df) == 2
        # 验证倒序显示（最新在前）
        assert new_df[0][1] == "药品2"
        assert new_df[1][1] == "药品1"

    def test_save_dataframe_with_none_string(self, temp_service):
        """测试保存包含'None'字符串的Dataframe"""
        df_data = [
            [1, "药品1", "2025-01-01 10:00:00", 12345],
            [2, "None", "2025-01-01 11:00:00", 12346],  # 文本是字符串"None" - 应该被跳过
            [3, "药品3", "2025-01-01 12:00:00", 12347],
        ]

        status, new_df, count = temp_service.save_dataframe(df_data)

        assert "✅" in status
        assert len(new_df) == 2  # "None"行被跳过
        texts = [row[1] for row in new_df]
        assert "药品1" in texts
        assert "药品3" in texts
        assert "None" not in texts

    def test_save_dataframe_with_pandas_dataframe(self, temp_service):
        """测试保存pandas DataFrame对象（Gradio传递的真实格式）"""
        try:
            import pandas as pd
        except ImportError:
            import pytest
            pytest.skip("pandas not installed")

        # 添加一些初始数据
        temp_service.add_entry("药品1")
        temp_service.add_entry("药品2")

        # 获取dataframe
        df_list = temp_service.get_dataframe()

        # 转换为pandas DataFrame（模拟Gradio的行为）
        df_pandas = pd.DataFrame(df_list, columns=["#", "药品信息", "录入时间", "ID"])

        # 修改第一行
        df_pandas.loc[0, "药品信息"] = "修改后的药品2"

        # 保存
        status, new_df, count = temp_service.save_dataframe(df_pandas)

        assert "✅" in status
        assert len(new_df) == 2
        assert new_df[0][1] == "修改后的药品2"
