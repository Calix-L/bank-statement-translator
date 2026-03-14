# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## Calix API Keys

### 百度 PaddleOCR
- **Token:** `42620046a093e39d5fae83a2ce353628b2e9a41b`
- **来源:** https://aistudio.baidu.com/

### 智谱 Zhipu
- **API Key:** `fc9088493723472cb447bd1ee17d30ae.1O1zO8D0K1VmRWJH`
- **模型:** glm-4-flash
- **来源:** https://open.bigmodel.cn/

## QuickQ 代理端口

| 类型 | 端口 | 用途 |
|------|------|------|
| HTTP | `127.0.0.1:8800` | Codex、gog 发邮件 |
| SOCKS5 | `127.0.0.1:10020` | gog 搜索/授权 |
| Switch | `127.0.0.1:12500` | Switch 代理 |

### 不同程序的代理格式

| 程序 | 代理格式 |
|------|----------|
| **gog 搜索/授权** | `socks5://127.0.0.1:10020` |
| **gog 发邮件** | `http://127.0.0.1:8800` |
| **Codex CLI** | `http://127.0.0.1:8800` |

### 设置代理命令

```powershell
# SOCKS5 (gog 搜索)
$env:HTTP_PROXY = "socks5://127.0.0.1:10020"
$env:HTTPS_PROXY = "socks5://127.0.0.1:10020"

# HTTP (Codex、gog 发邮件)
$env:HTTP_PROXY = "http://127.0.0.1:8800"
$env:HTTPS_PROXY = "http://127.0.0.1:8800"
```

## NAS 配置

- **IP:** 192.168.5.33
- **型号:** 绿联 DXP4800
- **账号:** 18154300717
- **密码:** Lzx315323
- **Z 盘:** `\\192.168.5.33\personal_folder` (永久连接)

### Z 盘目录结构

```
Z:\ (\\192.168.5.33\personal_folder)
├── Photos/
├── 资料/
├── 媒体文件/
├── 百度网盘/
├── Music/
├── .bt/
└── #recycle/
```

⚠️ **绝对不要修改 Z 盘里的内容！**

### 映射命令

```powershell
# 如果需要重新映射
net use Z: /delete
net use \\192.168.5.33\ipc$ /user:18154300717 Lzx315323
net use Z: \\192.168.5.33\personal_folder /persistent:yes
```

## PaddleOCR API

- **API Key:** 42620046a093e39d5fae83a2ce353628b2e9a41b
- **文档:** https://aistudio.baidu.com/paddleocr

### 使用方法

```python
from paddleocr import PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='ch')
result = ocr.ocr('image.jpg', cls=True)
```

## GitHub 配置

### Git 提交用户配置（重要！）
以后所有 GitHub 上传必须用这个配置，确保贡献者显示正确：

```bash
git config user.email "zhenxinlin290@gmail.com"
git config user.name "Calix"
```

- **GitHub 账号:** Calix-L
- **提交邮箱:** zhenxinlin290@gmail.com (Gmail)
- **显示名称:** Calix

---

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.
