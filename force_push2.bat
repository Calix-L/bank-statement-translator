@echo off
set HTTP_PROXY=http://127.0.0.1:8800
set HTTPS_PROXY=http://127.0.0.1:8800

cd "C:\Users\38832\.openclaw\workspace\Vesuvius\Vesuvius-main"
rmdir /s /q .git
git init
git config user.email "zhenxinlin290@gmail.com"
git config user.name "Calix"
git add .
git commit -m "Vesuvius Competition - Kaggle Silver Medal Solution"
git branch -M main
git remote add origin https://github.com/Calix-L/Vesuvius.git
git push -f -u origin main
