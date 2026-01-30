# 药品拍照识别系统 (Drug Identification System)

基于 OCR 和知识图谱的端到端药品识别与信息补全系统。

## 功能特性

- 📷 **图片上传/拍照**：支持网页上传药盒图片或调用摄像头实时拍照
- 🔍 **OCR 文字提取**：自动识别药盒上的文字信息（药品名、批准文号、生产企业等）
- 🎯 **智能匹配**：基于提取的文字信息匹配药品数据库
- 📋 **信息补全**：从知识图谱补全缺失信息（适应症、用法用量、禁忌等）
- 📊 **结构化输出**：返回完整的药品信息卡片

## 系统架构

```
用户上传图片
    ↓
图片预处理（裁剪、增强、去噪）
    ↓
OCR 文字提取（PaddleOCR / Tesseract）
    ↓
文字解析（提取批准文号、药品名、企业名等）
    ↓
药品匹配（精确匹配 → 模糊匹配 → 候选推荐）
    ↓
信息补全（从 Neo4j 知识图谱获取完整信息）
    ↓
返回结构化药品信息
```

## 目录结构

```
Drug_Identification/
├── api/                    # API 接口
│   ├── __init__.py
│   └── routes.py           # Flask 路由
├── core/                   # 核心模块
│   ├── __init__.py
│   ├── image_processor.py  # 图片预处理
│   ├── ocr_extractor.py    # OCR 文字提取
│   ├── text_parser.py      # 文字解析
│   └── drug_matcher.py     # 药品匹配
├── models/                 # 数据模型
│   ├── __init__.py
│   └── schemas.py          # 请求/响应模型
├── static/                 # 静态文件
│   └── uploads/            # 上传的图片
├── templates/              # 前端模板
│   └── index.html          # 主页面
├── tests/                  # 测试
│   └── test_images/        # 测试图片
├── config.py               # 配置文件
├── app.py                  # 应用入口
└── requirements.txt        # 依赖
```

## 快速开始

### 1. 安装依赖

```bash
cd Drug_Identification
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python app.py
```

### 3. 访问页面

打开浏览器访问 http://localhost:5001

## API 接口

### POST /api/identify

识别药品图片

**请求**：
- Content-Type: multipart/form-data
- image: 药盒图片文件

**响应**：
```json
{
  "success": true,
  "ocr_text": "提取的原始文字",
  "parsed_info": {
    "approval_no": "国药准字H20000001",
    "drug_name": "阿莫西林胶囊",
    "enterprise": "某某制药有限公司"
  },
  "matched_drug": {
    "approval_no": "...",
    "generic_name": "阿莫西林胶囊",
    "dosage_form": "胶囊剂",
    "indications": "...",
    "usage": "...",
    ...
  },
  "match_type": "approval_no | name_enterprise | fuzzy",
  "confidence": 0.95
}
```

## 技术栈

- **后端**：Python + Flask
- **OCR**：PaddleOCR（推荐）/ Tesseract
- **图像处理**：OpenCV + Pillow
- **数据库**：Neo4j（知识图谱）
- **前端**：HTML + CSS + JavaScript

## 依赖说明

- `paddleocr`：百度飞桨 OCR，中文识别效果好
- `opencv-python`：图像处理
- `Pillow`：图像读写
- `flask`：Web 框架
- `py2neo`：Neo4j 连接
