# 药品信息收集器 V3 - 开发文档

> 📚 开发者完整指南 - 架构设计、技术实现与最佳实践

本文档面向开发者和贡献者，提供项目的完整技术细节。

---

## 📑 目录

- [架构设计](#架构设计)
- [技术栈](#技术栈)
- [模块详解](#模块详解)
- [数据流程](#数据流程)
- [API 文档](#api-文档)
- [日志系统](#日志系统)
- [开发指南](#开发指南)
- [测试指南](#测试指南)
- [代码规范](#代码规范)
- [性能优化](#性能优化)
- [故障排查](#故障排查)

---

## 🏗️ 架构设计

### 分层架构

项目采用经典的四层架构模式，职责分离，易于维护和扩展：

```
┌─────────────────────────────────────┐
│      Presentation Layer (UI)       │  ui.py
│      - Gradio 界面组件              │  - 事件绑定
│      - 用户交互处理                 │  - 状态管理
├─────────────────────────────────────┤
│    Business Logic Layer (Service)   │  service.py
│      - 业务规则验证                 │  - 条目管理
│      - 数据转换                     │  - 导出逻辑
├─────────────────────────────────────┤
│       Data Model Layer (Models)     │  models.py
│      - Entry 实体                   │  - EntryList 集合
│      - 数据验证                     │  - 序列化/反序列化
├─────────────────────────────────────┤
│   Data Access Layer (Storage)       │  storage.py
│      - JSON 文件读写                │  - 数据持久化
│      - 异常处理                     │  - 文件管理
└─────────────────────────────────────┘
```

### 设计原则

1. **单一职责** - 每个模块只负责一个功能领域
2. **依赖倒置** - 高层模块不依赖低层模块，都依赖抽象
3. **开放封闭** - 对扩展开放，对修改封闭
4. **接口隔离** - 使用类型提示定义清晰的接口

### 关键设计决策

#### 为什么选择 Gradio？

- ✅ 快速构建 Web UI，无需前端开发
- ✅ 原生支持表格编辑
- ✅ 内置服务器，部署简单
- ✅ 自动生成 API 端点

#### 为什么使用 JSON 存储？

- ✅ 人类可读，便于调试
- ✅ 无需数据库依赖
- ✅ 易于备份和迁移
- ✅ 适合小规模数据（< 10000条）

#### 为什么采用 Web Speech API？

- ✅ 浏览器原生支持，无需后端
- ✅ 识别准确度高（Google引擎）
- ✅ 支持中文和多语言
- ❌ 仅限 Chrome/Edge 浏览器

---

## 🛠️ 技术栈

### 后端框架

| 组件 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.10+ | 主要编程语言 |
| **Gradio** | 5.0+ | Web UI 框架 |
| **logging** | 标准库 | 日志记录 |
| **json** | 标准库 | 数据序列化 |
| **pathlib** | 标准库 | 路径处理 |
| **dataclasses** | 标准库 | 数据类定义 |

### 前端技术

| 组件 | 用途 |
|------|------|
| **Web Speech API** | 语音识别 |
| **JavaScript** | 客户端逻辑 |
| **Gradio Components** | UI 组件 |

### 测试工具

| 组件 | 版本 | 用途 |
|------|------|------|
| **pytest** | 7.0+ | 测试框架 |
| **pytest-cov** | 4.0+ | 代码覆盖率 |

---

## 📦 模块详解

### 1. models.py - 数据模型层

#### Entry 类

表示单条药品记录。

```python
@dataclass
class Entry:
    id: int              # 唯一ID（毫秒时间戳）
    text: str           # 药品信息文本
    timestamp: str      # 录入时间 "YYYY-MM-DD HH:MM:SS"
```

**核心方法：**

- `to_dict()` - 转换为字典（用于JSON序列化）
- `from_dict()` - 从字典创建（反序列化）
- `to_dataframe_row()` - 转换为表格行

**设计考量：**
- 使用时间戳作为ID保证唯一性
- 文本字段不做格式验证，保持灵活性
- 使用 `@dataclass` 减少样板代码

#### EntryList 类

管理 Entry 集合的容器类。

```python
class EntryList:
    entries: List[Entry]
```

**核心方法：**

- `add(text: str) -> Entry` - 添加新条目
- `get_all() -> List[Entry]` - 获取所有条目
- `get_reversed()` - 倒序获取（最新的在前）
- `clear()` - 清空所有条目
- `to_dataframe()` - 转换为 Gradio Dataframe 格式
- `to_dict_list()` - 序列化为字典列表
- `from_dict_list()` - 从字典列表反序列化

**设计考量：**
- 封装列表操作，隐藏实现细节
- 提供高级方法如倒序、格式转换
- 自动生成ID和时间戳

### 2. storage.py - 存储层

#### JSONStorage 类

负责数据持久化到 JSON 文件。

```python
class JSONStorage:
    def __init__(self, file_path: Path)
    def load() -> List[Dict[str, Any]]
    def save(data: List[Dict[str, Any]]) -> bool
    def clear() -> bool
    def exists() -> bool
```

**核心功能：**

1. **加载数据**
   - 文件不存在时返回空列表
   - JSON解析失败时返回空列表
   - 记录详细日志

2. **保存数据**
   - 自动创建父目录
   - 格式化输出（indent=2）
   - 使用 UTF-8 编码
   - 确保中文正常显示

**错误处理：**

```python
try:
    with open(self.file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
except (json.JSONDecodeError, IOError) as e:
    logger.error(f"加载失败: {e}")
    return []
```

### 3. service.py - 业务逻辑层

#### EntryService 类

核心业务逻辑处理器。

```python
class EntryService:
    def __init__(self, storage: JSONStorage)
    def add_entry(text: str) -> Tuple[...]
    def clear_all() -> Tuple[...]
    def save_dataframe(df_data) -> Tuple[...]
    def refresh() -> Tuple[...]
    def export_to_text() -> str
```

**核心方法详解：**

##### add_entry()

添加新条目，返回多个输出供UI更新。

```python
def add_entry(self, text: str) -> Tuple[str, List, str, str]:
    """
    Returns:
        (状态消息, dataframe数据, 统计信息, 清空的文本框)
    """
```

**处理流程：**
1. 验证输入非空
2. 添加到 EntryList
3. 保存到存储
4. 记录日志
5. 返回更新后的UI数据

##### save_dataframe()

保存用户在表格中编辑的数据。

**复杂度：**
- 需要处理 Gradio 传递的 pandas DataFrame
- 验证每行数据的有效性
- 跳过空行和无效行
- 反序列化（表格是倒序显示的）

**关键代码：**

```python
# 跳过空行
if text is None or text == '' or str(text).strip() == '':
    continue

# 处理ID（可能是浮点数字符串）
entry_id = int(float(entry_id))

# 反序回正序（表格是倒序的）
new_entries.reverse()
```

##### export_to_text()

导出为文本文件。

```python
filename = f"medicine_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
```

**格式：**
```
1. 药品名称，数量，有效期
2. ...
```

### 4. ui.py - 界面层

#### GradioUI 类

构建和管理 Gradio 界面。

```python
class GradioUI:
    def build() -> gr.Blocks
    def _bind_events(...)
    def _get_custom_css() -> str
    def launch(**kwargs)
```

**核心功能：**

##### 1. 界面构建

```python
with gr.Blocks(title=..., theme=..., head=..., css=...) as app:
    # 组件定义
    dataframe = gr.Dataframe(...)
    buttons = gr.Button(...)

    # 事件绑定
    button.click(fn=..., inputs=..., outputs=...)

    # 页面加载事件
    app.load(fn=refresh, outputs=[dataframe, count])
```

##### 2. 关键优化

**数据初始化优化：**

```python
# ❌ 错误：构建时加载数据
dataframe = gr.Dataframe(value=service.get_dataframe())

# ✅ 正确：初始化为空，由 app.load() 加载
dataframe = gr.Dataframe(value=[])
app.load(fn=service.refresh, outputs=[dataframe, count])
```

**原因：**
- 避免浏览器刷新时数据不一致
- 确保只从文件加载一次

##### 3. 事件绑定

**语音输入：**

```python
voice_btn.click(
    fn=None,  # 不需要Python后端
    outputs=[text_input],
    js="""
    async () => {
        const text = await window.startVoiceRecognition();
        return text;
    }
    """
)
```

**表格编辑：**

```python
save_table_btn.click(
    fn=service.save_dataframe,
    inputs=[dataframe],
    outputs=[status, dataframe, count]
)
```

### 5. voice.py - 语音识别

纯 JavaScript 实现，注入到 Gradio 的 `<head>` 中。

#### 核心功能

**1. 单次识别**

```javascript
window.startVoiceRecognition = async () => {
    return new Promise((resolve, reject) => {
        const recognition = new webkitSpeechRecognition();
        recognition.lang = 'zh-CN';
        recognition.onresult = (event) => {
            resolve(event.results[0][0].transcript);
        };
        recognition.start();
    });
};
```

**2. 连续识别**

```javascript
window.startContinuousVoice = () => {
    if (window.continuousMode) {
        // 停止模式
        window.continuousMode = false;
        recognition.stop();
    } else {
        // 启动模式
        window.continuousMode = true;
        recognition.start();
    }
};
```

**关键机制：**

- 使用 `onend` 事件自动重启
- 防止重复启动的标志位
- 延迟重启避免竞态条件

```javascript
recognition.onend = () => {
    if (window.continuousMode && !window.isRestarting) {
        window.isRestarting = true;
        setTimeout(() => {
            recognition.start();
            window.isRestarting = false;
        }, 300);
    }
};
```

---

## 🔄 数据流程

### 添加条目流程

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ 语音识别  │────>│  UI Layer │────>│ Service  │────>│ Storage  │
│  (JS)    │     │  ui.py   │     │ service  │     │ storage  │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
                       │                 │                 │
                       │            ┌────▼─────┐          │
                       │            │  Models  │          │
                       │            │ EntryList│          │
                       │            └──────────┘          │
                       │                 │                 │
                       │            ┌────▼─────┐     ┌────▼─────┐
                       │            │   Log    │     │   JSON   │
                       └────────────┤  记录     │     │   文件    │
                                    └──────────┘     └──────────┘
```

### 表格编辑流程

```
用户双击单元格
    │
    ▼
编辑内容
    │
    ▼
点击"保存表格修改"
    │
    ▼
service.save_dataframe()
    │
    ├─> 验证数据
    ├─> 转换格式
    ├─> 反序回正序
    ├─> 保存到文件
    └─> 返回更新后的表格
```

---

## 📘 API 文档

### EntryService API

#### add_entry(text: str)

添加新条目。

**参数：**
- `text` (str): 药品信息文本

**返回：**
```python
Tuple[str, List[List], str, str]
# (状态消息, dataframe数据, 统计信息, 清空的文本框)
```

**示例：**
```python
status, df, count, clear = service.add_entry("阿莫西林一盒")
```

#### save_dataframe(df_data)

保存表格编辑。

**参数：**
- `df_data` (List[List] | pd.DataFrame): 表格数据

**返回：**
```python
Tuple[str, List[List], str]
# (状态消息, dataframe数据, 统计信息)
```

#### refresh()

刷新数据（从文件重新加载）。

**返回：**
```python
Tuple[List[List], str]
# (dataframe数据, 统计信息)
```

#### export_to_text()

导出为文本文件。

**返回：**
- `str`: 文件路径
- `None`: 没有数据或导出失败

---

## 📝 日志系统

### 日志配置

**配置文件：** `config.py`

```python
LOG_FILE = PROJECT_ROOT / "app.log"
LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
```

### 日志级别使用

| 级别 | 用途 | 示例 |
|------|------|------|
| **INFO** | 正常操作 | 添加条目、保存数据 |
| **WARNING** | 警告操作 | 清空数据、空内容 |
| **ERROR** | 错误情况 | 保存失败、解析失败 |

### 日志示例

```
2025-11-18 20:50:07 [INFO] __main__ - 应用启动: 药品信息收集器 V3 v3.0.0
2025-11-18 20:50:07 [INFO] src.storage - 加载文件成功: ..., 3 条
2025-11-18 20:50:32 [INFO] src.service - 添加条目: 阿莫西林一盒2027年6月
2025-11-18 20:51:15 [WARNING] src.service - 清空所有数据: 3 条
2025-11-18 20:52:00 [ERROR] src.storage - 保存文件失败: Permission denied
```

### 日志最佳实践

1. **记录关键操作**
   ```python
   logger.info(f"添加条目: {text[:50]}...")  # 截断长文本
   ```

2. **记录详细错误**
   ```python
   logger.error(f"保存失败: {e}", exc_info=True)  # 包含堆栈
   ```

3. **避免敏感信息**
   ```python
   # ❌ 不要记录完整ID或私密数据
   # ✅ 只记录操作类型和数量
   ```

---

## 💻 开发指南

### 环境搭建

```bash
# 1. 克隆仓库
cd solution3

# 2. 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行测试
pytest tests/ -v

# 5. 启动应用
python app.py
```

### 开发流程

#### 1. 添加新功能

**步骤：**

1. 在 `models.py` 中定义数据模型
2. 在 `storage.py` 中实现持久化
3. 在 `service.py` 中添加业务逻辑
4. 在 `ui.py` 中添加UI组件
5. 编写单元测试
6. 更新文档

**示例：添加"搜索"功能**

```python
# 1. models.py
class EntryList:
    def search(self, keyword: str) -> List[Entry]:
        return [e for e in self.entries if keyword in e.text]

# 2. service.py
def search_entries(self, keyword: str) -> Tuple[List, str]:
    results = self.entry_list.search(keyword)
    df = [e.to_dataframe_row(i+1) for i, e in enumerate(results)]
    status = f"找到 {len(results)} 条结果"
    return df, status

# 3. ui.py
search_input = gr.Textbox(label="搜索")
search_btn = gr.Button("🔍 搜索")
search_btn.click(
    fn=service.search_entries,
    inputs=[search_input],
    outputs=[dataframe, status]
)

# 4. tests/test_service.py
def test_search_entries():
    service.add_entry("阿莫西林")
    df, status = service.search_entries("阿莫西林")
    assert len(df) == 1
```

#### 2. 修改现有功能

**原则：**
- 向后兼容（不破坏现有数据格式）
- 添加测试覆盖新逻辑
- 更新文档

### 代码风格

遵循 PEP 8 和项目约定。

#### 命名规范

```python
# 类名：大驼峰
class EntryService:

# 函数/变量：小写下划线
def add_entry(text: str):
    entry_id = generate_id()

# 常量：全大写
MAX_TEXT_LENGTH = 500
```

#### 类型提示

```python
# ✅ 始终使用类型提示
def add_entry(self, text: str) -> Tuple[str, List[List[Any]], str, str]:
    pass

# ❌ 避免
def add_entry(self, text):
    pass
```

#### 文档字符串

```python
def add_entry(self, text: str) -> Tuple[...]:
    """
    添加新条目

    Args:
        text: 药品信息文本

    Returns:
        (状态消息, dataframe数据, 统计信息, 清空的文本框)

    Raises:
        ValueError: 如果文本为空
    """
```

---

## 🧪 测试指南

### 测试结构

```
tests/
├── test_models.py      # 20个测试
├── test_storage.py     # 8个测试
└── test_service.py     # 27个测试
```

### 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定文件
pytest tests/test_models.py -v

# 运行特定测试
pytest tests/test_models.py::test_entry_creation -v

# 查看覆盖率
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html

# 只看未覆盖的行
pytest tests/ --cov=src --cov-report=term-missing
```

### 编写测试

#### 单元测试示例

```python
import pytest
from src.models import Entry, EntryList

def test_entry_creation():
    """测试 Entry 创建"""
    entry = Entry(id=123, text="测试", timestamp="2025-01-01 00:00:00")
    assert entry.id == 123
    assert entry.text == "测试"

def test_entrylist_add():
    """测试添加条目"""
    elist = EntryList()
    entry = elist.add("药品A")

    assert len(elist) == 1
    assert entry.text == "药品A"
    assert entry.id > 0  # 自动生成ID
```

#### 测试夹具 (Fixtures)

```python
@pytest.fixture
def temp_storage(tmp_path):
    """创建临时存储"""
    file_path = tmp_path / "test.json"
    return JSONStorage(file_path)

def test_save_and_load(temp_storage):
    """测试保存和加载"""
    data = [{"id": 1, "text": "测试", "timestamp": "..."}]
    temp_storage.save(data)

    loaded = temp_storage.load()
    assert loaded == data
```

### 测试覆盖率目标

- **总体覆盖率**: > 70%
- **核心模块**:
  - models.py: 100%
  - storage.py: > 90%
  - service.py: > 80%
  - ui.py: 不强制（UI难以测试）

---

## ⚡ 性能优化

### 当前性能

- ✅ 数据量 < 1000条：秒级响应
- ✅ 数据量 < 10000条：可接受
- ⚠️ 数据量 > 10000条：需要优化

### 优化建议

#### 1. 数据分页

如果数据量大，实现分页加载：

```python
def get_dataframe(self, page=1, page_size=100):
    start = (page - 1) * page_size
    end = start + page_size
    entries = self.entry_list.get_reversed()[start:end]
    return [e.to_dataframe_row(i+1) for i, e in enumerate(entries)]
```

#### 2. 缓存优化

缓存Dataframe转换结果：

```python
from functools import lru_cache

@lru_cache(maxsize=1)
def get_dataframe(self):
    # 缓存最近一次的结果
    return self.entry_list.to_dataframe()
```

#### 3. 数据库迁移

超过10000条时，迁移到 SQLite：

```python
import sqlite3

class SQLiteStorage:
    def save(self, entries):
        conn = sqlite3.connect(self.db_path)
        # 使用批量插入
        conn.executemany("INSERT INTO entries VALUES (?, ?, ?)", entries)
```

---

## 🔍 故障排查

### 常见问题

#### 1. 语音识别不工作

**症状：** 点击按钮无反应

**排查：**
```javascript
// 浏览器控制台检查
console.log(window.webkitSpeechRecognition);  // 应该有定义
```

**解决：**
- 使用 Chrome/Edge 浏览器
- 检查麦克风权限
- 查看浏览器控制台错误

#### 2. 数据保存失败

**症状：** 提示"保存失败"

**排查：**
```bash
# 检查日志
tail -50 app.log | grep ERROR

# 检查文件权限
ls -l data/voice_entries.json

# 检查磁盘空间
df -h
```

**解决：**
- 确保data目录有写权限
- 检查磁盘空间
- 查看详细错误日志

#### 3. 浏览器刷新后数据不一致

**症状：** 刷新后先显示旧数据，1秒后更新

**原因：** Dataframe 初始化时加载了数据

**解决：** 已在最新版本修复（初始化为空数组）

#### 4. 测试失败

**排查：**
```bash
# 运行详细测试
pytest tests/ -vv

# 只运行失败的测试
pytest tests/ --lf

# 查看完整错误
pytest tests/ -vv --tb=long
```

---

## 🚀 部署指南

### 本地部署

已默认支持，运行 `python app.py` 即可。

### Docker 部署

创建 `Dockerfile`：

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["python", "app.py"]
```

构建和运行：

```bash
docker build -t medicine-tracker .
docker run -p 7860:7860 -v $(pwd)/data:/app/data medicine-tracker
```

### 云端部署

#### Hugging Face Spaces

1. 创建 `requirements.txt`
2. 推送到 GitHub
3. 连接到 Hugging Face Spaces
4. 自动部署

#### Railway / Render

支持一键部署，配置端口为 7860。

---

## 🤝 贡献指南

### 提交代码

1. Fork 仓库
2. 创建功能分支：`git checkout -b feature/new-feature`
3. 编写代码和测试
4. 运行测试：`pytest tests/`
5. 提交代码：`git commit -m "Add new feature"`
6. 推送分支：`git push origin feature/new-feature`
7. 创建 Pull Request

### 代码审查

所有PR需要：
- ✅ 通过所有测试
- ✅ 代码覆盖率不降低
- ✅ 遵循代码规范
- ✅ 更新相关文档

---

## 📚 参考资料

- [Gradio 文档](https://www.gradio.app/docs/)
- [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)
- [Python Logging](https://docs.python.org/3/library/logging.html)
- [Pytest 文档](https://docs.pytest.org/)

---

## 📜 更新日志

### v3.0.0 (2025-11-18)

- ✅ 完整的日志系统
- ✅ 优化数据初始化流程
- ✅ 完善文档体系
- ✅ 55个单元测试

### v2.0.0 (2025-11-17)

- ✅ 重构为分层架构
- ✅ 添加表格编辑功能
- ✅ 连续语音模式

### v1.0.0 (2025-11-16)

- ✅ 初始版本
- ✅ 单次语音输入
- ✅ JSON存储

---

**文档版本**: 3.0.0
**最后更新**: 2025-11-18
**维护者**: Medicine Tracker Team
