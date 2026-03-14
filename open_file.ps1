# 激活讯飞听见窗口并发送 Ctrl+O 或者尝试用键盘打开
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
    [DllImport("user32.dll")]
    public static extern IntPtr FindWindow(string lpClassName, string lpWindowName);
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern void keybd_event(byte bVk, byte bScan, int dwFlags, int dwExtraInfo);
    
    public const int VK_RETURN = 0x0D;
}
"@

$hwnd = [Win32]::FindWindow($null, "讯飞听见")
if ($hwnd -ne [IntPtr]::Zero) {
    [Win32]::SetForegroundWindow($hwnd)
    Write-Host "Window found and activated"
    
    # 发送向下箭头键来选择文件
    [Win32]::keybd_event(0x28, 0, 0, 0)  # Down arrow
    [Win32]::keybd_event(0x28, 0, 2, 0)
    
    Start-Sleep -Milliseconds 500
    
    # 发送回车键打开
    [Win32]::keybd_event(0x0D, 0, 0, 0)
    [Win32]::keybd_event(0x0D, 0, 2, 0)
    
    Write-Host "Keys sent"
} else {
    Write-Host "Window not found"
}
