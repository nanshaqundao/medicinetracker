# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Medicine Information Management System V3.1** - A voice-based intelligent medicine tracking system designed for elderly users, with AI-powered text structuring capabilities.

This is **solution3-1**, an enhanced version of solution3 that adds:
- LLM-powered text structuring (converting "阿莫西林一盒2027年6月" into structured fields)
- Multi-tab Gradio interface with three functional modules
- Data analysis, filtering, and sorting capabilities

## Essential Commands

### Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python3 app.py

# The app will start on http://localhost:7860
```

### Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run a single test file
pytest tests/test_models.py

# Run a single test function
pytest tests/test_models.py::test_entry_creation
```

### Development

```bash
# Check for running processes on port 7860
lsof -ti:7860

# Kill process on port 7860
lsof -ti:7860 | xargs kill -9

# View application logs
tail -f app.log

# Check log file for errors
grep ERROR app.log
```

## Architecture Overview

### Four-Layer Architecture

```
┌─────────────────────────────────────┐
│  UI Layer (ui.py)                   │  Multi-tab Gradio interface
│  - Tab 1: Voice Collection          │  - Event bindings
│  - Tab 2: Intelligent Structuring   │  - State management
│  - Tab 3: Data Analysis             │
├─────────────────────────────────────┤
│  Service Layer                      │
│  - EntryService (service.py)        │  Business logic for raw entries
│  - MedicineParserService            │  LLM-powered text structuring
│    (text_parser.py)                 │
├─────────────────────────────────────┤
│  Model Layer (models.py)            │
│  - Entry / EntryList                │  Raw text entries
│  - StructuredMedicine /             │  Parsed structured data
│    StructuredMedicineList           │
├─────────────────────────────────────┤
│  Storage Layer (storage.py)         │
│  - JSONStorage                      │  File-based persistence
│  - Two data files:                  │
│    * voice_entries.json             │
│    * structured_medicines.json      │
└─────────────────────────────────────┘
```

### Data Flow

**Voice Collection (Tab 1):**
```
User Voice → Web Speech API → text_input → EntryService.add_entry()
→ Entry → EntryList → JSONStorage → voice_entries.json
```

**Intelligent Structuring (Tab 2):**
```
voice_entries.json → MedicineParserService.parse_batch()
→ ClaudeClient.parse_medicine_text() → Claude API
→ StructuredMedicine → StructuredMedicineList → structured_medicines.json
```

**Data Analysis (Tab 3):**
```
structured_medicines.json → MedicineParserService
→ filter/sort/statistics → Dataframe display
```

## Key Modules

### 1. models.py

Defines two parallel data model hierarchies:

**Raw Entry Model:**
- `Entry`: Single voice entry with id, text, timestamp
- `EntryList`: Collection with add, remove, search, export methods

**Structured Medicine Model:**
- `StructuredMedicine`: Parsed fields (drug_name, brand_name, generic_name, quantity, unit, specification, package_count, expiry_date, etc.)
- `StructuredMedicineList`: Collection with filter, sort, search, statistics methods

**Critical:** Both models use `@dataclass` for clean data representation.

### 2. llm_client.py

LLM integration layer supporting multiple providers (Claude, OpenAI, Ollama).

**Current Implementation:** ClaudeClient with Anthropic API
- Model: `claude-3-5-sonnet-20241022`
- Temperature: `0.3` (for consistent parsing)
- Max tokens: `1024`

**Key Method:** `parse_medicine_text(text: str) -> Dict[str, Any]`
- Takes raw Chinese text like "阿莫西林一盒2027年6月"
- Returns structured JSON with extracted fields
- Has fallback parsing if LLM fails

**Prompt Engineering:** The prompt in `_build_prompt()` is carefully crafted for Chinese medicine text extraction. When modifying, ensure it maintains JSON-only output format.

### 3. text_parser.py

**MedicineParserService** orchestrates the structuring pipeline:
- `parse_single_text()`: Parse one entry
- `parse_batch()`: Bulk parsing with error handling
- `parse_and_save()`: Parse + persist to storage
- `filter_by_drug_name()`, `sort_by_expiry()`: Query operations

**Important:** This service manages its own `StructuredMedicineList` and `JSONStorage` instance, separate from the raw entry storage.

### 4. ui.py

**Multi-tab Gradio Interface** - Complex event binding pattern:

**Critical Pattern:**
1. `build()` creates the gr.Blocks app with three tabs
2. Each tab has its own `_build_tab*()` method that creates UI components
3. Event bindings are called **AFTER** `self.app` is assigned (lines 52-54)
4. This prevents `AttributeError: 'NoneType' object has no attribute 'load'`

**Event Binding Order Matters:**
```python
# WRONG - will fail
def _build_tab1_voice_collection(self):
    # ... create components ...
    self._bind_tab1_events()  # self.app is None here!

# CORRECT - current implementation
def build(self):
    with gr.Blocks() as app:
        # ... build all tabs ...
    self.app = app
    # NOW bind events after app exists
    self._bind_tab1_events()
    self._bind_tab2_events()
    self._bind_tab3_events()
```

### 5. voice.py

Contains `VOICE_RECOGNITION_JS` - JavaScript code injected into Gradio for Web Speech API integration.

**Two modes:**
- `startVoiceRecognition()`: Single recognition, returns text
- `startContinuousVoice()`: Toggle continuous recognition with auto-submit

