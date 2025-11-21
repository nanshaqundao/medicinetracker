
import pytest
from pathlib import Path
import shutil
from src.service import EntryService
from src.text_parser import MedicineParserService

# Setup temporary data directory
@pytest.fixture
def temp_data_dir(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir

def test_entry_service_isolation(temp_data_dir):
    service = EntryService(temp_data_dir)
    
    # User A adds an entry
    service.add_entry("Medicine A", "user_a")
    
    # User B adds an entry
    service.add_entry("Medicine B", "user_b")
    
    # Verify User A sees only Medicine A
    df_a = service.get_dataframe("user_a")
    assert len(df_a) == 1
    assert df_a[0][1] == "Medicine A"
    
    # Verify User B sees only Medicine B
    df_b = service.get_dataframe("user_b")
    assert len(df_b) == 1
    assert df_b[0][1] == "Medicine B"
    
    # Verify files are created correctly
    assert (temp_data_dir / "voice_entries_user_a.json").exists()
    assert (temp_data_dir / "voice_entries_user_b.json").exists()

def test_parser_service_isolation(temp_data_dir):
    # Mock LLM client to avoid API calls
    class MockLLM:
        def parse_medicine_text(self, text):
            return {"drug_name": text, "quantity": 1}
            
    service = MedicineParserService(temp_data_dir, llm_client=MockLLM())
    
    # User A parses text
    from src.models import Entry
    entries_a = [Entry(1, "Aspirin", "time")]
    service.parse_and_save(entries_a, "user_a")
    
    # User B parses text
    entries_b = [Entry(2, "Ibuprofen", "time")]
    service.parse_and_save(entries_b, "user_b")
    
    # Verify User A data
    df_a = service.get_structured_dataframe("user_a")
    assert len(df_a) == 1
    assert df_a[0][1] == "Aspirin"
    
    # Verify User B data
    df_b = service.get_structured_dataframe("user_b")
    assert len(df_b) == 1
    assert df_b[0][1] == "Ibuprofen"
    
    # Verify files
    assert (temp_data_dir / "structured_medicines_user_a.json").exists()
    assert (temp_data_dir / "structured_medicines_user_b.json").exists()
