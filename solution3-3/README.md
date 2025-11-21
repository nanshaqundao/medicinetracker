# 药品信息收集器 V3

> 🎤 基于语音输入的智能药品信息管理系统

一款专为老年人设计的药品信息收集工具，通过语音输入轻松记录药品名称、数量和有效期，支持实时编辑和数据导出。

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Gradio](https://img.shields.io/badge/Gradio-5.0+-orange.svg)](https://gradio.app/)
[![Tests](https://img.shields.io/badge/tests-55%20passed-brightgreen.svg)](./tests/)
[![Coverage](https://img.shields.io/badge/coverage-71%25-yellowgreen.svg)](./tests/)

---

## ✨ 核心功能

- 🎤 **智能语音输入** - 支持单次和连续语音识别，解放双手
- ✏️ **实时表格编辑** - 双击单元格直接修改，所见即所得
- 💾 **自动数据保存** - 每次操作自动持久化，数据永不丢失
- 📥 **一键导出** - 导出为文本文件，方便打印或分享
- 📝 **完整日志记录** - 所有操作可追溯，便于问题排查
- 🧪 **高测试覆盖** - 55个单元测试，71%代码覆盖率

---

## 🚀 快速开始

### 系统要求

- Python 3.10 或更高版本
- Chrome 或 Edge 浏览器（支持 Web Speech API）
- 麦克风设备

### 三步启动

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动应用
python app.py

# 3. 打开浏览器访问
# http://localhost:7860
```

就是这么简单！🎉

### 🐳 Docker 启动

如果您更喜欢使用 Docker：

```bash
# 1. 构建镜像
docker build -t medicinetracker .

# 2. 运行容器（传递 Windows 环境变量）
# PowerShell:
docker run -p 7860:7860 -v ${PWD}/data:/app/data -e CLAUDE_API_KEY=$env:CLAUDE_API_KEY medicinetracker

# CMD:
# docker run -p 7860:7860 -v %cd%/data:/app/data -e CLAUDE_API_KEY=%CLAUDE_API_KEY% medicinetracker
```

---

## 📖 使用指南

### 🎤 语音输入

#### 连续模式（推荐）

最高效的使用方式，说完自动添加：

1. 点击 **"🔴 连续语音输入"** 按钮
2. 允许浏览器麦克风权限（首次使用）
3. 开始说话，例如：
   ```
   "阿莫西林，一盒，2027年6月"
   "布洛芬，30片，2026年12月31日"
   ```
4. 识别结果自动添加到列表
5. 继续说下一条，无需重复点击
6. 完成后再次点击按钮停止

#### 单次模式

适合偶尔添加单条记录：

1. 点击 **"🎤 单次语音输入"** 按钮
2. 说出药品信息
3. 识别完成后点击 **"➕ 添加到列表"**

### ✏️ 编辑数据

#### 修改内容

1. 双击表格中的任意单元格
2. 直接输入新内容
3. 点击 **"💾 保存表格修改"** 确认

#### 删除记录

1. 选中要删除的行
2. 按键盘 `Delete` 键，或清空该行内容
3. 点击 **"💾 保存表格修改"** 确认

### 📥 导出数据

点击 **"📥 导出文本"** 按钮，将生成如下格式的文本文件：

```
1. 阿莫西林，一盒，2027年6月
2. 布洛芬，30片，2026年12月31日
3. 感冒灵，10袋，2025年8月10日
```

文件名格式：`medicine_list_20251118_205045.txt`

---

## 🗂️ 项目结构

```
solution3/
├── app.py              # 应用入口
├── config.py           # 配置文件
├── requirements.txt    # 依赖列表
│
├── src/                # 源代码
│   ├── models.py       # 数据模型
│   ├── storage.py      # 存储层
│   ├── service.py      # 业务逻辑
│   ├── ui.py          # 界面组件
│   └── voice.py       # 语音识别
│
├── tests/             # 测试代码
│   ├── test_models.py
│   ├── test_service.py
│   └── test_storage.py
│
├── data/              # 数据目录
│   └── voice_entries.json
│
└── app.log            # 应用日志
```

---

## 🔧 配置说明

编辑 `config.py` 自定义配置：

```python
SERVER_PORT = 7860          # 服务器端口
LOG_LEVEL = logging.INFO    # 日志级别
DATA_FILE = "data/voice_entries.json"  # 数据文件路径
```

---

## 📊 数据格式

数据保存在 `data/voice_entries.json`：

```json
[
  {
    "id": 1763487651827,
    "text": "阿莫西林一盒2027年6月",
    "timestamp": "2025-11-18 17:40:51"
  }
]
```

- `id`: 唯一标识（毫秒时间戳）
- `text`: 药品信息
- `timestamp`: 录入时间

---

## 🧪 运行测试

```bash
# 运行所有测试
pytest tests/

# 查看测试覆盖率
pytest tests/ --cov=src --cov-report=html

# 在浏览器查看覆盖率报告
open htmlcov/index.html
```

**测试统计：**
- ✅ 55个测试用例
- ✅ 100%通过率
- ✅ 71%代码覆盖率

---

## 📝 日志管理

应用会自动记录所有操作到 `app.log`：

```bash
# 查看完整日志
cat app.log

# 实时监控日志
tail -f app.log

# 查看最近50行
tail -50 app.log
```

日志包含：启动信息、数据操作、错误追踪等。

---

## ❓ 常见问题

### 语音识别不工作？

1. 确认使用 Chrome 或 Edge 浏览器
2. 检查麦克风权限是否已授予
3. Firefox 不支持 Web Speech API

### 数据丢失了？

- 所有操作自动保存到 `data/voice_entries.json`
- 检查该文件是否存在
- 查看 `app.log` 了解详情

### 如何备份数据？

```bash
# 备份数据文件
cp data/voice_entries.json data/backup_$(date +%Y%m%d).json

# 或导出为文本
# 点击界面上的"📥 导出文本"按钮
```

---

## 🤝 贡献指南

欢迎提交问题和改进建议！

详细的开发文档请参阅 [DEVELOPMENT.md](./DEVELOPMENT.md)

---

## 📄 许可证

本项目仅供学习和个人使用。

---

## 🔗 相关链接

- **开发文档**: [DEVELOPMENT.md](./DEVELOPMENT.md)
- **测试报告**: [htmlcov/index.html](./htmlcov/index.html)
- **Gradio 官网**: https://gradio.app/
- **Web Speech API**: https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API

---

**版本**: 3.0.0
**创建**: 2025-11-17
**更新**: 2025-11-18
**作者**: Medicine Tracker Team
