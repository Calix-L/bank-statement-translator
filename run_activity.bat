@echo off
cd /d "C:\Users\38832\.openclaw\workspace\github-activity\github-activity-generator-main"
set HTTP_PROXY=http://127.0.0.1:8800
set HTTPS_PROXY=http://127.0.0.1:8800
py contribute.py --repository=https://github.com/Calix-L/github-activity.git --max_commits=5 --frequency=50
