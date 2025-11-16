# Medicine Tracker - Solution 2 (Voice + Photo OCR)

## 功能特性 / Features

### 三种输入方式 / Three Input Methods
1. **🎤 语音输入** - Web Speech API（单次/连续）
2. **📷 拍照识别** - 用 Tesseract.js OCR 识别药物盒子文字（新增）
3. **✍️ 文本输入** - 手动输入或粘贴

### 拍照识别工作流 / Photo OCR Workflow
```
用户拍药物盒子 → Tesseract.js 识别文字 → 预览识别结果 → 确认添加
                                                          ↓
                                                     默认数量: 1
                                                     用户可修改
```

### 数量管理 / Quantity Management
- 每条记录默认数量为 1
- 支持 +/- 按钮调整数量
- 导出时包含数量信息（如：布洛芬 x3）

## 快速开始 / Quick Start

### 本地运行 / Run Locally

```bash
cd solution2
python3 -m http.server 8080
```

访问：`http://localhost:8080/voice-collector.html`

### Docker 运行 / Run with Docker

```bash
docker build -t medicine-tracker-v2 .
docker run -p 8080:8080 medicine-tracker-v2
```

### 访问 URL / Access URLs

- **本地**：`http://localhost:8080/voice-collector.html`
- **局域网**：`http://192.168.0.135:8080/voice-collector.html`（替换为你的主机 IP）

## 使用说明 / Instructions

### 拍照识别模式 / Photo OCR Mode
1. 点击 "📷 拍照识别" 的文件输入框
2. 拍摄药物盒子正面（包含药名、规格等）
3. Tesseract.js 会自动识别图片中的文字
4. 检查识别结果后点击"确认"
5. 药品自动添加到列表，数量默认为 1
6. 可用 +/- 按钮调整数量

### 语音输入模式 / Voice Mode
- **单次录入**：说一句后自动停止
- **连续录入**：多次说话，每次自动添加，完成后点"停止"

### 文本输入 / Text Mode
- 直接输入或粘贴文本
- 按 Enter 或点击"添加"提交

## 数据持久化 / Data Persistence

- 所有数据保存在浏览器 LocalStorage
- 刷新页面后数据依然存在
- 不涉及后端服务

## 浏览器兼容性 / Browser Compatibility

| 功能 | Chrome | Firefox | Safari | Edge |
|------|--------|---------|--------|------|
| 语音识别 | ✅ | ⚠️ | ❌ | ✅ |
| Tesseract OCR | ✅ | ✅ | ✅ | ✅ |
| 文本输入 | ✅ | ✅ | ✅ | ✅ |

## 注意事项 / Notes

- **首次使用**：需要授予摄像头和麦克风权限
- **OCR 准确度**：取决于拍照质量，建议光线充足、文字清晰
- **性能**：Tesseract.js 第一次运行时需加载模型，可能需要几秒

## 常见问题 / FAQ

**Q: 拍照时提示"无法访问摄像头"**
A: 检查浏览器权限设置，确保允许该网站访问摄像头

**Q: OCR 识别效果差**
A: 确保：
- 药物盒子字体清晰
- 光线充足
- 拍照角度垂直
- 尽量充满整个画面

**Q: 数据会上传到服务器吗？**
A: 不会，所有数据只保存在本地浏览器

## 技术栈 / Tech Stack

- **前端框架**：原生 HTML/CSS/JavaScript
- **UI 库**：Tailwind CSS
- **OCR 库**：Tesseract.js
- **语音识别**：Web Speech API
- **部署**：Docker + Python HTTP Server
