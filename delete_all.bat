@echo off
set HTTP_PROXY=http://127.0.0.1:8800
set HTTPS_PROXY=http://127.0.0.1:8800
"C:\Program Files\GitHub CLI\gh.exe" repo delete Calix-L/Calix-L --yes
"C:\Program Files\GitHub CLI\gh.exe" repo delete Calix-L/Vesuvius --yes
