# Bank Statement Translator

[English](README.md) | [简体中文](README.zh-CN.md)

将中文银行流水 PDF 转换为清晰、可交付的英文输出。

这个项目聚焦一个非常实际的流程：

- 输入：中文银行流水 PDF
- 输出：尽量保持原始版式的英文 PDF
- 可选输出：结构化英文 Excel

项目整体保持轻量、本地优先，目标不是做通用文档翻译，而是把银行流水这类文件处理好。

## 当前支持范围

- 当前仅支持：中国工商银行（ICBC）
- 主要场景：为签证办理准备英文版银行流水
- OCR 服务：百度飞桨 PaddleOCR API
- 翻译服务：智谱 GLM API

目前项目里的解析逻辑和高密度 PDF 重建逻辑，都是按工行流水版式做的专门适配，暂不承诺支持其他银行。

## 功能特性

- 聚焦真实签证办理场景，解决“中文银行流水需要英文版提交很麻烦”的问题
- 重建高密度流水页面，同时尽量保留印章、二维码和关键页面元素
- 采用分层翻译策略：精确覆盖、术语表、缓存、API 回退
- 内置适合银行流水场景的银行与支付术语
- 同时支持 PDF 输出和结构化 Excel 导出
- 提供了解析、翻译和 Excel 生成相关测试

## 快速开始

1. 创建并激活 Python 环境。
2. 安装依赖。
3. 将 `.env.example` 复制为 `.env`。
4. 填入 API 凭证。

```bash
pip install -r requirements.txt
```

`.env` 中至少需要配置：

- `ZHIPU_API_KEY`
- `OCR_TOKEN`

这两个配置当前分别对应：

- `OCR_TOKEN`：百度飞桨 PaddleOCR 的访问令牌
- `ZHIPU_API_KEY`：智谱 GLM 翻译接口密钥

直接翻译 PDF：

```bash
python run_word_translator_pipeline.py "input.pdf" -o "output_translated.pdf"
```

如果不传 `-o`，输出文件默认命名为 `<input>_translated.pdf`。

## 使用方式

运行 PDF 翻译主流程：

```bash
python run_word_translator_pipeline.py "statement.pdf"
```

运行 Streamlit 界面：

```bash
streamlit run app.py
```

运行 CLI：

```bash
python cli.py --help
```

运行测试：

```bash
pytest tests -v
```

典型签证材料处理流程：

1. 从工行导出原始中文流水 PDF
2. 在 `.env` 中配置百度飞桨 OCR 和智谱翻译密钥
3. 执行 `python run_word_translator_pipeline.py "statement.pdf"`
4. 检查生成的英文 PDF 后再用于提交

## 项目结构

```text
app.py                          Streamlit 界面
cli.py                          命令行入口
run_word_translator_pipeline.py 最简单的 PDF 转 PDF 命令
word_translator.py              翻译流程编排
word_layout.py                  PDF 布局与渲染辅助
translator.py                   文本与 DataFrame 翻译逻辑
glossary.py                     主术语表构建入口
terms/                          银行与支付术语词典
pdf_parser.py                   PDF 文本提取
statement_structurer.py         流水行解析
excel_generator.py              Excel 导出
tests/                          测试集
```

## 设计说明

- `word_translator.py` 负责主流程。
- `word_layout.py` 负责页面排版与表格绘制。
- `translator.py` 负责术语命中、文本翻译和 API 回退。
- `terms/` 将可读词表与历史兼容映射分开，方便维护。

之所以仍然保留部分乱码兼容映射，是因为某些 PDF 在提取文本时本身就会产生相同的乱码。把它们隔离在兼容层里，可以让主词表保持可读。

## 开发

常用本地命令：

```bash
make install
make test
make lint
make format
make check
make run
make translate
```

仓库目前刻意保持精简。旧的 Docker 文件和多余示例脚本已经移除，目标是让代码更容易阅读、测试和维护。

## 贡献

欢迎贡献。开发流程和约定请参考 [CONTRIBUTING.md](CONTRIBUTING.md)。
