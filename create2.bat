@echo off
set HTTP_PROXY=http://127.0.0.1:8800
set HTTPS_PROXY=http://127.0.0.1:8800
"C:\Program Files\GitHub CLI\gh.exe" repo create Calix-L/Vesuvius --public --clone=false
