@echo off
set HTTP_PROXY=http://127.0.0.1:8800
set HTTPS_PROXY=http://127.0.0.1:8800

cd "C:\Users\38832\.openclaw\workspace\Vesuvius\Vesuvius-main"
git add .
git commit -m "Add Kaggle Silver Medal certificate"
git push -f origin main
