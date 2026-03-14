Add-Type -AssemblyName System.Runtime.WindowsRuntime
Add-Type -AssemblyName System.IO.FileStream

# 使用 Windows.Media.Ocr (需要 Win10+)
Add-Type @"
using System;
using System.Runtime.InteropServices;
using Windows.Graphics.Imaging;
using Windows.Media.Ocr;
using Windows.Storage;
using System.Threading.Tasks;
using System.Runtime.InteropServices.WindowsRuntime;

public class WindowsOCR {
    public static async Task<string> RecognizeText(string imagePath) {
        var file = await StorageFile.GetFileFromPathAsync(imagePath);
        using var stream = await file.OpenAsync(Windows.Storage.FileAccessMode.Read);
        var decoder = await BitmapDecoder.CreateAsync(stream);
        var softwareBitmap = await decoder.GetSoftwareBitmapAsync();
        
        var ocrEngine = OcrEngine.TryCreateFromUserProfileLanguages();
        var result = await ocrEngine.RecognizeAsync(softwareBitmap);
        
        return result.Text;
    }
}
"@

# 截取讯飞听见窗口
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$proc = Get-Process -Id 47728
$rect = New-Object System.Drawing.Rectangle
$rect.X = $proc.MainWindowTitle
$rect.Y = 0
$rect.Width = 800
$rect.Height = 600

# 简单截图
$bmp = New-Object System.Drawing.Bitmap(800, 600)
$graphics = [System.Drawing.Graphics]::FromImage($bmp)
$graphics.CopyFromScreen(100, 100, 0, 0, (New-Object System.Drawing.Size(800, 600)))
$bmp.Save("C:\Users\38832\.openclaw\workspace\ift_recording.png")

Write-Host "Screenshot saved to ift_recording.png"
