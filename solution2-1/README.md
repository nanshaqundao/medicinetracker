# Medicine Tracker - Solution 2.1 (Real-time Camera OCR)

## 功能特性 / Features

### 三种输入方式 / Three Input Methods
1. **🎤 语音输入** - Web Speech API（单次/连续）
2. **📷 实时相机识别** - 直接调用相机，实时预览，拍照即识别（推荐）
3. **✍️ 文本输入** - 手动输入或粘贴

### 相机识别工作流 / Camera OCR Workflow
```
点击"📷 相机识别" 
    ↓
启动实时相机预览（可调整角度）
    ↓
点击"📸 拍照"
    ↓
Tesseract.js 自动识别文字
    ↓
预览识别结果
    ↓
确认 → 添加到列表（默认数量: 1）
```

### 数量管理 / Quantity Management
- 每条记录默认数量为 1
- 支持 +/- 按钮调整数量
- 导出时包含数量信息（如：布洛芬 x3）

### 来源标识 / Source Indicators
- 🎤 语音
- 📷 相机
- ✍️ 文本

## 快速开始 / Quick Start

### 本地运行 / Run Locally

```bash
cd solution2-1
python3 -m http.server 8080
```

访问：`http://localhost:8080/voice-collector.html`

### Docker 运行 / Run with Docker

```bash
docker build -t medicine-tracker-v2.1 .
docker run -p 8080:8080 medicine-tracker-v2.1
```

### 访问 URL / Access URLs

- **本地**：`http://localhost:8080/voice-collector.html`
- **局域网**：`http://192.168.0.135:8080/voice-collector.html`（替换为你的主机 IP）

## 使用说明 / Instructions

### 相机识别模式 / Camera OCR Mode（推荐）
1. 点击 "📷 相机识别" 按钮
2. 允许浏览器访问摄像头
3. 实时预览 + 调整角度（支持移动设备后置摄像头）
4. 拍药物盒子正面（包含药名、规格等清晰文字）
5. 点击 "📸 拍照" 按钮
6. 自动进行 OCR 识别（显示进度条）
7. 检查识别结果后点击"确认"
8. 药品自动添加到列表，数量默认为 1

### 语音输入模式 / Voice Mode
- **单次录入**：说一句后自动停止
- **连续录入**：多次说话，每次自动添加，完成后点"停止"

### 文本输入 / Text Mode
- 直接输入或粘贴文本
- 按 Enter 或点击"添加"提交

## 核心改进 / Key Improvements

| 特性 | Solution 2 | Solution 2.1 |
|------|-----------|-------------|
| 文件上传 | ✅ 需要文件选择 | ❌ 无需 |
| 实时预览 | ❌ | ✅ 边看边调 |
| 用户体验 | 一般 | ✅✅✅ 优秀 |
| 流程简洁度 | 3 步 | 2 步 |

## 数据持久化 / Data Persistence

- 所有数据保存在浏览器 LocalStorage
- 刷新页面后数据依然存在
- 不涉及后端服务

## 浏览器兼容性 / Browser Compatibility

| 功能 | Chrome | Firefox | Safari | Edge |
|------|--------|---------|--------|------|
| MediaStream API (相机) | ✅ | ✅ | ⚠️ (iOS 14.5+) | ✅ |
| Tesseract OCR | ✅ | ✅ | ✅ | ✅ |
| Web Speech API | ✅ | ⚠️ | ❌ | ✅ |
| 文本输入 | ✅ | ✅ | ✅ | ✅ |

## 注意事项 / Notes

- **HTTPS 要求**：移动 Safari (iOS) 需要 HTTPS
- **权限授予**：首次使用需授予摄像头和麦克风权限
- **OCR 准确度**：取决于拍照质量
- **性能**：Tesseract.js 第一次运行时需加载模型（~20MB）

## OCR 效果优化建议

**拍照时最佳实践：**
- ✅ 光线充足（自然光或白色 LED）
- ✅ 避免逆光
- ✅ 拍药物盒子正面（文字清晰）
- ✅ 保持相机垂直，尽量充满整个预览框
- ✅ 避免模糊和过度曝光

## 技术栈 / Tech Stack

- **前端框架**：原生 HTML/CSS/JavaScript
- **UI 库**：Tailwind CSS
- **OCR 库**：Tesseract.js v5
- **相机 API**：MediaStream API
- **语音识别**：Web Speech API
- **部署**：Docker + Python HTTP Server

## 常见问题 / FAQ

**Q: 无法启动相机**
A: 
1. 检查浏览器权限设置（地址栏左边的锁形图标）
2. 确保允许该网站访问摄像头
3. iOS Safari 需要 HTTPS 协议

**Q: 相机预览显示镜像**
A: 这是正常的（前置摄像头显示方式），拍照时会自动纠正

**Q: OCR 识别率低**
A: 请确保：
- 光线充足
- 文字清晰且垂直
- 不要有阴影或反光
- 避免手抖

**Q: 相机权限弹窗**
A: 这是浏览器安全机制，点击"允许"即可

## 版本对比

- **Solution 1**：基础语音输入
- **Solution 1-1**：语音 + 文本输入框
- **Solution 2**：语音 + 照片上传 + OCR
- **Solution 2.1**：语音 + **实时相机** + OCR（最新，推荐）
