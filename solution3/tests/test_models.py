"""
测试models模块
"""

import pytest
from src.models import Entry, EntryList


class TestEntry:
    """测试Entry类"""

    def test_create_entry(self):
        """测试创建Entry"""
        entry = Entry.create("测试药品")
        assert entry.text == "测试药品"
        assert entry.id > 0
        assert len(entry.timestamp) > 0

    def test_entry_to_dict(self):
        """测试Entry转字典"""
        entry = Entry(id=123, text="药品A", timestamp="2025-01-01 10:00:00")
        data = entry.to_dict()

        assert data['id'] == 123
        assert data['text'] == "药品A"
        assert data['timestamp'] == "2025-01-01 10:00:00"

    def test_entry_from_dict(self):
        """测试从字典创建Entry"""
        data = {'id': 456, 'text': "药品B", 'timestamp': "2025-01-02 11:00:00"}
        entry = Entry.from_dict(data)

        assert entry.id == 456
        assert entry.text == "药品B"
        assert entry.timestamp == "2025-01-02 11:00:00"

    def test_entry_to_dataframe_row(self):
        """测试Entry转Dataframe行"""
        entry = Entry(id=789, text="药品C", timestamp="2025-01-03 12:00:00")
        row = entry.to_dataframe_row(number=5)

        assert row == [5, "药品C", "2025-01-03 12:00:00", 789]


class TestEntryList:
    """测试EntryList类"""

    def test_create_empty_list(self):
        """测试创建空列表"""
        entry_list = EntryList()
        assert len(entry_list) == 0
        assert not entry_list

    def test_add_entry(self):
        """测试添加条目"""
        entry_list = EntryList()
        entry = entry_list.add("测试药品1")

        assert len(entry_list) == 1
        assert entry.text == "测试药品1"

    def test_add_empty_entry(self):
        """测试添加空条目应该失败"""
        entry_list = EntryList()

        with pytest.raises(ValueError):
            entry_list.add("")

        with pytest.raises(ValueError):
            entry_list.add("   ")

    def test_get_all(self):
        """测试获取所有条目"""
        entry_list = EntryList()
        entry_list.add("药品1")
        entry_list.add("药品2")

        entries = entry_list.get_all()
        assert len(entries) == 2
        assert entries[0].text == "药品1"
        assert entries[1].text == "药品2"

    def test_get_reversed(self):
        """测试获取倒序条目"""
        entry_list = EntryList()
        entry_list.add("药品1")
        entry_list.add("药品2")
        entry_list.add("药品3")

        reversed_entries = entry_list.get_reversed()
        assert len(reversed_entries) == 3
        assert reversed_entries[0].text == "药品3"
        assert reversed_entries[1].text == "药品2"
        assert reversed_entries[2].text == "药品1"

    def test_clear(self):
        """测试清空"""
        entry_list = EntryList()
        entry_list.add("药品1")
        entry_list.add("药品2")

        assert len(entry_list) == 2

        entry_list.clear()
        assert len(entry_list) == 0
        assert not entry_list

    def test_to_dict_list(self):
        """测试转字典列表"""
        entry_list = EntryList()
        entry_list.add("药品1")
        entry_list.add("药品2")

        dict_list = entry_list.to_dict_list()
        assert len(dict_list) == 2
        assert dict_list[0]['text'] == "药品1"
        assert dict_list[1]['text'] == "药品2"

    def test_to_dataframe(self):
        """测试转Dataframe格式"""
        entry_list = EntryList()
        entry_list.add("药品A")
        entry_list.add("药品B")
        entry_list.add("药品C")

        df_data = entry_list.to_dataframe()
        assert len(df_data) == 3

        # 验证倒序（最新的在前）
        assert df_data[0][0] == 3  # 序号3
        assert df_data[0][1] == "药品C"
        assert df_data[2][0] == 1  # 序号1
        assert df_data[2][1] == "药品A"

    def test_from_dict_list(self):
        """测试从字典列表创建"""
        dict_list = [
            {'id': 1, 'text': "药品X", 'timestamp': "2025-01-01 10:00:00"},
            {'id': 2, 'text': "药品Y", 'timestamp': "2025-01-02 11:00:00"}
        ]

        entry_list = EntryList.from_dict_list(dict_list)
        assert len(entry_list) == 2
        assert entry_list.entries[0].text == "药品X"
        assert entry_list.entries[1].text == "药品Y"

    def test_delete_by_id(self):
        """测试根据ID删除"""
        # 手动创建不同ID的条目以避免时间戳冲突
        entry1 = Entry(id=1001, text="药品1", timestamp="2025-01-01 10:00:00")
        entry2 = Entry(id=1002, text="药品2", timestamp="2025-01-01 11:00:00")
        entry3 = Entry(id=1003, text="药品3", timestamp="2025-01-01 12:00:00")

        entry_list = EntryList([entry1, entry2, entry3])

        # 删除中间的条目
        result = entry_list.delete_by_id(entry2.id)
        assert result is True
        assert len(entry_list) == 2

        # 验证删除的是正确的条目
        texts = [e.text for e in entry_list.entries]
        assert "药品1" in texts
        assert "药品2" not in texts
        assert "药品3" in texts

    def test_delete_by_id_not_found(self):
        """测试删除不存在的ID"""
        entry_list = EntryList()
        entry_list.add("药品1")

        result = entry_list.delete_by_id(999999)
        assert result is False
        assert len(entry_list) == 1

    def test_update_by_id(self):
        """测试根据ID更新"""
        entry_list = EntryList()
        entry1 = entry_list.add("药品1")
        entry2 = entry_list.add("药品2")

        # 更新第一个条目
        result = entry_list.update_by_id(entry1.id, "更新后的药品1")
        assert result is True

        # 验证更新成功
        updated_entry = entry_list.get_by_id(entry1.id)
        assert updated_entry.text == "更新后的药品1"

    def test_update_by_id_empty_text(self):
        """测试更新为空文本应该失败"""
        entry_list = EntryList()
        entry = entry_list.add("药品1")

        with pytest.raises(ValueError):
            entry_list.update_by_id(entry.id, "")

        with pytest.raises(ValueError):
            entry_list.update_by_id(entry.id, "   ")

    def test_update_by_id_not_found(self):
        """测试更新不存在的ID"""
        entry_list = EntryList()
        entry_list.add("药品1")

        result = entry_list.update_by_id(999999, "新文本")
        assert result is False

    def test_get_by_id(self):
        """测试根据ID获取"""
        # 手动创建不同ID的条目
        entry1 = Entry(id=2001, text="药品1", timestamp="2025-01-01 10:00:00")
        entry2 = Entry(id=2002, text="药品2", timestamp="2025-01-01 11:00:00")

        entry_list = EntryList([entry1, entry2])

        # 获取存在的条目
        found = entry_list.get_by_id(entry1.id)
        assert found is not None
        assert found.text == "药品1"

        found = entry_list.get_by_id(entry2.id)
        assert found is not None
        assert found.text == "药品2"

    def test_get_by_id_not_found(self):
        """测试获取不存在的ID"""
        entry_list = EntryList()
        entry_list.add("药品1")

        found = entry_list.get_by_id(999999)
        assert found is None
