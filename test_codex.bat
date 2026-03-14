@echo off
set HTTP_PROXY=http://127.0.0.1:8800
set HTTPS_PROXY=http://127.0.0.1:8800
mcporter call codex.codex prompt="Say hello" model="gpt-5.1" --timeout 120
