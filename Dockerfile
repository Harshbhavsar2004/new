 # Use a Windows Server Core image
 FROM mcr.microsoft.com/windows/servercore:ltsc2019

 # Install Windows Defender
 RUN powershell -Command "Install-WindowsFeature -Name Windows-Defender-Features"

 # Copy your scanning script
 COPY scan_script.ps1 C:\scan_script.ps1

 # Set the entry point to run the scan
 ENTRYPOINT ["powershell", "C:\\scan_script.ps1"]