**Browser Requirement:** Chrome/Edge only (Firefox doesn't support Web Speech API).

### 6. service.py

**EntryService** handles raw voice entry business logic:
- `add_entry()`: Validates, creates Entry, saves, returns updated UI state
- `save_dataframe()`: Syncs Gradio table edits back to storage
- `refresh()`: Reloads from storage and returns updated UI state
- `clear_all()`: Deletes all entries

**Return Pattern:** Service methods return tuples for Gradio outputs:
```python
def add_entry(self, text: str):
    # ... logic ...
    return (status_msg, dataframe, count_display, cleared_input)
```

## Configuration

**config.py** holds all configuration:

```python
# Data files
DATA_FILE = "data/voice_entries.json"          # Raw entries
STRUCTURED_DATA_FILE = "data/structured_medicines.json"  # Parsed data

# Server
SERVER_PORT = 7860
SERVER_NAME = "0.0.0.0"

# LLM Settings
LLM_PROVIDER = "claude"
CLAUDE_API_KEY = "sk-ant-api03-..."  # User's API key
CLAUDE_MODEL = "claude-3-5-sonnet-20241022"
CLAUDE_TEMPERATURE = 0.3
```

**Logging:** Configured in `app.py`'s `setup_logging()`, outputs to both `app.log` and console.

## Important Development Patterns

### 1. Dataframe Conversion

Models have `to_dataframe()` and `to_dataframe_row()` methods for Gradio table compatibility:

```python
# In models.py
def to_dataframe(self) -> List[List]:
    return [entry.to_dataframe_row(i+1) for i, entry in enumerate(self.entries)]

def to_dataframe_row(self, index: int) -> List:
    return [index, self.text, self.timestamp, self.id]
```

### 2. Error Handling

All service methods have try-except blocks with logging:

```python
try:
    # ... operation ...
    logger.info(f"Operation succeeded: {details}")
except Exception as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    return error_message
```

### 3. Gradio State Management

**Critical:** Gradio components are stateless. Don't rely on component state between interactions.

- Always return updated data from service methods
- Use `app.load()` to initialize UI on page load
- For editable tables, explicitly save changes via service methods

### 4. Testing Strategy

Tests are organized by layer:
- `test_models.py`: Entry, EntryList, StructuredMedicine validation
- `test_storage.py`: JSONStorage read/write operations
- `test_service.py`: EntryService business logic

**Run tests before committing:** `pytest tests/`

## Common Pitfalls

### UI Event Binding

**Problem:** `AttributeError: 'NoneType' object has no attribute 'load'`

**Cause:** Calling `self.app.load()` before `self.app` is assigned.

**Solution:** Only bind events in `build()` after `self.app = app` (see lines 49-54 in ui.py).

### Port Already in Use

**Problem:** `OSError: Cannot find empty port in range: 7860-7860`

**Solution:**
```bash
lsof -ti:7860 | xargs kill -9
```

### Empty Dataframe on Browser Refresh

**Problem:** Table shows empty on browser refresh even though data exists.

**Solution:** Initialize Gradio components with empty values, only load via `app.load()`:
```python
# WRONG
dataframe = gr.Dataframe(value=self.service.get_dataframe())

# CORRECT
dataframe = gr.Dataframe(value=[])
# ... then in build():
app.load(fn=self.service.refresh, outputs=[dataframe, count_display])
```

### LLM API Failures

**Problem:** Claude API calls fail or return invalid JSON.

**Solution:** The `ClaudeClient` has fallback parsing in `_fallback_parse()`. Check logs for API errors. Verify API key in config.py.

## Project Structure

```
solution3-1/
├── app.py                    # Application entry point
├── config.py                 # Configuration
├── requirements.txt          # Dependencies
├── app.log                   # Runtime logs
│
├── src/
│   ├── models.py             # Entry + StructuredMedicine models
│   ├── storage.py            # JSONStorage for persistence
│   ├── service.py            # EntryService business logic
│   ├── text_parser.py        # MedicineParserService (LLM integration)
│   ├── llm_client.py         # ClaudeClient, OpenAIClient, OllamaClient
│   ├── ui.py                 # Multi-tab Gradio interface
│   └── voice.py              # Web Speech API JavaScript
│
├── data/
│   ├── voice_entries.json    # Raw voice entries
│   └── structured_medicines.json  # Parsed structured data
│
├── tests/
│   ├── test_models.py
│   ├── test_service.py
│   └── test_storage.py
│
├── README.md                 # User-facing documentation
├── DEVELOPMENT.md            # Developer documentation
└── discussion&todo.md        # Feature planning and notes
```

## Extending the System

### Adding a New LLM Provider

1. Create a new client class in `llm_client.py`:
   ```python
   class NewProviderClient(LLMClient):
       def parse_medicine_text(self, text: str) -> Dict[str, Any]:
           # Implementation
   ```

2. Update `create_llm_client()` factory function

3. Add configuration in `config.py`

### Adding New Structured Fields

1. Update `StructuredMedicine` dataclass in `models.py`
2. Update `to_dataframe_row()` to include new field
3. Modify LLM prompt in `llm_client.py` to extract new field
4. Update UI dataframe headers in `ui.py` (Tab 2 and Tab 3)

### Adding a New Tab

1. Create `_build_tab4_*()` method in `ui.py`
2. Add tab in `build()` method
3. Create `_bind_tab4_events()` method
4. Call binding method after `self.app = app`

## Version History

- **v3.1.0** (2025-11-19): Added LLM structuring, multi-tab UI, data analysis
- **v3.0.0** (2025-11-18): Initial voice collection system with editable tables and logging

## Related Files

- **User Docs:** README.md
- **Developer Docs:** DEVELOPMENT.md
- **Feature Planning:** discussion&todo.md
