@echo off
set HTTP_PROXY=http://127.0.0.1:8800
set HTTPS_PROXY=http://127.0.0.1:8800
cd "C:\Users\38832\.openclaw\workspace\github-profile"
git init
git config user.email "1553181496@qq.com"
git config user.name "Calix"
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/Calix-L/Calix-L.git
git push -u origin main
