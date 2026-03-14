@echo off
set HTTP_PROXY=http://127.0.0.1:8800
set HTTPS_PROXY=http://127.0.0.1:8800
cd "C:\Users\38832\.openclaw\workspace\Vesuvius\Vesuvius-main"
git init
git config user.email "1553181496@qq.com"
git config user.name "Calix"
git add .
git commit -m "Vesuvius Competition - Kaggle Silver Medal Solution"
git branch -M main
git remote add origin https://github.com/Calix-L/Vesuvius.git
git push -u origin main
