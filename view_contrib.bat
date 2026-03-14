@echo off
"C:\Program Files\GitHub CLI\gh.exe" repo view Calix-L/Calix-L --json defaultBranchRef
echo.
"C:\Program Files\GitHub CLI\gh.exe" api repos/Calix-L/Calix-L/contributors
echo.
"C:\Program Files\GitHub CLI\gh.exe" api repos/Calix-L/Vesuvius/contributors
