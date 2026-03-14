# 🏦 Bank Statement Translator

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[English](#english) | [简体中文](#简体中文)

Translate Chinese bank statement PDFs into polished English outputs — perfect for visa applications, immigration, and international financial workflows.

---

## English

### Overview

A local-first Python toolkit that converts Chinese bank statement PDFs into clean English documents while preserving the original layout as closely as possible.

**Input** → **Output**
- Chinese ICBC bank statement PDF → English PDF (layout-preserved)
- Optional: Structured English Excel workbook

### Why This Project?

Existing OCR/translation tools are either:
- Too generic (don't understand banking terminology)
- Too expensive (cloud services)
- Lose important visual elements (stamps, QR codes, tables)

This project solves these problems with banking-specific optimization.

### Features

| Feature | Description |
|---------|-------------|
| 🏦 **Banking-Optimized** | 500+ banking & payment terms, ICBC-specific parsing |
| 🎨 **Layout Preservation** | Keeps stamps, QR codes, tables, and formatting |
| 🔍 **Smart OCR** | Baidu PaddleOCR for scanned documents |
| 📦 **Dual Output** | Both PDF and Excel formats |
| ⚡ **Caching** | 10x faster for repeated processing |
| 🐳 **Docker Ready** | One-click deployment |

### Supported Banks

- ✅ Industrial and Commercial Bank of China (ICBC)
- 🔄 More banks coming soon

### Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure API keys
cp .env.example .env
# Edit .env with your keys:
#   - ZHIPU_API_KEY (from https://open.bigmodel.cn/)
#   - OCR_TOKEN (from https://aistudio.baidu.com/)

# 3. Translate a PDF
python run_word_translator_pipeline.py "statement.pdf" -o "statement_en.pdf"
```

### Usage

```bash
# PDF translation
python run_word_translator_pipeline.py "input.pdf" -o "output.pdf"

# Streamlit UI
streamlit run app.py

# CLI
python cli.py --help

# Run tests
pytest tests -v
```

### Project Structure

```
bank_statement_translator/
├── app.py                     # Streamlit UI
├── cli.py                     # CLI entry point
├── run_word_translator_pipeline.py  # Simple PDF→PDF command
├── word_translator.py         # Main translation pipeline
├── word_layout.py            # PDF layout & rendering
├── translator.py             # Text translation logic
├── glossary.py              # Terminology builder
├── terms/                   # Banking/payment terms
│   ├── banking_terms.py
│   ├── payment_terms.py
│   └── readable_terms.py
├── pdf_parser.py            # PDF text extraction
├── statement_structurer.py   # Statement row parsing
├── excel_generator.py       # Excel export
└── tests/                   # Test suite
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ZHIPU_API_KEY` | ✅ | Zhipu GLM API key |
| `OCR_TOKEN` | ✅ | Baidu PaddleOCR token |
| `ZHIPU_MODEL` | ❌ | Model (default: glm-4-flash) |
| `TARGET_LANGUAGE` | ❌ | Target language (default: English) |

### Development

```bash
make install    # Install dependencies
make test       # Run tests
make lint       # Lint code
make format     # Format code
make run        # Run Streamlit
make translate  # Quick translate
```

### License

MIT License - see [LICENSE](LICENSE) for details.

---

## 简体中文

### 项目简介

一个本地优先的 Python 工具包，将中文银行流水 PDF 转换为清晰的英文文档，同时尽可能保留原始版式。

**输入** → **输出**
- 中文工商银行流水 PDF → 英文 PDF（保留版式）
- 可选：结构化英文 Excel

### 核心优势

| 功能 | 说明 |
|------|------|
| 🏦 **银行优化** | 500+ 银行与支付术语，专为工行流水优化 |
| 🎨 **版式保留** | 保留印章、二维码、表格等关键元素 |
| 🔍 **智能 OCR** | 百度 PaddleOCR 处理扫描件 |
| 📦 **双格式输出** | 支持 PDF 和 Excel 两种格式 |
| ⚡ **缓存加速** | 重复处理提速 10 倍 |
| 🐳 **Docker 部署** | 一键容器化部署 |

### 支持银行

- ✅ 中国工商银行 (ICBC)
- 🔄 更多银行开发中

### 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API 密钥
cp .env.example .env
# 编辑 .env 填入：
#   - ZHIPU_API_KEY (来自 https://open.bigmodel.cn/)
#   - OCR_TOKEN (来自 https://aistudio.baidu.com/)

# 3. 翻译 PDF
python run_word_translator_pipeline.py "流水.pdf" -o "流水_en.pdf"
```

### 使用方式

```bash
# PDF 翻译
python run_word_translator_pipeline.py "input.pdf" -o "output.pdf"

# Streamlit 界面
streamlit run app.py

# 命令行
python cli.py --help

# 运行测试
pytest tests -v
```

### 项目结构

```
bank_statement_translator/
├── app.py                     # Streamlit 界面
├── cli.py                     # 命令行入口
├── run_word_translator_pipeline.py  # 简单 PDF→PDF 命令
├── word_translator.py         # 主翻译流程
├── word_layout.py            # PDF 布局与渲染
├── translator.py             # 文本翻译逻辑
├── glossary.py              # 术语表构建
├── terms/                   # 银行与支付术语
│   ├── banking_terms.py
│   ├── payment_terms.py
│   └── readable_terms.py
├── pdf_parser.py            # PDF 文本提取
├── statement_structurer.py   # 流水行解析
├── excel_generator.py       # Excel 导出
└── tests/                   # 测试套件
```

### 环境变量

| 变量 | 必需 | 说明 |
|------|------|------|
| `ZHIPU_API_KEY` | ✅ | 智谱 GLM API 密钥 |
| `OCR_TOKEN` | ✅ | 百度 PaddleOCR 令牌 |
| `ZHIPU_MODEL` | ❌ | 翻译模型（默认：glm-4-flash） |
| `TARGET_LANGUAGE` | ❌ | 目标语言（默认：English） |

### 开发命令

```bash
make install    # 安装依赖
make test       # 运行测试
make lint       # 代码检查
make format     # 代码格式化
make run        # 启动 Streamlit
make translate  # 快速翻译
```

### 许可证

MIT 许可证 - 详见 [LICENSE](LICENSE)
