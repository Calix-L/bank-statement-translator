# 🏦 银行流水翻译工具

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[English](../README.md) | [简体中文](#简体中文)

将中文银行流水 PDF 转换为清晰的英文文档，轻松应对签证申请、移民审批、国际金融流程。

---

## 项目简介

一个本地优先的 Python 工具包，将中文银行流水 PDF 转换为清晰的英文文档，同时尽可能保留原始版式。

### 输入 → 输出

- 📄 中文工商银行流水 PDF → 📄 英文 PDF（保留原始版式）
- 📊 可选：结构化英文 Excel 表格

### 核心优势

| 功能 | 说明 |
|------|------|
| 🏦 **银行优化** | 500+ 银行与支付术语，专为工行流水优化 |
| 🎨 **版式保留** | 保留印章、二维码、表格等关键页面元素 |
| 🔍 **智能 OCR** | 百度 PaddleOCR 处理扫描件和影像件 |
| 📦 **双格式输出** | 支持 PDF 和 Excel 两种格式 |
| ⚡ **缓存加速** | 重复处理提速高达 10 倍 |
| 🐳 **Docker 部署** | 支持一键容器化部署 |

### 支持银行

- ✅ 中国工商银行 (ICBC)
- 🔄 更多银行适配中

---

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API 密钥

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入以下密钥：

| 变量 | 获取地址 |
|------|----------|
| `ZHIPU_API_KEY` | [智谱开放平台](https://open.bigmodel.cn/) |
| `OCR_TOKEN` | [百度 AI Studio](https://aistudio.baidu.com/) |

### 3. 开始翻译

```bash
# 基本用法
python run_word_translator_pipeline.py "流水.pdf" -o "流水_en.pdf"

# 如果不指定输出文件，默认命名为 <原文件>_translated.pdf
python run_word_translator_pipeline.py "流水.pdf"
```

---

## 使用方式

### 命令行翻译

```bash
# PDF 翻译
python run_word_translator_pipeline.py "input.pdf" -o "output.pdf"

# 指定语言
python run_word_translator_pipeline.py "input.pdf" -o "output.pdf" --target-lang English
```

### Streamlit 图形界面

```bash
streamlit run app.py
```

### CLI 命令行工具

```bash
# 查看帮助
python cli.py --help

# 批量翻译
python cli.py batch "folder/*.pdf"
```

### 运行测试

```bash
pytest tests -v
```

---

## 项目结构

```
bank_statement_translator/
├── app.py                          # Streamlit 图形界面
├── cli.py                          # 命令行入口
├── run_word_translator_pipeline.py  # 简单易用的 PDF→PDF 命令
├── word_translator.py              # 主翻译流程编排
├── word_layout.py                  # PDF 布局与渲染辅助
├── translator.py                   # 文本翻译核心逻辑
├── glossary.py                     # 术语表构建器
├── terms/                          # 银行与支付术语词典
│   ├── banking_terms.py           # 银行相关术语
│   ├── payment_terms.py           # 支付平台术语
│   ├── readable_terms.py          # 可读性优化术语
│   └── garbled_terms.py           # 乱码兼容映射
├── pdf_parser.py                   # PDF 文本提取
├── statement_structurer.py         # 流水行解析
├── excel_generator.py              # Excel 导出
├── cache.py                        # 翻译缓存
├── rate_limiter.py                 # API 速率限制
├── config.py                       # 配置管理
└── tests/                          # 测试套件
```

---

## 环境变量

| 变量 | 必需 | 默认值 | 说明 |
|------|------|--------|------|
| `ZHIPU_API_KEY` | ✅ | - | 智谱 GLM API 密钥 |
| `OCR_TOKEN` | ✅ | - | 百度 PaddleOCR 令牌 |
| `ZHIPU_MODEL` | ❌ | glm-4-flash | 智谱翻译模型 |
| `TARGET_LANGUAGE` | ❌ | English | 目标语言 |
| `ENABLE_CACHE` | ❌ | true | 是否启用缓存 |
| `LOG_LEVEL` | ❌ | INFO | 日志级别 |

---

## 典型工作流程

1. **导出流水**：从工行手机 APP 或网银导出中文流水 PDF
2. **配置环境**：在 `.env` 中填入 API 密钥
3. **执行翻译**：`python run_word_translator_pipeline.py "流水.pdf"`
4. **检查结果**：查看生成的英文 PDF
5. **提交使用**：用于签证、移民等申请

---

## 开发命令

```bash
make install    # 安装依赖
make test       # 运行测试
make lint       # 代码检查
make format     # 代码格式化
make check      # 完整检查
make run        # 启动 Streamlit
make translate  # 快速翻译测试
```

---

## 许可证

MIT 许可证 - 详见 [LICENSE](LICENSE)

---

## 贡献

欢迎提交 Issue 和 Pull Request！

开发流程和项目约定请参考 [CONTRIBUTING.md](CONTRIBUTING.md)
