"""
测试storage模块
"""

import json
import pytest
from pathlib import Path
from src.storage import JSONStorage


@pytest.fixture
def temp_storage(tmp_path):
    """创建临时存储"""
    file_path = tmp_path / "test_entries.json"
    return JSONStorage(file_path)


class TestJSONStorage:
    """测试JSONStorage类"""

    def test_save_and_load(self, temp_storage):
        """测试保存和加载"""
        test_data = [
            {'id': 1, 'text': "药品1", 'timestamp': "2025-01-01 10:00:00"},
            {'id': 2, 'text': "药品2", 'timestamp': "2025-01-02 11:00:00"}
        ]

        # 保存
        success = temp_storage.save(test_data)
        assert success is True

        # 加载
        loaded_data = temp_storage.load()
        assert len(loaded_data) == 2
        assert loaded_data[0]['text'] == "药品1"
        assert loaded_data[1]['text'] == "药品2"

    def test_load_nonexistent_file(self, temp_storage):
        """测试加载不存在的文件"""
        loaded_data = temp_storage.load()
        assert loaded_data == []

    def test_load_empty_file(self, temp_storage):
        """测试加载空文件"""
        # 创建空JSON文件
        temp_storage.file_path.write_text("[]", encoding='utf-8')

        loaded_data = temp_storage.load()
        assert loaded_data == []

    def test_load_invalid_json(self, temp_storage):
        """测试加载无效JSON"""
        # 写入无效JSON
        temp_storage.file_path.write_text("invalid json", encoding='utf-8')

        loaded_data = temp_storage.load()
        assert loaded_data == []

    def test_save_empty_list(self, temp_storage):
        """测试保存空列表"""
        success = temp_storage.save([])
        assert success is True

        loaded_data = temp_storage.load()
        assert loaded_data == []

    def test_clear(self, temp_storage):
        """测试清空"""
        # 先保存一些数据
        test_data = [{'id': 1, 'text': "药品1", 'timestamp': "2025-01-01 10:00:00"}]
        temp_storage.save(test_data)

        # 清空
        success = temp_storage.clear()
        assert success is True

        # 验证已清空
        loaded_data = temp_storage.load()
        assert loaded_data == []

    def test_exists(self, temp_storage):
        """测试文件存在检查"""
        assert not temp_storage.exists()

        # 保存后应该存在
        temp_storage.save([])
        assert temp_storage.exists()

    def test_save_creates_parent_directory(self, tmp_path):
        """测试保存时自动创建父目录"""
        nested_path = tmp_path / "nested" / "dir" / "test.json"
        storage = JSONStorage(nested_path)

        success = storage.save([{'id': 1, 'text': "test"}])
        assert success is True
        assert nested_path.exists()
