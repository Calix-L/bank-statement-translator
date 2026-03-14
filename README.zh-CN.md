# 🏦 银行流水翻译工具

[English](../README.md) | [简体中文](#简体中文)

将中文银行流水 PDF 转换为清晰的英文文档，轻松应对签证申请、国际金融流程。

---

## 项目简介

一个本地优先的 Python 工具包，将中文银行流水 PDF 转换为清晰的英文文档，同时尽可能保留原始版式。

- **输入**: 中文银行流水 PDF（当前支持工行 ICBC）
- **输出**: 英文 PDF（保留版式）或结构化 Excel

本项目专注于银行流水这一特定场景的翻译优化，而非通用文档转换。

### 当前支持范围

- **支持银行**: 中国工商银行 (ICBC)
- **主要场景**: 签证申请材料准备
- **OCR 服务**: 百度飞桨 PaddleOCR API
- **翻译服务**: 智谱 GLM API

---

## 功能特性

- 🎨 **版式保留** — 保留印章、二维码、表格等页面元素
- 🔍 **智能 OCR** — 百度 PaddleOCR 处理扫描件
- 📦 **双格式输出** — 支持 PDF 和 Excel 两种格式
- 💾 **缓存加速** — 内置翻译缓存，重复处理提速
- ⚡ **速率限制** — 智能 API 速率限制，防止触发限制
- ✅ **完整测试** — 配套测试用例

---

## 快速开始

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

---

## 使用方式

```bash
# PDF 翻译
python run_word_translator_pipeline.py "input.pdf" -o "output.pdf"

# Streamlit 界面
streamlit run app.py

# 命令行工具
python cli.py --help

# 运行测试
pytest tests -v
```

---

## 项目结构

```
app.py                          Streamlit 界面
cli.py                          命令行入口
run_word_translator_pipeline.py 最简单的 PDF 转 PDF 命令
word_translator.py              翻译流程编排
word_layout.py                  PDF 布局与渲染辅助
translator.py                   文本与 DataFrame 翻译逻辑
glossary.py                     术语表构建器
terms/                          银行与支付术语词典
    banking_terms.py           # 银行术语
    payment_terms.py           # 支付平台术语
    readable_terms.py          # 可读性优化
    garbled_terms.py          # OCR 乱码映射
pdf_parser.py                   PDF 文本提取
statement_structurer.py         流水行解析
excel_generator.py              Excel 导出
config.py                       配置管理
cache.py                        翻译缓存
rate_limiter.py                 API 速率限制
tests/                          测试套件
```

---

## 环境变量

| 变量 | 必需 | 说明 |
|------|------|------|
| `ZHIPU_API_KEY` | ✅ | 智谱 GLM API 密钥 |
| `OCR_TOKEN` | ✅ | 百度 PaddleOCR 令牌 |
| `ZHIPU_MODEL` | ❌ | 翻译模型（默认：glm-4-flash） |
| `TARGET_LANGUAGE` | ❌ | 目标语言（默认：English） |
| `ENABLE_CACHE` | ❌ | 启用缓存（默认：true） |

---

## 开发命令

```bash
make install    # 安装依赖
make test       # 运行测试
make lint       # 代码检查
make format     # 代码格式化
make check      # 完整检查
make run        # 启动 Streamlit
make translate  # 快速翻译
make clean      # 清理临时文件
```

---

## 许可证

MIT 许可证 - 详见 [LICENSE](LICENSE)

---

## 贡献

欢迎提交 Issue 和 Pull Request！开发流程请参考 [CONTRIBUTING.md](CONTRIBUTING.md)
