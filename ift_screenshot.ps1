Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$proc = Get-Process -Id 47728
if ($proc -eq $null) {
    Write-Host "Process not found"
    exit
}

# 获取窗口位置和大小
$rect = [System.Drawing.Rectangle]::FromLTRB(
    [int]([System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Left),
    [int]([System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Top),
    [int]([System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Right),
    [int]([System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Bottom)
)

# 截取整个主屏幕
$bmp = New-Object System.Drawing.Bitmap($rect.Width, $rect.Height)
$graphics = [System.Drawing.Graphics]::FromImage($bmp)
$graphics.CopyFromScreen($rect.Location, [System.Drawing.Point]::Empty, $rect.Size)
$bmp.Save("C:\Users\38832\.openclaw\workspace\ift_screen.png")
$graphics.Dispose()
$bmp.Dispose()

Write-Host "Screenshot saved"
